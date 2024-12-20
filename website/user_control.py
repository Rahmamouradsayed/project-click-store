from flask import Blueprint, render_template, flash, redirect, request, jsonify,session, url_for
from .classes import Product, Cart, Order
from flask_login import login_required, current_user
from . import db, mail
from intasend import APIService
import json
import random
from flask_mail import Message


UserController = Blueprint('UserController', __name__)


@UserController.route('/')
def home():
    
    return render_template('home.html',session = session.get("user"), pretty = json.dumps(session.get("user"),
                                               indent = 4))
    

@UserController.route('/orders')
@login_required
def order():
    orders = Order.query.filter_by(customer_id=current_user.id).all()
    return render_template('orders.html', orders=orders)




@UserController.route('/all_products')
def all_products():
    products = Product.query.all()  
    return render_template('all_products.html', products=products)

def products_search(keyword):
    keywords = keyword.split()  
    products = set()  
    for word in keywords:
        founded_products = Product.query.filter(Product.product_name.ilike(f'%{word}%')).all()
        for product in founded_products:
            products.add(product) 
    return products

@UserController.route('/search', methods=['POST'])
def search():
    products=set()
    keyword = request.form.get('keyword')
    if  keyword:
        products=products_search(keyword)
        if not products:
            flash('No products found')
    else:
        flash('Please enter a keyword')
        redirect(url_for('UserController.search'))
    return render_template('search.html', products=products, keyword=keyword)

def get_cart_items(customer_id):
    items = db.session.query(Product, Cart.quantity).join(Product).filter(Cart.customer_id == customer_id).all()
    total_price = 0
    total_items = 0
    for product, quantity in items:
        total_price += product.current_price * quantity
        total_items += quantity
    return items , total_price , total_items

@UserController.route('/cart')
@login_required
def cart():
        customer_id = current_user.id
        items, total_price , total_items = get_cart_items(customer_id)
        if items:
            return render_template('cart.html', items=items)
        else:
            flash("Your cart is empty")
            return render_template('cart.html')
        

@UserController.route('/order_summary', methods=['GET', 'POST'])
@login_required
def order_summary():
    customer_id = current_user.id
    items, total_price , total_items = get_cart_items(customer_id)
    
    if items:
        return render_template('order_summary.html', items=items, total_price=total_price, total_items=total_items)
    else:
        flash("Your cart is empty")
        return redirect(url_for('UserController.cart')) 

@UserController.route('/place-order-btn', methods=['POST'])
@login_required
def place_order():
    customer_id = current_user.id
    items = db.session.query(Product, Cart.quantity).join(Product).filter(Cart.customer_id == customer_id).all()
    
    random_payment_id = random.randint(10000, 999999)
    if not items:
        flash("Your cart is empty.")
        return redirect(url_for('UserController.cart'))
    
    for product, quantity in items:
        if product.in_stock < quantity:
            flash(f"Product {product.product_name} is not in stock.")
            return redirect(url_for('UserController.cart'))
        
        product.in_stock -= quantity
        order = Order(
            quantity=quantity,
            price=product.current_price * quantity,
            status="Pending",
            payment_id=random_payment_id,
            customer_id=customer_id,
            product_id=product.id
        )
        db.session.add(order)
    
    db.session.query(Cart).filter(Cart.customer_id == customer_id).delete()
    db.session.commit()

    email=current_user.email
    message = Message('Order Confirmation',
                        sender='clickstore.official65@gmail.com',
                        recipients=[email])
    message.body = f"Dear {current_user.username},\n\nThank you for your order!\n\nYour order has been placed successfully, and we are currently processing it"
    mail.send(message)
    flash("Order placed successfully!")
    return redirect(url_for('UserController.home'))
