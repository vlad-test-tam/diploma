import torch


class Losses:

    @staticmethod
    def ls_loss_d(pos: torch.Tensor, neg: torch.Tensor,
                  value: float = 1.0) -> torch.Tensor:
        l2_pos = torch.mean((pos - value) ** 2)
        l2_neg = torch.mean(neg ** 2)
        d_loss = 0.5 * l2_pos + 0.5 * l2_neg
        return d_loss

    @staticmethod
    def ls_loss_g(neg: torch.Tensor, value: float = 1.0) -> torch.Tensor:
        g_loss = torch.mean((neg - value) ** 2)
        return g_loss

    @staticmethod
    def hinge_loss_d(pos: torch.Tensor, neg: torch.Tensor) -> torch.Tensor:
        hinge_pos = torch.mean(torch.relu(1 - pos))
        hinge_neg = torch.mean(torch.relu(1 + neg))
        d_loss = 0.5 * hinge_pos + 0.5 * hinge_neg
        return d_loss

    @staticmethod
    def hinge_loss_g(neg: torch.Tensor) -> torch.Tensor:
        g_loss = -torch.mean(neg)
        return g_loss
