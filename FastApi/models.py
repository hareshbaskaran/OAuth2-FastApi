from sqlalchemy import Column, Integer, String, Float

from database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    price = Column(Float)
    quantity = Column(Integer)
    seller_id = Column(Integer)
    carrier_id = Column(Integer)
    category_id = Column(Integer)