# main.py - Main entry point for FastAPI application

import logging
import os
import time
from typing import List

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import engine, get_db
from app.models.user import User
from app.operations import add, divide, multiply, subtract
from app.schemas import UserCreate, UserResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Setup templates directory
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)


class OperationRequest(BaseModel):
    a: float = Field(..., description="The first number")
    b: float = Field(..., description="The second number")

    @field_validator("a", "b")
    def validate_numbers(cls, value):
        if not isinstance(value, (int, float)):
            raise ValueError("Both a and b must be numbers.")
        return value


class OperationResponse(BaseModel):
    result: float = Field(..., description="The result of the operation")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error("HTTPException on %s: %s", request.url.path, exc.detail)
    from fastapi.responses import JSONResponse

    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error("RequestValidationError on %s: %s", request.url.path, exc)
    from fastapi.responses import JSONResponse

    return JSONResponse(status_code=422, content={"error": "Invalid request data"})


@app.on_event("startup")
def on_startup():
    # Wait for database readiness before creating tables to avoid startup race conditions.
    max_attempts = 30
    for attempt in range(1, max_attempts + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            User.metadata.create_all(bind=engine)
            logger.info("Database is ready; tables initialized")
            return
        except SQLAlchemyError as exc:
            logger.warning("Database not ready (attempt %s/%s): %s", attempt, max_attempts, exc)
            time.sleep(1)

    raise RuntimeError("Database did not become ready during startup")


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
    return {
        "access_token": auth_result["access_token"],
        "token_type": "bearer",
        "user": auth_result["user"],
    }


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
    db: Session = Depends(get_db),
):
    user_data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "username": username,
        "password": password,
    }
    try:
        User.register(db, user_data)
        db.commit()
        return RedirectResponse(url="/login?success=Account created, please login", status_code=303)
    except ValueError as exc:
        return RedirectResponse(url="/register?error=" + str(exc), status_code=303)


@app.get("/add")
def add_route(a: float, b: float):
    try:
        result = add(a, b)
        return OperationResponse(result=result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/subtract")
def subtract_route(a: float, b: float):
    try:
        result = subtract(a, b)
        return OperationResponse(result=result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/multiply")
def multiply_route(a: float, b: float):
    try:
        result = multiply(a, b)
        return OperationResponse(result=result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/divide")
def divide_route(a: float, b: float):
    try:
        result = divide(a, b)
        return OperationResponse(result=result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User.register(db, user.dict())
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get("/users/", response_model=List[UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(User).offset(skip).limit(limit).all()


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
