from datetime import datetime

from src.repositories.user_repository import UserRepository
from src.utils.database import session

user_repository = UserRepository(session)


class AccountService:
    def __init__(self, user_repo: UserRepository = user_repository):
        self.user_repo = user_repo

    def calculate_subscription_time_left(self, user):
        """Вычисляет оставшееся время подписки и возвращает строку с результатом"""
        if not user.subscriptions_end_datetime:
            return False, None

        now = datetime.now()
        end_time = user.subscriptions_end_datetime

        if end_time < now:
            return False, None

        delta = end_time - now

        # Вычисляем дни, часы и минуты
        days = delta.days
        seconds = delta.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60

        return True, {"days": days, "hours": hours, "minutes": minutes}

    def update_subscription(self, user_id: int, months: int):
        """Обновляет подписку пользователя"""
        return self.user_repo.update_subscription(user_id, 30*months)

