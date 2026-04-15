from fastapi import FastAPI, HTTPException, WebSocket, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import List, Dict
import uuid
import asyncio
from datetime import datetime
from schemas import OrderRequest, OrderItem
from auth import hash_password, verify_password, create_token, verify_token
from database import engine, SessionLocal
from models import UserDB, ProductDB
from database import engine, Base
from models import UserDB, ProductDB
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()

# =========================
# IN-MEMORY DATABASE
# =========================
users = []
products = []
orders = []
notifications = []
connections: Dict[str, WebSocket] = {}
idempotency_keys = set()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from fastapi import UploadFile, File
import shutil
import os

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# =========================
# MODELS
# =========================

class User(BaseModel):
    email: str
    password: str
    role: str  # admin / customer

class Product(BaseModel):
    id: str
    name: str
    price: float
    stock: int

class OrderItem(BaseModel):
    product_id: str
    quantity: int

class Order(BaseModel):
    id: str = ""
    user_email: str
    items: List[OrderItem]
    total: float = 0
    status: str = "Created"
    timestamps: Dict[str, str] = {}

class StatusUpdate(BaseModel):
    status: str

class Idempotency(BaseModel):
    key: str

class OrderRequest(BaseModel):
    user_email: str
    items: List[OrderItem]
    key: str

# =========================
# AUTH APIs
# =========================

@app.post("/auth/register")
def register(user: User):
    db = SessionLocal()

    existing = db.query(UserDB).filter(UserDB.email == user.email).first()
    if existing:
        raise HTTPException(400, "User already exists")

    new_user = UserDB(
        email=user.email,
        password=hash_password(user.password),
        role=user.role
    )

    db.add(new_user)
    db.commit()

    return {"msg": "User registered"}

@app.post("/auth/login")
def login(user: User):
    db = SessionLocal()

    db_user = db.query(UserDB).filter(UserDB.email == user.email).first()

    if not db_user:
        raise HTTPException(401, "Invalid credentials")

    if not verify_password(user.password, db_user.password):
        raise HTTPException(401, "Invalid credentials")

    token = create_token({"email": db_user.email, "role": db_user.role})

    return {"access_token": token}

# =========================
# PRODUCTS
# =========================

from database import SessionLocal

@app.post("/products")
def add_product(product: Product):
    db = SessionLocal()

    new_product = ProductDB(
        id=product.id,
        name=product.name,
        price=product.price,
        stock=product.stock
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product

@app.get("/products")
def get_products():
    db = SessionLocal()
    return db.query(ProductDB).all()

@app.patch("/products/{id}")
def update_product(id: str, stock: int, user=Depends(verify_token)):
    if user["role"] != "admin":
        raise HTTPException(403, "Admin only")

    for p in products:
        if p.id == id:
            p.stock = stock
            return p
    raise HTTPException(404, "Product not found")

# =========================
# ORDERS
# =========================

@app.post("/orders")
async def create_order(req: OrderRequest, bg: BackgroundTasks):
    db = SessionLocal()

    if req.key in idempotency_keys:
        raise HTTPException(400, "Duplicate request")

    idempotency_keys.add(req.key)

    total = 0

    # ✅ FIX: Fetch from DB (NOT products list)
    for item in req.items:
        product = db.query(ProductDB).filter(ProductDB.id == item.product_id).first()

        if not product:
            raise HTTPException(404, f"Product {item.product_id} not found")

        total += product.price * item.quantity

    order = Order(
        id=str(uuid.uuid4()),
        user_email=req.user_email,
        items=req.items,
        total=total,
        status="Created",
        timestamps={"Created": str(datetime.now())}
    )

    orders.append(order)

    add_notification("Order Created")

    bg.add_task(simulate_order_flow, order)

    return order

@app.get("/orders")
def get_orders(user=Depends(verify_token)):
    return orders

@app.get("/orders/{id}")
def get_order(id: str, user=Depends(verify_token)):
    for o in orders:
        if o.id == id:
            return o
    raise HTTPException(404, "Order not found")

@app.patch("/orders/{id}/status")
async def update_status(id: str, update: StatusUpdate, user=Depends(verify_token)):
    for o in orders:
        if o.id == id:
            o.status = update.status
            o.timestamps[update.status] = str(datetime.now())

            add_notification(f"Order {update.status}")
            await notify_order(o)
            return o

    raise HTTPException(404, "Order not found")
@app.post("/upload")
def upload_image(file: UploadFile = File(...)):
    file_path = f"{UPLOAD_DIR}/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename": file.filename}

# =========================
# WEBSOCKET
# =========================

@app.websocket("/ws/orders/{order_id}")
async def websocket_endpoint(websocket: WebSocket, order_id: str):
    await websocket.accept()
    connections[order_id] = websocket

    try:
        while True:
            await asyncio.sleep(1)
    except:
        connections.pop(order_id, None)

async def notify_order(order):
    ws = connections.get(order.id)
    if ws:
        await ws.send_json(order.dict())

async def simulate_order_flow(order):
    statuses = ["Confirmed", "Processing", "Shipped", "Delivered"]

    for status in statuses:
        await asyncio.sleep(5)

        order.status = status
        order.timestamps[status] = str(datetime.now())

        add_notification(f"Order {status}")
        await notify_order(order)

# =========================
# NOTIFICATIONS
# =========================

def add_notification(msg):
    notifications.append({
        "message": msg,
        "time": str(datetime.now())
    })

@app.get("/notifications")
def get_notifications(user=Depends(verify_token)):
    return notifications

# =========================
# ADMIN
# =========================

@app.get("/admin/orders/summary")
def summary(user=Depends(verify_token)):
    return {
        "total_orders": len(orders),
        "pending": len([o for o in orders if o.status != "Delivered"])
    }

@app.get("/admin/revenue")
def revenue(user=Depends(verify_token)):
    total = sum(o.total for o in orders)
    return {"total_revenue": total}

@app.get("/admin/top-products")
def top_products(user=Depends(verify_token)):
    return products