import datetime
from math import prod
import os
from sqlalchemy import Column, String, create_engine
from flask_sqlalchemy import SQLAlchemy
import json

database_path = os.environ['DATABASE_URL']
if database_path.startswith("postgres://"):
  database_path = database_path.replace("postgres://", "postgresql://", 1)

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()

'''
The default interface for a table in the database
Contains methods for getting all items, getting one item, inserting, updating, and deleting items
'''
class DefaultTableInterface:
  @classmethod
  def get_all(cls, page=1, items_per_page=10):
    start = (page - 1) * items_per_page
    end = start + items_per_page
    products = db.session.query(cls).where(cls.id >= start).where(cls.id < end).all()
    return products
  
  @classmethod
  def count_total(cls):
    return db.session.query(cls).count()
  
  @classmethod
  def insert(cls, product):
    db.session.add(product)
    db.session.commit()

  @classmethod
  def update(cls, product):
    db.session.commit()
  
  @classmethod
  def delete(cls, product):
    db.session.delete(product)
    db.session.commit()

  @classmethod
  def get_one_or_none(cls, id):
    return db.session.query(cls).get(id)


'''
A brand of a product
'''
class Brand(db.Model, DefaultTableInterface):
  __tablename__ = 'Brands'

  id = Column(db.Integer, primary_key=True)
  name = Column(String)
  catchphrase = Column(String)

  def __init__(self, name, catchphrase=""):
    self.name = name
    self.catchphrase = catchphrase

  def format(self):
    return {
      'id': self.id,
      'name': self.name,
      'catchphrase': self.catchphrase}
  

'''
A product category
'''
class ProductCategory(db.Model, DefaultTableInterface):
  __tablename__ = 'ProductCategories'

  id = Column(db.Integer, primary_key=True)
  name = Column(String)
  description = Column(String)

  def __init__(self, name, description=""):
    self.name = name
    self.description = description

  def format(self):
    return {
      'id': self.id,
      'name': self.name,
      'description': self.description}

'''
A product in the store
'''
class Product(db.Model):  
  __tablename__ = 'Products'

  id = Column(db.Integer, primary_key=True)
  name = Column(String)
  price = Column(db.Float)
  brand = Column(db.Integer, db.ForeignKey('Brands.id'), nullable=False)
  description = Column(String)
  product_category = Column(db.Integer, db.ForeignKey('ProductCategories.id'))
  

  def __init__(self, name, price, brand, description, product_category):
    self.name = name
    self.price = price
    self.brand = brand
    self.description = description
    self.product_category = product_category


  def format(self):
    return {
      'id': self.id,
      'name': self.name,
      'description': self.description,
      'price': self.price,
      'price_usd': f"${self.price:.2f}",
      'product_category': ProductCategory.get_one_or_none(self.product_category).format(),
      'brand': Brand.get_one_or_none(self.brand).format()}
  
'''
A review of a product
'''
class ProductReview(db.Model, DefaultTableInterface):
  __tablename__ = 'ProductReviews'

  id = Column(db.Integer, primary_key=True)
  review = Column(String)
  rating = Column(db.Float)
  product = Column(db.Integer, db.ForeignKey('Products.id'), nullable=False)

  def __init__(self, review, rating):
    self.review = review
    self.rating = rating

  def format(self):
    return {
      'id': self.id,
      'review': self.review,
      'rating': self.rating}

'''
A customer of the store
'''
class Customer(db.Model, DefaultTableInterface):
  __tablename__ = 'Customers'

  id = Column(db.Integer, primary_key=True)
  name = Column(String)
  email = Column(String)
  address = Column(String)

  def __init__(self, name, email, address):
    self.name = name
    self.email = email
    self.address = address

  def format(self):
    return {
      'id': self.id,
      'name': self.name,
      'email': self.email,
      'address': self.address}

'''
An order in the store
'''
class Order(db.Model, DefaultTableInterface):
  __tablename__ = 'Orders'

  id = Column(db.Integer, primary_key=True)
  customer = Column(db.Integer, db.ForeignKey('Customers.id'), nullable=False)
  items_json = Column(String, nullable=False, default="{}")
  cost = Column(db.Float, nullable=False, default=0.0)
  datetime = Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
  status = Column(String, nullable=False, default="pending")

  def __init__(self, customer, items_json, cost):
    self.customer = customer
    self.items_json = items_json
    self.cost = cost

  def pretty_print_items(self):
    items = json.loads(self.items_json)
    pretty_items = ""
    for item in items:
      pretty_items += f"{item['name']} x{item['quantity']}, "
    
    return pretty_items[:-2]


  def format(self):
    return {
      'id': self.id,
      'customer': self.customer,
      'items_json': self.items_json,
      'cost': self.cost,
      'datetime': self.datetime,
      'status': self.status}