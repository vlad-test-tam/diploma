import os
import time
import argparse
import torch
import torchvision as tv
import torchvision.transforms as T


from src.ml_pipeline.model_gan.train.networks.discriminator import Discriminator
from src.ml_pipeline.model_gan.train.networks.generator import Generator
from src.ml_pipeline.model_gan.train.data import ImageDataset
from src.ml_pipeline.model_gan.train.losses_metrics.losses import Losses
from src.ml_pipeline.model_gan.train.utils import Utils


parser = argparse.ArgumentParser()
parser.add_argument('--config', type=str, default="configs/train.yaml", help="Path to yaml config file")


class InpaintTrainer:
    @staticmethod
    def training_loop(generator,
                      discriminator,
                      g_optimizer,
                      d_optimizer,
                      gan_loss_g,
                      gan_loss_d,
                      train_dataloader,
                      last_n_iter,
                      writer,
                      config
                      ):

        device = torch.device('cuda' if torch.cuda.is_available()
                              and config.use_cuda_if_available else 'cpu')

        losses = {}

        generator.train()
        discriminator.train()

        losses_log = {'d_loss':   [],
                      'g_loss':   [],
                      'ae_loss':  [],
                      'ae_loss1': [],
                      'ae_loss2': [],
                      }

        init_n_iter = last_n_iter + 1
        train_iter = iter(train_dataloader)
        time0 = time.time()
        for n_iter in range(init_n_iter, config.max_iters):
            try:
                batch_real = next(train_iter)
            except:
                train_iter = iter(train_dataloader)
                batch_real = next(train_iter)

            batch_real = batch_real.to(device, non_blocking=True)

            bbox = Utils.random_bbox(config)
            regular_mask = Utils.bbox2mask(config, bbox).to(device)
            irregular_mask = Utils.brush_stroke_mask(config).to(device)
            mask = torch.logical_or(irregular_mask, regular_mask).to(torch.float32)

            batch_incomplete = batch_real*(1.-mask)
            ones_x = torch.ones_like(batch_incomplete)[:, 0:1].to(device)
            x = torch.cat([batch_incomplete, ones_x, ones_x*mask], axis=1)

            x1, x2 = generator(x, mask)
            batch_predicted = x2

            batch_complete = batch_predicted*mask + batch_incomplete*(1.-mask)

            batch_real_mask = torch.cat(
                (batch_real, torch.tile(mask, [config.batch_size, 1, 1, 1])), dim=1)
            batch_filled_mask = torch.cat((batch_complete.detach(), torch.tile(
                mask, [config.batch_size, 1, 1, 1])), dim=1)

            batch_real_filled = torch.cat((batch_real_mask, batch_filled_mask))

            d_real_gen = discriminator(batch_real_filled)
            d_real, d_gen = torch.split(d_real_gen, config.batch_size)

            d_loss = gan_loss_d(d_real, d_gen)
            losses['d_loss'] = d_loss

            d_optimizer.zero_grad()
            losses['d_loss'].backward()
            d_optimizer.step()

            losses['ae_loss1'] = config.l1_loss_alpha * \
                torch.mean((torch.abs(batch_real - x1)))
            losses['ae_loss2'] = config.l1_loss_alpha * \
                torch.mean((torch.abs(batch_real - x2)))
            losses['ae_loss'] = losses['ae_loss1'] + losses['ae_loss2']

            batch_gen = batch_predicted
            batch_gen = torch.cat((batch_gen, torch.tile(
                mask, [config.batch_size, 1, 1, 1])), dim=1)

            d_gen = discriminator(batch_gen)

            g_loss = gan_loss_g(d_gen)
            losses['g_loss'] = g_loss
            losses['g_loss'] = config.gan_loss_alpha * losses['g_loss']
            if config.ae_loss:
                losses['g_loss'] += losses['ae_loss']

            g_optimizer.zero_grad()
            losses['g_loss'].backward()
            g_optimizer.step()


            for k in losses_log.keys():
                losses_log[k].append(losses[k].item())

            # logging
            if n_iter % config.print_iter == 0:
                dt = time.time() - time0
                print(f"@iter: {n_iter}: {(config.print_iter/dt):.4f} it/s")
                time0 = time.time()

                for k, loss_log in losses_log.items():
                    loss_log_mean = sum(loss_log)/len(loss_log)
                    print(f"{k}: {loss_log_mean:.4f}")
                    if config.tb_logging:
                        writer.add_scalar(
                            f"losses/{k}", loss_log_mean, global_step=n_iter)
                    losses_log[k].clear()

            if config.tb_logging \
                and config.save_imgs_to_tb_iter \
                and n_iter % config.save_imgs_to_tb_iter == 0:
                viz_images = [Utils.pt_to_image(batch_complete),
                              Utils.pt_to_image(x1), Utils.pt_to_image(x2)]
                img_grids = [tv.utils.make_grid(images[:config.viz_max_out], nrow=2)
                            for images in viz_images]

                writer.add_image(
                    "Inpainted", img_grids[0], global_step=n_iter, dataformats="CHW")
                writer.add_image(
                    "Stage 1", img_grids[1], global_step=n_iter, dataformats="CHW")
                writer.add_image(
                    "Stage 2", img_grids[2], global_step=n_iter, dataformats="CHW")

            if config.save_imgs_to_disc_iter \
                and n_iter % config.save_imgs_to_disc_iter == 0:
                viz_images = [Utils.pt_to_image(batch_real),
                              Utils.pt_to_image(batch_complete)]
                img_grids = [tv.utils.make_grid(images[:config.viz_max_out], nrow=2)
                                                for images in viz_images]
                tv.utils.save_image(img_grids,
                f"{config.checkpoint_dir}/images/iter_{n_iter}.png",
                nrow=2)

            if n_iter % config.save_checkpoint_iter == 0 \
                and n_iter > init_n_iter:
                Utils.save_states("states.pth",
                            generator, discriminator,
                            g_optimizer, d_optimizer,
                            n_iter, config)
            if config.save_cp_backup_iter \
                and n_iter % config.save_cp_backup_iter == 0 \
                and n_iter > init_n_iter:
                Utils.save_states(f"states_{n_iter}.pth",
                            generator, discriminator,
                            g_optimizer, d_optimizer,
                            n_iter, config)


