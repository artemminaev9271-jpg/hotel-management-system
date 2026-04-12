import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool  # ← ДОБАВЬТЕ ЭТУ СТРОКУ
from datetime import date
import os
import sys

# Добавляем путь к server/
current_dir = os.path.dirname(os.path.abspath(__file__))
server_dir = os.path.join(os.path.dirname(current_dir), 'server')
sys.path.insert(0, server_dir)

# Создаём папку images для тестов
images_dir = os.path.join(server_dir, 'images')
os.makedirs(images_dir, exist_ok=True)

# Импорты из server/
from main import app, get_db
from database import Base
from models import Users, Hotels, Rooms, Bookings, Reviews

# ========== НАСТРОЙКА ТЕСТОВОЙ БД ==========

# Создание тестовой БД в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Переопределение зависимости БД для тестов"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Подменяем зависимость БД в FastAPI
app.dependency_overrides[get_db] = override_get_db

# ========== ФИКСТУРЫ ==========

@pytest.fixture(scope="function", autouse=False)
def client():
    """Создание тестового клиента с чистой БД"""
    # Пересоздаём engine и metadata для каждого теста
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool  # Важно для :memory:
    )
    
    # Создаём таблицы
    Base.metadata.create_all(bind=test_engine)
    
    # Новая сессия
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    def override_get_db_test():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()
    
    # Переопределяем зависимость
    app.dependency_overrides[get_db] = override_get_db_test
    
    # Создаём клиент
    with TestClient(app) as test_client:
        yield test_client
    
    # Очищаем
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


@pytest.fixture
def test_user(client):
    """Фикстура: создание тестового пользователя"""
    response = client.post("/register/", json={
        "first_name": "Иван",
        "last_name": "Иванов",
        "email": "ivan@test.ru",
        "password": "password123"
    })
    assert response.status_code == 200
    return response.json()["user"]


@pytest.fixture
def test_hotel(client):
    """Фикстура: создание тестового отеля"""
    # Получаем сессию через dependency override
    def get_session():
        for db_session in app.dependency_overrides[get_db]():
            return db_session
    
    db = get_session()
    
    hotel = Hotels(
        name="Тестовый Отель",
        city="Москва",
        location="Тверская, 1",
        description="Отель для тестирования",
        rating=4.5
    )
    db.add(hotel)
    db.commit()
    db.refresh(hotel)
    
    result = {"id": hotel.id, "name": hotel.name, "city": hotel.city}
    return result


