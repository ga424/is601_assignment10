from typing import List
from fastapi import Depends, FastAPI, HTTPException, Request, RedirectResponse, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import Base, engine, get_db
from app.schemas import UserCreate, UserResponse
from app.models import User, Calculator
import os

app = FastAPI()

# Set up templates
templates_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
templates = Jinja2Templates(directory=templates_dir)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    auth_result = User.authenticate(db, username, password)
    if not auth_result:
        return RedirectResponse(url="/login?error=Invalid credentials", status_code=303)
    return {"access_token": auth_result["access_token"], "token_type": "bearer", "user": auth_result["user"]}

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user_data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "username": username,
        "password": password
    }
    try:
        new_user = User.register(db, user_data)
        db.commit()
        return RedirectResponse(url="/login?success=Account created, please login", status_code=303)
    except ValueError as e:
        return RedirectResponse(url="/register?error=" + str(e), status_code=303)

@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(email=user.email, password=user.password, name=user.name, is_active=user.is_active)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=List[UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

