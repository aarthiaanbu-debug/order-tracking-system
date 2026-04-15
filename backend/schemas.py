from pydantic import BaseModel
from typing import List, Dict


# =====================
# USER
# =====================
class User(BaseModel):
    email: str
    password: str
    role: str


class UserLogin(BaseModel):
    email: str
    password: str


# =====================
# PRODUCT
# =====================
class ProductCreate(BaseModel):
    id: str
    name: str
    price: float
    stock: int


# =====================
# ORDER
# =====================
class OrderItem(BaseModel):
    product_id: str
    quantity: int


class OrderRequest(BaseModel):
    user_email: str
    items: List[OrderItem]
    key: str
class Product(BaseModel):
    id: str
    name: str
    price: float
    stock: int
    image: str = ""