from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models, schemas
from dependencies import get_db

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/")
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    new_order = models.Order(
        product_id=order.product_id,
        user_id=1,
        status="pending"
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

@router.get("/")
def get_orders(db: Session = Depends(get_db)):
    return db.query(models.Order).all()

@router.get("/{id}")
def get_order(id: int, db: Session = Depends(get_db)):
    return db.query(models.Order).filter(models.Order.id == id).first()

@router.patch("/{id}/status")
def update_status(id: int, status: str, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == id).first()
    order.status = status
    db.commit()
    return {"msg": "Status updated"}