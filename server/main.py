from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date, datetime
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

class Booking_add(BaseModel):
    user_id: int
    hotel_id: int
    room_id: int
    in_date: date
    out_date: date

class Review_add(BaseModel):
    user_id: int
    hotel_id: int
    rating: float
    comment: str

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

    rooms_data = [{"id": r.id, "room_num": r.room_num, "room_type": r.room_type, "price": r.price, "is_available": r.is_available} for r in hotel.rooms]

    reviews_data = []
    for rev in hotel.reviews:
        author_name = f"{rev.users.first_name} {rev.users.last_name}" if rev.users else "Аноним"
        
        reviews_data.append({
            "id": rev.id,
            "author": author_name,
            "rating": rev.rating,
            "comment": rev.comment,
            "created_at": rev.created_at.strftime("%d.%m.%Y")
        })

    return {
        "id": hotel.id,
        "name": hotel.name,
        "city": hotel.city,
        "location": hotel.location,
        "description": hotel.description,
        "rating": hotel.rating or 0.0,
        "image_path": hotel.image_path,
        "rooms": rooms_data,
        "reviews": reviews_data
    }

@app.post("/book_room/")
def book_room(booking: Booking_add, db: Session = Depends(get_db)):
    if booking.in_date >= booking.out_date:
        raise HTTPException(status_code=400, detail="Дата выезда должна быть позже даты заезда.")
    if booking.in_date < date.today():
        raise HTTPException(status_code=400, detail="Нельзя забронировать номер в прошлом.")

    overlapping_booking = db.query(models.Bookings).filter(
        models.Bookings.room_id == booking.room_id,
        models.Bookings.in_date < booking.out_date,
        models.Bookings.out_date > booking.in_date
    ).first()

    if overlapping_booking:
        busy_from = overlapping_booking.in_date.strftime("%d.%m.%Y")
        busy_to = overlapping_booking.out_date.strftime("%d.%m.%Y")
        
        error_msg = f"Номер занят на выбранные даты!\nПересечение с существующей бронью:\nс {busy_from} по {busy_to}"
        
        raise HTTPException(status_code=400, detail=error_msg)

    room = db.query(models.Rooms).filter(models.Rooms.id == booking.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Номер не найден.")

    days = (booking.out_date - booking.in_date).days
    total_price = days * room.price

    new_booking = models.Bookings(
        hotel_id=booking.hotel_id,
        room_id=booking.room_id,
        user_id=booking.user_id,
        in_date=booking.in_date,
        out_date=booking.out_date,
        total_price=total_price,
        created_at=date.today()
    )

    try:
        db.add(new_booking)
        db.commit()
        return {"message": "Успешно забронировано!", "total_price": total_price}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при бронировании.")

@app.get("/my_bookings/{user_id}")
def get_user_bookings(user_id: int, db: Session = Depends(get_db)):
    bookings = db.query(models.Bookings).filter(
        models.Bookings.user_id == user_id
    ).order_by(models.Bookings.in_date.desc()).all()

    result = []
    today = date.today()

    for b in bookings:
        status = "Активна" if b.out_date >= today else "Завершена"

        result.append({
            "id": b.id,
            "hotel_name": b.hotels.name,
            "city": b.hotels.city,
            "room_num": b.rooms.room_num,
            "room_type": b.rooms.room_type,
            "in_date": b.in_date.strftime("%d.%m.%Y"),
            "out_date": b.out_date.strftime("%d.%m.%Y"),
            "total_price": b.total_price,
            "status": status
        })
        
    return result

@app.post("/add_review/")
def add_review(review: Review_add, db: Session = Depends(get_db)):
    new_review = models.Reviews(
        user_id = review.user_id,
        hotel_id = review.hotel_id,
        rating = review.rating,
        comment = review.comment,
        created_at = date.today()
    )
    db.add(new_review)
    db.commit()

    hotel = db.query(models.Hotels).filter(models.Hotels.id == review.hotel_id).first()
    if hotel:
        all_reviews = db.query(models.Reviews).filter(models.Reviews.hotel_id == review.hotel_id).all()
        if all_reviews:
            avg_rating = sum([r.rating for r in all_reviews]) / len(all_reviews)
            hotel.rating = round(avg_rating, 1)
            db.commit()

    return {"message": "Отзыв успешно добавлен"}

@app.get("/top_hotels/")
def get_top_hotels(db: Session = Depends(get_db)):
    top_hotels = db.query(models.Hotels).order_by(models.Hotels.rating.desc()).limit(3).all()
    
    result = []
    for h in top_hotels:
        min_price = min([r.price for r in h.rooms]) if h.rooms else "Нет номеров"
        result.append({
            "id": h.id,
            "name": h.name,
            "city": h.city,
            "rating": h.rating or 0.0,
            "price": min_price
        })
    return result

@app.get("/")
def read_root():
    return {"message": "Сервер бронирования отелей успешно работает!"}