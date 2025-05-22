import torch
import torch.nn.functional as F


class Metrics:
    @staticmethod
    def psnr_score(output: torch.Tensor, target: torch.Tensor, mask: torch.Tensor, max_val: float = 1.0) -> torch.Tensor:

        mse = F.mse_loss(output * mask, target * mask, reduction='none')
        mse = mse.view(mse.size(0), -1).mean(dim=1)  # [B]
        psnr = 20 * torch.log10(max_val / torch.sqrt(mse))
        return psnr.mean()

    @staticmethod
    def ssim_score(output: torch.Tensor, target: torch.Tensor, mask: torch.Tensor, window_size: int = 11, k1: float = 0.01, k2: float = 0.03) -> torch.Tensor:

        output_masked = output * mask
        target_masked = target * mask

        mu_x = F.avg_pool2d(output_masked, window_size, 1, 0)
        mu_y = F.avg_pool2d(target_masked, window_size, 1, 0)

        sigma_x = F.avg_pool2d(output_masked ** 2, window_size, 1, 0) - mu_x ** 2
        sigma_y = F.avg_pool2d(target_masked ** 2, window_size, 1, 0) - mu_y ** 2
        sigma_xy = F.avg_pool2d(output_masked * target_masked, window_size, 1, 0) - mu_x * mu_y

        ssim_map = ((2 * mu_x * mu_y + k1) * (2 * sigma_xy + k2)) / (
                    (mu_x ** 2 + mu_y ** 2 + k1) * (sigma_x + sigma_y + k2))
        return ssim_map.mean()
