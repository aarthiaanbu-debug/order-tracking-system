from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models
from dependencies import get_db

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/orders/summary")
def order_summary(db: Session = Depends(get_db)):
    orders = db.query(models.Order).all()
    return {
        "total_orders": len(orders),
        "pending": len([o for o in orders if o.status == "pending"]),
        "completed": len([o for o in orders if o.status == "completed"])
    }

@router.get("/revenue")
def revenue(db: Session = Depends(get_db)):
    orders = db.query(models.Order).all()
    revenue = len(orders) * 100  # dummy price
    return {"total_revenue": revenue}