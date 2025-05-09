from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from cryptography.fernet import Fernet
import os

# Настройка базы данных
DATABASE_URL = "sqlite:///./graphene.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Генерация ключа шифрования
SECRET_KEY = os.getenv("SECRET_KEY", Fernet.generate_key().decode())
fernet = Fernet(SECRET_KEY)

# Пример шифрования и дешифрования
class EncryptedString(String):
    def bind_processor(self, dialect):
        def process(value):
            if value is not None:
                return fernet.encrypt(value.encode()).decode()
            return value
        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            if value is not None:
                return fernet.decrypt(value.encode()).decode()
            return value
        return process

# Модель пользователя
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(EncryptedString, unique=True, index=True)
    language = Column(EncryptedString, default="en")
    balance = Column(Integer, default=0)

# Создание таблиц
Base.metadata.create_all(bind=engine)