@pytest.fixture
def test_room(client, test_hotel):
    """Фикстура: создание тестового номера"""
    # Получаем сессию через dependency override
    def get_session():
        for db_session in app.dependency_overrides[get_db]():
            return db_session
    
    db = get_session()
    
    room = Rooms(
        hotel_id=test_hotel["id"],
        room_num=101,
        room_type="Стандарт",
        price=3000,
        is_available=True
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    
    result = {"id": room.id, "hotel_id": test_hotel["id"], "room_num": 101}
    return result


# ========== ТЕСТЫ ==========

def test_register_new_user(client):
    """Тест успешной регистрации нового пользователя"""
    response = client.post("/register/", json={
        "first_name": "Петр",
        "last_name": "Петров",
        "email": "petr@test.ru",
        "password": "pass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == "petr@test.ru"
    assert data["user"]["role"] == "CLIENT"


def test_register_duplicate_email(client, test_user):
    """Тест регистрации с уже существующим email"""
    response = client.post("/register/", json={
        "first_name": "Другой",
        "last_name": "Иванов",
        "email": "ivan@test.ru",
        "password": "pass456"
    })
    assert response.status_code == 400
    assert "уже зарегистрирован" in response.json()["detail"]


def test_login_success(client, test_user):
    """Тест успешного входа в систему"""
    response = client.post("/login/", json={
        "email": "ivan@test.ru",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == "ivan@test.ru"


def test_login_wrong_password(client, test_user):
    """Тест входа с неверным паролем"""
    response = client.post("/login/", json={
        "email": "ivan@test.ru",
        "password": "wrongpassword"
    })
    assert response.status_code == 400


def test_login_nonexistent_user(client):
    """Тест входа несуществующего пользователя"""
    response = client.post("/login/", json={
        "email": "notexist@test.ru",
        "password": "anypass"
    })
    assert response.status_code == 400


def test_search_hotels_by_city(client, test_hotel):
    """Тест поиска отелей по городу"""
    response = client.get("/search_hotels/", params={"city": "Москва"})
    assert response.status_code == 200
    hotels = response.json()
    assert len(hotels) > 0
    assert hotels[0]["city"] == "Москва"


def test_search_hotels_empty_result(client):
    """Тест поиска в городе без отелей"""
    response = client.get("/search_hotels/", params={"city": "Несуществующий"})
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_get_hotel_details(client, test_hotel):
    """Тест получения детальной информации об отеле"""
    response = client.get(f"/hotel_details/{test_hotel['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Тестовый Отель"
    assert data["city"] == "Москва"


def test_get_nonexistent_hotel(client):
    """Тест запроса несуществующего отеля"""
    response = client.get("/hotel_details/99999")
    assert response.status_code == 404


def test_top_hotels(client, test_hotel):
    """Тест получения топ-3 отелей"""
    response = client.get("/top_hotels/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_hotels_list(client, test_hotel):
    """Тест получения списка всех отелей"""
    response = client.get("/hotels_list/")
    assert response.status_code == 200
    hotels = response.json()
    assert len(hotels) > 0


def test_add_room_success(client, test_hotel):
    """Тест успешного добавления номера"""
    response = client.post("/add_room/", json={
        "hotel_id": test_hotel["id"],
        "room_num": 202,
        "room_type": "Люкс",
        "price": 5000
    })
    assert response.status_code == 200


def test_add_duplicate_room(client, test_hotel, test_room):
    """Тест добавления дубликата номера"""
    response = client.post("/add_room/", json={
        "hotel_id": test_hotel["id"],
        "room_num": 101,
        "room_type": "Другой тип",
        "price": 4000
    })
    assert response.status_code == 400


def test_book_room_success(client, test_user, test_hotel, test_room):
    """Тест успешного бронирования номера"""
    response = client.post("/book_room/", json={
        "user_id": test_user["id"],
        "hotel_id": test_hotel["id"],
        "room_id": test_room["id"],
        "in_date": "2027-08-01",
        "out_date": "2027-08-05"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["total_price"] == 12000  # 4 дня * 3000


def test_book_room_invalid_dates(client, test_user, test_hotel, test_room):
    """Тест бронирования с некорректными датами"""
    response = client.post("/book_room/", json={
        "user_id": test_user["id"],
        "hotel_id": test_hotel["id"],
        "room_id": test_room["id"],
        "in_date": "2027-08-10",
        "out_date": "2027-08-05"
    })
    assert response.status_code == 400


def test_book_room_in_past(client, test_user, test_hotel, test_room):
    """Тест бронирования в прошлом"""
    response = client.post("/book_room/", json={
        "user_id": test_user["id"],
        "hotel_id": test_hotel["id"],
        "room_id": test_room["id"],
        "in_date": "2020-01-01",
        "out_date": "2020-01-05"
    })
    assert response.status_code == 400


def test_book_already_booked_room(client, test_user, test_hotel, test_room):
    """Тест бронирования занятого номера"""
    # Первое бронирование
    client.post("/book_room/", json={
        "user_id": test_user["id"],
        "hotel_id": test_hotel["id"],
        "room_id": test_room["id"],
        "in_date": "2024-09-01",
        "out_date": "2024-09-10"
    })
    
    # Попытка второго бронирования
    response = client.post("/book_room/", json={
        "user_id": test_user["id"],
        "hotel_id": test_hotel["id"],
        "room_id": test_room["id"],
        "in_date": "2024-09-05",
        "out_date": "2024-09-15"
    })
    assert response.status_code == 400


def test_get_user_bookings(client, test_user, test_hotel, test_room):
    """Тест получения списка бронирований"""
    # Создаём бронь
    client.post("/book_room/", json={
        "user_id": test_user["id"],
        "hotel_id": test_hotel["id"],
        "room_id": test_room["id"],
        "in_date": "2027-10-01",
        "out_date": "2027-10-05"
    })
    
    response = client.get(f"/my_bookings/{test_user['id']}")
    assert response.status_code == 200
    bookings = response.json()
    assert len(bookings) > 0


def test_add_review_success(client, test_user, test_hotel):
    """Тест успешного добавления отзыва"""
    response = client.post("/add_review/", json={
        "user_id": test_user["id"],
        "hotel_id": test_hotel["id"],
        "rating": 5.0,
        "comment": "Отличный отель!"
    })
    assert response.status_code == 200


def test_review_updates_hotel_rating(client, test_user, test_hotel):
    """Тест пересчёта рейтинга отеля"""
    client.post("/add_review/", json={
        "user_id": test_user["id"],
        "hotel_id": test_hotel["id"],
        "rating": 5.0,
        "comment": "Отлично!"
    })
    
    # Проверяем, что рейтинг изменился
    response = client.get(f"/hotel_details/{test_hotel['id']}")
    # Рейтинг должен быть средним между 4.5 (начальным) и новыми отзывами
    assert response.status_code == 200


def test_root_endpoint(client):
    """Тест корневого endpoint"""
    response = client.get("/")
    assert response.status_code == 200