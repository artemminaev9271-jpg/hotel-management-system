from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Создаем "движок" базы данных SQLite
# echo=True будет выводить в консоль реальные SQL-запросы (удобно для отладки)
SQLALCHEMY_DATABASE_URL = "sqlite:///hotel.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)

# Создаем фабрику сессий (через сессию мы будем добавлять и искать данные)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс, от которого мы будем наследовать все наши таблицы
Base = declarative_base()
