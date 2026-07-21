from sqlalchemy import Column, Integer, String
from database import Base


class User(Base):

    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="User")


class Employee(Base):

    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    ssn = Column(String, nullable=False)
    salary = Column(String, nullable=False)