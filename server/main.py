from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel
import database
import models
import os
import shutil
import uuid

models.Base.metadata.create_all(bind=database.engine)
app = FastAPI(title="Hotel Booking API")
app.mount("/images", StaticFiles(directory="images"), name="images")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

class User_register(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str

class User_login(BaseModel):
    email: str
    password: str

class Room_add(BaseModel):
    hotel_id: int
    room_num: int
    room_type: str
    price: int

@app.post("/register/")
def register_user(user: User_register, db: Session = Depends(get_db)):
    db_user = db.query(models.Users).filter(models.Users.email == user.email).first()

    if db_user:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    
    new_user = models.Users(
        first_name = user.first_name,
        last_name = user.last_name, 
        email = user.email,
        password = user.password,
        role = "ADMIN"
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при сохранении пользователя")
   
    data = {
        "id": new_user.id,
        "first_name": new_user.first_name,
        "last_name": new_user.last_name,
        "email": new_user.email,
        "role": new_user.role
    }

    return {"message": "Пользователь успешно зарегистрирован", "user": data}

@app.post("/login/")
def login_user(user: User_login, db: Session = Depends(get_db)):
    db_user = db.query(models.Users).filter(models.Users.email == user.email, models.Users.password == user.password).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="Неверный email или пароль")
    
    data = {
        "id": db_user.id,
        "first_name": db_user.first_name,
        "last_name": db_user.last_name,
        "email": db_user.email,
        "role": db_user.role
    }

    return {"message": "Успешный вход", "user": data}

@app.post("/add_hotel/")
def add_hotel(name: str = Form(...), location: str = Form(...), city: str = Form(...), description: str = Form(...), image: UploadFile = File(...), db: Session = Depends(get_db)):
    db_hotel = db.query(models.Hotels).filter(models.Hotels.name == name).first()

    if db_hotel:
        raise HTTPException(status_code=400, detail="Отель с таким названием уже существует")

    os.makedirs("images", exist_ok=True)
    safe_filename = f"{uuid.uuid4().hex[:8]}_{image.filename}"
    file_path = os.path.join("images", safe_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    new_hotel = models.Hotels(
        name = name,
        location = location,
        city = city,
        description = description,
        image_path = file_path
    )

    try:
        db.add(new_hotel)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при сохранении отеля")

@app.post("/add_room/")
def add_room(room: Room_add, db: Session = Depends(get_db)):
    db_room = db.query(models.Rooms).filter(models.Rooms.hotel_id == room.hotel_id, models.Rooms.room_num == room.room_num).first()

    if db_room:
        raise HTTPException(status_code=400, detail="Комната с таким номером уже есть в этом отеле")

    new_room = models.Rooms(
        hotel_id = room.hotel_id,
        room_num = room.room_num,
        room_type = room.room_type,
        price = room.price,
        is_available = True
    )

    try:
        db.add(new_room)
        db.commit()
        return {"message": "Комната успешно добавлена"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при сохранении комнаты")

@app.get("/hotels_list/")
def get_hotels_list(db: Session = Depends(get_db)):
    hotels = db.query(models.Hotels).all()
    
    return [{"id": h.id, "name": h.name} for h in hotels]

@app.get("/search_hotels/")
def search_hotels(city: str = Query(None), name: str = Query(None), db: Session = Depends(get_db)):
    all_hotels = db.query(models.Hotels).all()

    result = []
    
    for hotel in all_hotels:
        if city:
            if city.lower() not in hotel.city.lower():
                continue

        if name:
            if name.lower() not in hotel.name.lower():
                continue

        min_price = "Нет номеров"
        if hotel.rooms:
            min_price = min([room.price for room in hotel.rooms])

        result.append({
            "id": hotel.id,
            "name": hotel.name,
            "city": hotel.city,
            "rating": hotel.rating or 0.0,
            "min_price": min_price,
            "image_path": hotel.image_path
        })

    return result

@app.get("/hotel_details/{hotel_id}")
def get_hotel_details(hotel_id: int, db: Session = Depends(get_db)):
    hotel = db.query(models.Hotels).filter(models.Hotels.id == hotel_id).first()
    
    if not hotel:
        raise HTTPException(status_code=404, detail="Отель не найден")

    rooms_data = []
    for room in hotel.rooms:
        rooms_data.append({
            "id": room.id,
            "room_num": room.room_num,
            "room_type": room.room_type,
            "price": room.price,
            "is_available": room.is_available
        })

    return {
        "id": hotel.id,
        "name": hotel.name,
        "city": hotel.city,
        "location": hotel.location,
        "description": hotel.description,
        "rating": hotel.rating or 0.0,
        "image_path": hotel.image_path,
        "rooms": rooms_data
    }

@app.get("/")
def read_root():
    return {"message": "Сервер бронирования отелей успешно работает!"}