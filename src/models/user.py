from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from src.models.base import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    registration_datetime = Column(DateTime, nullable=False)
    username = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_subscription_active = Column(Boolean, default=False)
    subscriptions_end_datetime = Column(DateTime, nullable=True)
    free_attempts_count = Column(Integer, default=5)

    images = relationship("Image", back_populates="user")

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email})>"