def main():
    args = parser.parse_args()
    config = Utils.get_config(args.config)

    if not os.path.isdir(config.checkpoint_dir):
        os.makedirs(os.path.abspath(config.checkpoint_dir))
        os.makedirs(os.path.abspath(f"{config.checkpoint_dir}/images"))
        print(f"Created checkpoint_dir folder: {config.checkpoint_dir}")

    transforms = [T.RandomHorizontalFlip(0.5)] if config.random_horizontal_flip else None

    train_dataset = ImageDataset(config.dataset_path,
                                 img_shape=config.img_shapes,
                                 random_crop=config.random_crop,
                                 scan_subdirs=config.scan_subdirs,
                                 transforms=transforms)

    train_dataloader = torch.utils.data.DataLoader(train_dataset,
                                                   batch_size=config.batch_size,
                                                   shuffle=True,
                                                   drop_last=True,
                                                   num_workers=config.num_workers,
                                                   pin_memory=True)

    device = torch.device('cuda' if torch.cuda.is_available()
                          and config.use_cuda_if_available else 'cpu')

    cnum_in = config.img_shapes[2]
    generator = Generator(cnum_in=cnum_in+2, cnum_out=cnum_in, cnum=48, return_flow=False)
    discriminator = Discriminator(cnum_in=cnum_in+1, cnum=64)

    generator = generator.to(device)
    discriminator = discriminator.to(device)

    g_optimizer = torch.optim.Adam(generator.parameters(), lr=config.g_lr, betas=(config.g_beta1, config.g_beta2))
    d_optimizer = torch.optim.Adam(discriminator.parameters(), lr=config.d_lr, betas=(config.d_beta1, config.d_beta2))

    if config.gan_loss == 'hinge':
        gan_loss_d, gan_loss_g = Losses.hinge_loss_d, Losses.hinge_loss_g
    elif config.gan_loss == 'ls':
        gan_loss_d, gan_loss_g = Losses.ls_loss_d, Losses.ls_loss_g
    else:
        raise NotImplementedError(f"Unsupported loss: {config.gan_loss}")

    last_n_iter = -1
    if config.model_restore != '':
        state_dicts = torch.load(config.model_restore)
        generator.load_state_dict(state_dicts['G'])
        if 'D' in state_dicts.keys():
            discriminator.load_state_dict(state_dicts['D'])
        if 'G_optim' in state_dicts.keys():
            g_optimizer.load_state_dict(state_dicts['G_optim'])
        if 'D_optim' in state_dicts.keys():
            d_optimizer.load_state_dict(state_dicts['D_optim'])
        if 'n_iter' in state_dicts.keys():
            last_n_iter = state_dicts['n_iter']
        print(f"Loaded models from: {config.model_restore}!")

    if config.tb_logging:
        from torch.utils.tensorboard import SummaryWriter
        writer = SummaryWriter(config.log_dir)

    InpaintTrainer.training_loop(generator, discriminator, g_optimizer, d_optimizer, gan_loss_g, gan_loss_d, train_dataloader, last_n_iter,  writer, config)


if __name__ == '__main__':
    main()
