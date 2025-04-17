from datetime import datetime, timedelta
from typing import Optional

from passlib.context import CryptContext
from sqlalchemy.orm import Session
from src.models.user import User
from src.entities.user import UserDTO, UserAddDTO

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверяет соответствие пароля хэшу"""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Генерирует хэш пароля"""
        return pwd_context.hash(password)

    def create_user(self, user_data: UserAddDTO) -> UserDTO:
        """Создает нового пользователя с проверкой уникальности"""
        if self.get_user_by_email(user_data.email):
            raise ValueError("Email already exists")

        hashed_password = self.get_password_hash(user_data.password)
        db_user = User(
            registration_datetime=datetime.now(),
            username=user_data.username,
            email=user_data.email,
            password=hashed_password,
            is_subscription_active=user_data.is_subscription_active,
            subscriptions_end_datetime=user_data.subscriptions_end_datetime,
            free_attempts_count=user_data.free_attempts_count
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return UserDTO.model_validate(db_user)

    def update_username(self, user_id: str, new_name: str) -> None:
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.username = new_name
            self.db.commit()

    def update_user_password(self, email: str, new_password_hash: str) -> None:
        """Обновляет пароль пользователя"""
        user = self.db.query(User).filter(User.email == email).first()
        if user:
            user.password = new_password_hash
            self.db.commit()

    def verify_user_password(self, email: str, password_to_check: str) -> bool:
        """Проверяет соответствие пароля пользователя"""
        user = self.get_user_by_email(email)
        if user:
            return self.verify_password(password_to_check, user.password)
        return False

    def update_subscription(self, user_id: int, days_to_add: int) -> Optional[User]:
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        current_time = datetime.now()

        if user.subscriptions_end_datetime and user.subscriptions_end_datetime > current_time:
            new_end_date = user.subscriptions_end_datetime + timedelta(days=days_to_add)
        else:
            new_end_date = current_time + timedelta(days=days_to_add)

        user.subscriptions_end_datetime = new_end_date
        user.is_subscription_active = True
        self.db.commit()
        self.db.refresh(user)
        return user

    def end_subscription(self, user_id: int) -> Optional[User]:
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        user.is_subscription_active = False
        user.subscriptions_end_datetime = None
        self.db.commit()
        self.db.refresh(user)
        return user

    def decrease_attempts_count(self, user_id):

        user = self.db.query(User).filter(User.id == user_id).first()
        print("user.free_attempts_count=", user.free_attempts_count)
        user.free_attempts_count -= 1
        self.db.commit()
        print("minus user.free_attempts_count=", user.free_attempts_count)
        self.db.refresh(user)
        return user.free_attempts_count
