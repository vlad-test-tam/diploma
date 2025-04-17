import torch
from PIL import Image
import torchvision.transforms as T

class Inpainting:
    def __init__(self, image=None, mask=None, out=r"D:\Projects\Python\diploma_project\saved_images\buff\fixed\fixed.png", checkpoint=r"D:\Projects\Python\diploma_project\src\ml_pipeline\results\states_tf_places2.pth"):
        self.image = image
        self.mask = mask
        self.out = out
        self.checkpoint = checkpoint

        # Load the generator model
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.generator = self._load_generator()

    def _load_generator(self):
        generator_state_dict = torch.load(self.checkpoint)['G']

        if 'stage1.conv1.conv.weight' in generator_state_dict.keys():
            from src.ml_pipeline.train.deepfill.networks import Generator
        else:
            from src.ml_pipeline.train.deepfill.networks_tf import Generator

        generator = Generator(cnum_in=5, cnum=48, return_flow=False).to(self.device)
        generator.load_state_dict(generator_state_dict, strict=True)
        return generator

    def prepare_inputs(self):
        # Check if the image is passed directly or as a path
        if isinstance(self.image, str):
            self.image = Image.open(self.image)
        if isinstance(self.mask, str):
            self.mask = Image.open(self.mask)

        # Convert images to tensors
        image_tensor = T.ToTensor()(self.image)
        mask_tensor = T.ToTensor()(self.mask)

        _, h, w = image_tensor.shape
        grid = 8

        image_tensor = image_tensor[:3, :h//grid*grid, :w//grid*grid].unsqueeze(0)
        mask_tensor = mask_tensor[0:1, :h//grid*grid, :w//grid*grid].unsqueeze(0)

        image_tensor = (image_tensor * 2 - 1.).to(self.device)  # map image values to [-1, 1] range
        mask_tensor = (mask_tensor > 0.5).to(dtype=torch.float32, device=self.device)  # 1.: masked 0.: unmasked

        return image_tensor, mask_tensor

    def inpaint(self):
        image_tensor, mask_tensor = self.prepare_inputs()

        image_masked = image_tensor * (1. - mask_tensor)  # mask image
        ones_x = torch.ones_like(image_masked)[:, 0:1, :, :]
        x = torch.cat([image_masked, ones_x, ones_x * mask_tensor], dim=1)  # concatenate channels

        with torch.inference_mode():
            _, x_stage2 = self.generator(x, mask_tensor)

        # Complete image
        image_inpainted = image_tensor * (1. - mask_tensor) + x_stage2 * mask_tensor

        # Save inpainted image
        img_out = ((image_inpainted[0].permute(1, 2, 0) + 1) * 127.5)
        img_out = img_out.to(device='cpu', dtype=torch.uint8)
        img_out = Image.fromarray(img_out.numpy())
        img_out.save(self.out)

        print(f"Saved output file at: {self.out}")


# Пример использования
if __name__ == '__main__':
    # Пример передачи изображения и маски напрямую
    inpainting = Inpainting(image="path_to_image.jpg", mask="path_to_mask.png", out="output_inpainting.png")
    inpainting.inpaint()

    # Или передача уже загруженных изображений (например, через PIL)
    image = Image.open("path_to_image.jpg")
    mask = Image.open("path_to_mask.png")
    inpainting_with_images = Inpainting(image=image, mask=mask, out="output_inpainting.png")
    inpainting_with_images.inpaint()
