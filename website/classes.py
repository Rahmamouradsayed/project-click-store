from . import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Customer(db.Model, UserMixin):
    __tablename__ = 'Customers' 
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    date_joined = db.Column(db.DateTime(), default=datetime.utcnow)
    reset_token_used = db.Column(db.Boolean, default=False) 

    cart_items = db.relationship('Cart', backref=db.backref('customer', lazy=True))
    wishlist_items = db.relationship('Wishlist', backref=db.backref('customer', lazy=True))
    orders = db.relationship('Order', backref=db.backref('customer', lazy=True))
      
    @property
    def password(self):
        raise AttributeError('Password is not a readable Attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password=password, method='scrypt')
    
    def check_password(self, password):
        print(f"Checking password: {password} against hash: {self.password_hash}")
        return check_password_hash(self.password_hash, password)

    def __str__(self):
        return f'<Customer {self.id}>'

class Wishlist(db.Model):
    __tablename__ = 'Wishlist'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'), nullable=False)  
    product_id = db.Column(db.Integer, db.ForeignKey('Products.id'), nullable=False) 

class Product(db.Model):
    __tablename__ = 'Products'  
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    previous_price = db.Column(db.Float, nullable=False)
    in_stock = db.Column(db.Integer, nullable=False)
    product_picture = db.Column(db.String(1000), nullable=False)
    flash_sale = db.Column(db.Boolean, default=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(50), nullable=False)

    wishlist = db.relationship('Wishlist', backref=db.backref('product', lazy=True))
    carts = db.relationship('Cart', backref=db.backref('product', lazy=True))
    orders = db.relationship('Order', backref=db.backref('product', lazy=True))

    def __str__(self):
        return f'<Product {self.product_name}>'


class Cart(db.Model):
    __tablename__ = 'Cart'  
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'), nullable=False)  
    product_id = db.Column(db.Integer, db.ForeignKey('Products.id'), nullable=False)  

    def __str__(self):
        return f'<Cart {self.id}>'


class Order(db.Model):
    __tablename__ = 'Orders'  
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(100), nullable=False)
    payment_id = db.Column(db.String(1000), nullable=False)

    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'), nullable=False) 
    product_id = db.Column(db.Integer, db.ForeignKey('Products.id'), nullable=False)  

    def __str__(self):
        return f'<Order {self.id}>'


