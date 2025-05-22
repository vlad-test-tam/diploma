import torch
from PIL import Image
import torchvision.transforms as T
import torch.nn.functional as F


class Inpainter:
    def __init__(self, generator, image=None, mask=None, weights="", ):
        self.image = image
        self.mask = mask
        self.weights = weights

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.generator = generator

    def _pad_to_multiple(self, tensor, multiple=8):
        _, h, w = tensor.shape
        pad_h = (multiple - h % multiple) % multiple
        pad_w = (multiple - w % multiple) % multiple
        padding = (0, pad_w, 0, pad_h)  # (left, right, top, bottom)
        return F.pad(tensor, padding), (h, w)

    def prepare_inputs(self):
        if isinstance(self.image, str):
            self.image = Image.open(self.image).convert("RGB")
        if isinstance(self.mask, str):
            self.mask = Image.open(self.mask).convert("L")

        image_tensor = T.ToTensor()(self.image)[:3]
        mask_tensor = T.ToTensor()(self.mask)[0:1]

        image_tensor, self.orig_size = self._pad_to_multiple(image_tensor)
        mask_tensor, _ = self._pad_to_multiple(mask_tensor)

        image_tensor = image_tensor.unsqueeze(0).to(self.device)
        mask_tensor = (mask_tensor > 0.5).float().unsqueeze(0).to(self.device)

        image_tensor = image_tensor * 2 - 1.
        return image_tensor, mask_tensor

    def inpaint(self):
        image_tensor, mask_tensor = self.prepare_inputs()

        image_masked = image_tensor * (1. - mask_tensor)
        ones_x = torch.ones_like(image_masked)[:, 0:1, :, :]
        x = torch.cat([image_masked, ones_x, ones_x * mask_tensor], dim=1)

        with torch.inference_mode():
            _, x_stage2 = self.generator(x, mask_tensor)

        image_inpainted = image_tensor * (1. - mask_tensor) + x_stage2 * mask_tensor

        # Crop back to original size
        h_orig, w_orig = self.orig_size
        image_inpainted = image_inpainted[:, :, :h_orig, :w_orig]

        img_out = ((image_inpainted[0].permute(1, 2, 0) + 1) * 127.5).clamp(0, 255)
        img_out = img_out.to('cpu', dtype=torch.uint8).numpy()
        return Image.fromarray(img_out)


if __name__ == '__main__':
    inpainting = Inpainter(
        image=r"D:\Projects\Python\diploma_project\saved_images\buff\defected\20250429194531_59d9e999ccf7441abe7faaf4053b54b6.jpg",
        mask=r"D:\Projects\Python\diploma_project\saved_images\buff\masked\20250429194531_59d9e999ccf7441abe7faaf4053b54b6.jpg")
    img = inpainting.inpaint()
    img.save("IMAGE.jpg")
