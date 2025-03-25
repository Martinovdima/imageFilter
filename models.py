from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime


Base = declarative_base()
# Определение модели User
class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, nullable=False, unique=True, index=True)
    username = Column(String, nullable=True)
    login_time = Column(DateTime, default=datetime.utcnow)

    requests = relationship("ImageProcessingRequest", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, username={self.username})>"

class ImageProcessingRequest(Base):
    __tablename__ = "image_processing_requests"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    uploaded_image_id = Column(String, nullable=False)
    processed_image_id = Column(String, nullable=True)
    processing_type = Column(String, nullable=False)
    request_time = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="requests")

    def __repr__(self):
        return f"<Request(user_id={self.user_id}, type={self.processing_type}, time={self.request_time})>"
# Функция создания или обновления пользователя