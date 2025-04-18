from sqlalchemy import Column, Integer, Boolean, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from src.models.base import Base


class Image(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    fix_datetime = Column(DateTime, nullable=False)
    is_liked = Column(Boolean, default=False)
    defected_path = Column(String, nullable=False)
    fixed_path = Column(String, nullable=False)
    masked_path = Column(String, nullable=False)
    segmented_path = Column(String, nullable=False)

    user = relationship("User", back_populates="images")

    def __repr__(self):
        return f"<Image(id={self.id}, user_id={self.user_id})>"
