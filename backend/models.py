from sqlalchemy import Column, String, Float, Integer
from database import Base

class UserDB(Base):
    __tablename__ = "users"

    email = Column(String, primary_key=True, index=True)
    password = Column(String)
    role = Column(String)


class ProductDB(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True)
    name = Column(String)
    price = Column(Float)
    stock = Column(Integer)