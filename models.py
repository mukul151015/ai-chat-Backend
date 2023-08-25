from sqlalchemy import Column, Integer, String, DateTime, Boolean
from database import Base
import datetime

class User(Base):
    __tablename__ = 'users'  # Corrected "__tablename__"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)


class TokenTable(Base):
    __tablename__ = "token"
    user_id = Column(Integer, primary_key=True)  # Added primary key constraint
    access_token = Column(String(450), unique=True, nullable=False)  # Corrected "access_token"
    refresh_token = Column(String(450), unique=True, nullable=False)  # Corrected "refresh_token"
    status = Column(Boolean)
    created_date = Column(DateTime, default=datetime.datetime.now)
