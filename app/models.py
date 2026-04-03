from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)   

class Calculator():
    
    __tablename__ = "calculators"

    operator: Mapped[str] = mapped_column(String(10), primary_key=True, index=True)
    operand1: Mapped[int] = mapped_column(Integer, nullable=False)
    operand2: Mapped[int] = mapped_column(Integer, nullable=False)
    result: Mapped[int] = mapped_column(Integer, nullable=False)
    