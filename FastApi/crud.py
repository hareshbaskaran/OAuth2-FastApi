from sqlalchemy.orm import Session
import models, schemas


def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(name=product.name, description=product.description, price=product.price,
                                quantity=product.quantity, seller_id=product.seller_id, carrier_id=product.carrier_id,
                                category_id=product.category_id)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def get_product_by_name(db: Session, name: str):
    return db.query(models.Product).filter(models.Product.name == name).first()


def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Product).offset(skip).limit(limit).all()
