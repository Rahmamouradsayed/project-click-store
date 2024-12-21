from flask import Blueprint, render_template, flash, redirect, request, jsonify,session, url_for
from .classes import Product, Cart, Order,Wishlist
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

@UserController.route('/search', methods=['POST', 'GET'])
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


@UserController.route('/add-to-cart/<int:item_id>', methods=['POST'])
@login_required
def add_to_cart(item_id):
    item_to_add = Product.query.get(item_id)
    item_exists = Cart.query.filter_by(product_id=item_id, customer_id=current_user.id).first()
    if item_exists:
        try:
            item_exists.quantity = item_exists.quantity + 1
            db.session.commit()
            flash(f' Quantity of { item_exists.product.product_name } has been updated')
            return redirect(request.referrer)
        except Exception as e:
            print('Quantity not Updated', e)
            flash(f'Quantity of { item_exists.product.product_name } not updated')
            return redirect(request.referrer)

    new_cart_item = Cart()
    new_cart_item.quantity = 1
    new_cart_item.product_id = item_to_add.id
    new_cart_item.customer_id = current_user.id

    try:
        db.session.add(new_cart_item)
        db.session.commit()
        flash(f'{new_cart_item.product.product_name} added to cart')
    except Exception as e:
        print('Item not added to cart', e)
        flash(f'{new_cart_item.product.product_name} has not been added to cart')

    return redirect(request.referrer)


@UserController.route('/cart')
@login_required
def show_cart():
    cart = Cart.query.filter_by(customer_id=current_user.id).all()
    return render_template('cart.html', cart=cart)


@UserController.route('/pluscart')
@login_required
def plus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        cart_item.quantity = cart_item.quantity + 1
        db.session.commit()

        cart = Cart.query.filter_by(customer_id=current_user.id).all()
        data = {
            'quantity': cart_item.quantity,
        }
        return jsonify(data)


@UserController.route('/minuscart')
@login_required
def minus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        cart_item.quantity = cart_item.quantity - 1
        db.session.commit()

        cart = Cart.query.filter_by(customer_id=current_user.id).all()
        data = {
            'quantity': cart_item.quantity,
        }
        return jsonify(data)


@UserController.route('removecart')
@login_required
def remove_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        db.session.delete(cart_item)
        db.session.commit()

        cart = Cart.query.filter_by(customer_id=current_user.id).all()
        data = {
            'quantity': cart_item.quantity,
        }

        return jsonify(data)



def get_cart_items(customer_id):
    items = db.session.query(Product, Cart.quantity).join(Product).filter(Cart.customer_id == customer_id).all()
    total_price = 0
    total_items = 0
    for product, quantity in items:
        total_price += product.current_price * quantity
        total_items += quantity
    return items , total_price , total_items


@UserController.route('/order_summary', methods=['GET', 'POST'])
@login_required
def order_summary():
    customer_id = current_user.id
    items, total_price , total_items = get_cart_items(customer_id)
    
    if items:
        return render_template('order_summary.html', items=items, total_price=total_price, total_items=total_items)
    else:
        flash("Your cart is empty")
        return redirect(url_for('UserController.show_cart')) 

@UserController.route('/place-order-btn', methods=['POST'])
@login_required
def place_order():
    customer_id = current_user.id
    items = db.session.query(Product, Cart.quantity).join(Product).filter(Cart.customer_id == customer_id).all()
    
    random_payment_id = random.randint(10000, 999999)
    if not items:
        flash("Your cart is empty.")
        return redirect(url_for('UserController.show_cart'))
    
    for product, quantity in items:
        if product.in_stock < quantity:
            flash(f"Product {product.product_name} is not in stock.")
            return redirect(url_for('UserController.show_cart'))
        
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


@UserController.route('/add_to_wishlist/<int:product_id>', methods=['POST'])
@login_required
def add_to_wishlist(product_id):
    try:
        existing_item = Wishlist.query.filter_by(customer_id=current_user.id, product_id=product_id).first()
        if not existing_item:
            new_item = Wishlist(customer_id=current_user.id, product_id=product_id)
            db.session.add(new_item)
            db.session.commit()
            flash('Product added to wishlist!', 'success') 
            return redirect(url_for('UserController.all_products')) 
        else:
            flash('This product is already in your wishlist.', 'info') 
            return redirect(url_for('UserController.wishlist')) 
    except Exception as e:
        flash(f'Error adding product to wishlist: {str(e)}', 'error')  
        return redirect(request.referrer) 


@UserController.route('/remove_from_wishlist/<int:product_id>', methods=['POST'])
@login_required
def remove_from_wishlist(product_id):
    try:
        item = Wishlist.query.filter_by(customer_id=current_user.id, product_id=product_id).first()
        if item:
            db.session.delete(item)
            db.session.commit()
            flash('Product removed from wishlist!', 'success')
            return redirect(request.referrer)
        else:
            flash('Product not found in your wishlist.', 'info')
            return redirect(request.referrer)
    except Exception as e:
        flash(f'Error removing product from wishlist: {str(e)}', 'error')
        return redirect(request.referrer)


@UserController.route('/wishlist')
@login_required
def wishlist():
    items = Wishlist.query.filter_by(customer_id=current_user.id).all()
    products = [item.product for item in items]
    return render_template('wishlist.html', products=products)

