from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from dao.wb_card import *


# сделать более унифицированным
class DBHelper:
    def __init__(self, user, passwd, host, port, db):
        postgresql_url = f"postgresql://{user}:{passwd}@{host}:{port}/{db}"
        print(postgresql_url)
        if not database_exists(postgresql_url):
            create_database(postgresql_url)
        self.engine = create_engine(postgresql_url)
        self.session = sessionmaker(bind=self.engine)()

    def create_table(self):
        Base.metadata.create_all(self.engine)

    def insert(self, data):
        for product in data:
            self.session.add(product)
            try:
                self.session.commit()
            except IntegrityError as e:
                self.session.rollback()
                continue

    def print_info(self):
        products = self.session.query(Product).all()
        for product in products:
            print("ID:", product.nm_id)
            print("Product name:", product.name)
            print("Product brand:", product.brand)
            print("Brand id:", product.brand_id)
            print("Site brand id:", product.site_brand_id)
            print("Supplier id:", product.supplier_id)
            print("Product sale:", product.sale)
            print("Product price:", product.price)
            print("Discounted price:", product.sale_price)
            print("Product rating:", product.rating)
            print("Product feedbacks:", product.feedbacks)
            print("Colors:", product.colors)
            print("Product quantity:", product.quantity)    #?
            print()

    def update(self, nm_id, updates):
        item = self.session.query(Product).filter_by(id=nm_id).first()
        if item:
            for key, value in updates.items():
                setattr(item, key, value)
            self.session.commit()
        else:
            print("Запись не найдена")

    def delete(self, nm_id):
        item = self.session.query(Product).filter_by(id=nm_id).first()
        if item:
            self.session.delete(item)
            self.session.commit()
        else:
            print("Запись не найдена")

    def close(self):
        self.session.close()