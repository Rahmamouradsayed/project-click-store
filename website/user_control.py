from flask import Blueprint, render_template, flash, redirect, request, jsonify,session, url_for
from .classes import Product, Cart, Order
from flask_login import login_required, current_user
from . import db
from intasend import APIService
import json
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


# @UserController.route('/search', methods=['GET', 'POST'])
# def search():
#     if request.method == 'POST':
#         search_query = request.form.get('search')
#         items = Product.query.filter(Product.product_name.ilike(f'%{search_query}%')).all()
#         return render_template('search.html', items=items, cart=Cart.query.filter_by(customer_id=current_user.id).all()
#                            if current_user.is_authenticated else [])

#     return render_template('search.html')
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
    return items

@UserController.route('/cart')
def cart():
    if current_user.is_authenticated:
        customer_id = current_user.id
        items = get_cart_items(customer_id)
        
        if items:
            total_price = 0
            total_items = 0
            
            for product, quantity in items:
                total_price += product.current_price * quantity
                total_items += quantity
                
            return render_template('cart.html', items=items, total_price=total_price, total_items=total_items)
        else:
            flash("Your cart is empty")
            return render_template('cart.html')
    else:
        flash('You must be logged in to view your cart')
        return redirect(url_for('auth.login'))
        

