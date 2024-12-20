from flask import Blueprint, render_template, flash, redirect, request, jsonify,session
from .classes import Product, Cart, Order ,Wishlist
from flask_login import login_required, current_user
from . import db
from intasend import APIService
import json
from dotenv import load_dotenv
import os

load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')
API_PUBLISHABLE_KEY = os.getenv('API_PUBLISHABLE_KEY')

service = APIService(token=API_TOKEN, publishable_key=API_PUBLISHABLE_KEY, test=True)

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


@UserController.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form.get('search')
        items = Product.query.filter(Product.product_name.ilike(f'%{search_query}%')).all()
        return render_template('search.html', items=items, cart=Cart.query.filter_by(customer_id=current_user.id).all()
                           if current_user.is_authenticated else [])

    return render_template('search.html')

@UserController.route('/add-to-wishlist/<int:item_id>')
@login_required
def add_to_wishlist(item_id):
    item_to_add = Product.query.get(item_id)
    item_exists = Wishlist.query.filter_by(product_link=item_id, customer_link=current_user.id).first()

    if item_exists:
        flash(f'{item_to_add.product_name} is already in your wishlist!')
        return redirect(request.referrer)

    new_wishlist_item = Wishlist()
    new_wishlist_item.product_link = item_to_add.id
    new_wishlist_item.customer_link = current_user.id

    try:
        db.session.add(new_wishlist_item)
        db.session.commit()
        flash(f'{item_to_add.product_name} added to wishlist')
    except Exception as e:
        print('Item not added to wishlist', e)
        flash(f'{item_to_add.product_name} has not been added to wishlist')

    return redirect(request.referrer)

@UserController.route('/remove-from-wishlist/<int:item_id>')
@login_required
def remove_from_wishlist(item_id):
    item_to_remove = Wishlist.query.filter_by(product_link=item_id, customer_link=current_user.id).first()

    if item_to_remove:
        try:
            db.session.delete(item_to_remove)
            db.session.commit()
            flash('Item removed from wishlist')
        except Exception as e:
            print('Item not removed from wishlist', e)
            flash('Failed to remove item from wishlist')

    return redirect(request.referrer)


@UserController.route('/wishlist')
@login_required
def show_wishlist():
    wishlist_items = Wishlist.query.filter_by(customer_link=current_user.id).all()
    return render_template('wishlist.html', wishlist=wishlist_items)