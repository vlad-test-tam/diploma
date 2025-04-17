import re
import json
from datetime import datetime
from typing import Optional

from argon2 import PasswordHasher

from src.entities.user import UserDTO, UserAddDTO
from src.repositories.user_repository import UserRepository
from src.utils.database import session

ph = PasswordHasher()

user_repository = UserRepository(session)


class AuthService:
    def __init__(self, user_repo: UserRepository = user_repository):
        self.user_repo = user_repo

    def authenticate_user(self, username: str, password: str) -> Optional[UserDTO]:
        """
        Аутентифицирует пользователя по username и password.
        Возвращает UserDTO если аутентификация успешна, иначе None.
        """
        user = self.user_repo.get_user_by_email(username)
        if not user:
            return None

        if not self.user_repo.verify_password(password, user.password):
            return None

        return UserDTO.model_validate(user)

    def check_usr_pass(self, email: str, password: str) -> bool:
        return self.authenticate_user(email, password) is not None

    def check_valid_email(self, email: str) -> bool:
        """
        Checks if the user entered a valid email while creating the account.
        """
        regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

        if re.fullmatch(regex, email):
            return True
        return False

    def check_unique_email(self, email_sign_up: str) -> bool:
        return self.user_repo.get_user_by_email(email_sign_up) is None

    def non_empty_str_check(self, string: str) -> bool:
        """
        Checks for non-empty strings.
        """
        empty_count = 0
        for i in string:
            if i == ' ':
                empty_count = empty_count + 1
                if empty_count == len(string):
                    return False

        if not string:
            return False
        return True

    def check_password(self, password: str, check_password: str):
        return password == check_password

    def register_new_user(self, name: str, email: str, username: str, password: str) -> UserDTO:

        if self.user_repo.get_user_by_email(email) is not None:
            raise Exception("User with this username or email already exists")

        user_data = UserAddDTO(
            registration_datetime=datetime.now(),
            username=username,
            email=email,
            password=password,  # Будет захеширован в репозитории
            is_subscription_active=False,
            free_attempts_count=5
        )

        return self.user_repo.create_user(user_data)

    def check_email_exists(self, email: str) -> tuple[bool, Optional[str]]:
        """
        Проверяет существование email в базе данных
        Returns:
            tuple: (exists: bool, username: Optional[str])
        """
        user = self.user_repo.get_user_by_email(email)
        return (user is not None, user.username if user else None)

    def change_name(self, user_id: str, new_name: str) -> None:
        """Изменяет пароль пользователя"""
        self.user_repo.update_username(user_id, new_name)

    def change_password(self, email: str, new_password: str) -> None:
        """Изменяет пароль пользователя"""
        hashed_password = self.user_repo.get_password_hash(new_password)
        print(new_password)
        self.user_repo.update_user_password(email, hashed_password)

    def check_current_password(self, email: str, current_password: str) -> bool:
        """Проверяет текущий пароль пользователя"""
        return self.user_repo.verify_user_password(email, current_password)

    def get_user_by_email(self, email):
        return self.user_repo.get_user_by_email(email)

    def get_user_by_id(self, user_id):
        return self.user_repo.get_user_by_id(user_id)
