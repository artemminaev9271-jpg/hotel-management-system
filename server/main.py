from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import database
import models

models.Base.metadata.create_all(bind=database.engine)
app = FastAPI(title="Hotel Booking API")

# Зависимость для получения сессии БД
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

@app.post("/register/")
def register_user(user: User_register, db: Session = Depends(get_db)):
    db_user = db.query(models.Users).filter(models.Users.email == user.email).first()

    if db_user:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    
    new_user = models.Users(
        first_name = user.first_name,
        last_name = user.last_name,
        email = user.email,
        password = user.password
    )

    db.add(new_user)
    db.commit()
    return {"message": "Пользователь успешно зарегистрирован"}

@app.post("/login/")
def login_user(user: User_login, db: Session = Depends(get_db)):
    db_user = db.query(models.Users).filter(models.Users.email == user.email, models.Users.password == user.password).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="Неверный email или пароль")
    
    return {"message": "Успешный вход", "user_id": db_user.id, "role": db_user.role}

@app.get("/")
def read_root():
    return {"message": "Сервер бронирования отелей успешно работает!"}