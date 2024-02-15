from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float

Base = declarative_base()


class Product(Base):
    __tablename__ = "product"

    nm_id = Column(Integer, primary_key=True)
    name = Column(String)
    brand = Column(String)
    brand_id = Column(String)
    site_brand_id = Column(String)
    supplier_id = Column(Integer)
    sale = Column(Integer)
    price = Column(Integer)
    sale_price = Column(Integer)
    rating = Column(Float)
    feedbacks = Column(Integer)
    colors = Column(String)
    # quantity = Column(Integer)  #кол-во товара в наличии
