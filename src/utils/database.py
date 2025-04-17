from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, Session
from src.models.user import Base as UserBase
from src.models.image import Base as ImageBase


# from src.settings.database_settings import DatabaseSettings


class Database:
    def __init__(self):
        # self.database_settings = DatabaseSettings()
        # self.database_url = (
        #     f"postgresql://{self.database_settings.user}:"
        #     f"{self.database_settings.password.get_secret_value()}@"
        #     f"{self.database_settings.host}/"
        #     f"{self.database_settings.db_name}"
        # )
        self.database_url = (
            f"postgresql://postgres:"
            f"17215@"
            f"127.0.0.1/"
            f"flawless_ai"
        )
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_session(self) -> Session:
        """Возвращает новую сессию для работы с БД"""
        return self.SessionLocal()

    def check_connection(self):
        try:
            with self.engine.connect() as connection:
                connection.execute("SELECT 1")
            print("Соединение с БД успешно установлено.")
        except OperationalError as e:
            print(f"Ошибка соединения с БД: {e}")

    def init_db(self):
        UserBase.metadata.create_all(bind=self.engine)
        ImageBase.metadata.create_all(bind=self.engine)
        print("Таблицы успешно созданы.")


db = Database()
db.init_db()
session = db.get_session()
