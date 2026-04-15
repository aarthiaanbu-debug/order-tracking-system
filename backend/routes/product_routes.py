from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models, schemas
from dependencies import get_db

router = APIRouter(prefix="/products")

@router.post("/")
def add_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    p = models.Product(**product.dict())
    db.add(p)
    db.commit()
    return {"msg": "Product added"}

@router.get("/")
def get_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()