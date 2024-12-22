from flask import Blueprint, render_template, flash, send_from_directory, redirect
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, FileField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange
from werkzeug.utils import secure_filename
from .classes import Product, Order, Customer
from . import db
import os

from flask import current_app

class ShopItemsForm(FlaskForm):
    product_name = StringField('Name of Product', validators=[DataRequired()])
    current_price = FloatField('Current Price', validators=[DataRequired()])
    previous_price = FloatField('Previous Price', validators=[DataRequired()])
    in_stock = IntegerField('In Stock', validators=[DataRequired(), NumberRange(min=0)])
    product_picture = FileField('Product Picture', validators=[DataRequired()])
    flash_sale = BooleanField('Flash Sale')
    category = SelectField('Category', choices=[
        ('accessories', 'Accessories'),
        ('womens_clothes', "Women's Clothing"),
        ('shoes', 'Shoes'),
    ], validators=[DataRequired()])
    add_product = SubmitField('Add Product')
    update_product = SubmitField('Update')


class OrderForm(FlaskForm):
    order_status = SelectField('Order Status', choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'),
                                                        ('Out for delivery', 'Out for delivery'),
                                                        ('Delivered', 'Delivered'), ('Canceled', 'Canceled')])
    update = SubmitField('Update Status')

admin = Blueprint('admin', __name__)


def get_images():
    image_folder = os.path.join(current_app.root_path, 'static', 'images')
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)
    images = [f for f in os.listdir(image_folder) if f.endswith(('jpg', 'jpeg', 'png'))]
    return images


@admin.route('/add-shop-items', methods=['GET', 'POST'])
@login_required
def add_shop_items():
    if current_user.id == 1:
        form = ShopItemsForm()

        image_list = get_images()

        if form.validate_on_submit():
            product_name = form.product_name.data
            current_price = form.current_price.data
            previous_price = form.previous_price.data
            in_stock = form.in_stock.data
            flash_sale = form.flash_sale.data

            file = form.product_picture.data

            
            file_name = secure_filename(file.filename)
            file_path = os.path.join('static', 'images', file_name)

            
            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))

            file.save(file_path)

            category = form.category.data  
            if not category:
                flash('Category must be selected.')
                return render_template('add_shop_items.html', form=form, images=image_list)

            new_shop_item = Product()
            new_shop_item.product_name = product_name
            new_shop_item.current_price = current_price
            new_shop_item.previous_price = previous_price
            new_shop_item.in_stock = in_stock
            new_shop_item.flash_sale = flash_sale
            new_shop_item.category = category  

            new_shop_item.product_picture = f'images/{file_name}'


            try:
                db.session.add(new_shop_item)
                db.session.commit()
                flash(f'{product_name} added Successfully')
                return redirect('/shop-items')
            except Exception as e:
                db.session.rollback()  
                flash(f'Error: {str(e)}')

        return render_template('add_shop_items.html', form=form, images=image_list)

    return render_template('404.html')




@admin.route('/shop-items', methods=['GET', 'POST'])
@login_required
def shop_items():
    if current_user.id == 1:
        items = Product.query.order_by(Product.date_added).all()
        return render_template('shop_items.html', items=items)
    return render_template('404.html')


@admin.route('/update-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def update_item(item_id):
    if current_user.id == 1:
        form = ShopItemsForm()

        item_to_update = Product.query.get(item_id)

        form.product_name.render_kw = {'placeholder': item_to_update.product_name}
        form.previous_price.render_kw = {'placeholder': item_to_update.previous_price}
        form.current_price.render_kw = {'placeholder': item_to_update.current_price}
        form.in_stock.render_kw = {'placeholder': item_to_update.in_stock}
        form.flash_sale.render_kw = {'placeholder': item_to_update.flash_sale}
        form.category.data = item_to_update.category  

        if form.validate_on_submit():
            product_name = form.product_name.data
            current_price = form.current_price.data
            previous_price = form.previous_price.data
            in_stock = form.in_stock.data
            flash_sale = form.flash_sale.data
            category = form.category.data  

            file = form.product_picture.data
            file_name = secure_filename(file.filename)

           
            if file:
                file_path = os.path.join('static', 'images', file_name)

                if not os.path.exists(os.path.dirname(file_path)):
                    os.makedirs(os.path.dirname(file_path))

                file.save(file_path)
                product_picture = f'images/{file_name}'  
            else:
                
                product_picture = item_to_update.product_picture

            try:
                Product.query.filter_by(id=item_id).update(dict(
                    product_name=product_name,
                    current_price=current_price,
                    previous_price=previous_price,
                    in_stock=in_stock,
                    flash_sale=flash_sale,
                    category=category,  
                    product_picture=product_picture  
                ))

                db.session.commit()
                flash(f'{product_name} updated Successfully')
                print('Product Updated')
                return redirect('/shop-items')
            except Exception as e:
                print('Product not Updated', e)
                flash('Item Not Updated!!!')

        return render_template('update_item.html', form=form)

    return render_template('404.html')


@admin.route('/delete-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def delete_item(item_id):
    if current_user.id == 1:
        try:
            item_to_delete = Product.query.get(item_id)
            db.session.delete(item_to_delete)
            db.session.commit()
            flash('One Item deleted')
            return redirect('/shop-items')
        except Exception as e:
            print('Item not deleted', e)
            flash('Item not deleted!!')
        return redirect('/shop-items')

    return render_template('404.html')


@admin.route('/view-orders')
@login_required
def order_view():
    if current_user.id == 1:
        orders = Order.query.all()
        return render_template('view_orders.html', orders=orders)
    return render_template('404.html')


@admin.route('/update-order/<int:order_id>', methods=['GET', 'POST'])
@login_required
def update_order(order_id):
    if current_user.id == 1:
        form = OrderForm()

        order = Order.query.get(order_id)

        if form.validate_on_submit():
            status = form.order_status.data
            order.status = status

            try:
                db.session.commit()
                flash(f'Order {order_id} Updated successfully')
                return redirect('/view-orders')
            except Exception as e:
                print(e)
                flash(f'Order {order_id} not updated')
                return redirect('/view-orders')

        return render_template('order_update.html', form=form)

    return render_template('404.html')


@admin.route('/category/<string:category>', methods=['GET'])
def category(category):
    category_map = {
        'accessories': 'Accessories',
        'womens_clothes': "Women's Clothing",
        'shoes': 'Shoes' 
    }
    category_name = category_map.get(category, 'Category')
    
    items = Product.query.filter_by(category=category).all()
    return render_template('category.html', items=items, category_name=category_name)


@admin.route('/customers')
@login_required
def display_customers():
    if current_user.id == 1:
        customers = Customer.query.all()
        return render_template('customers.html', customers=customers)
    return render_template('404.html')


@admin.route('/admin-page')
@login_required
def admin_page():
    if current_user.id == 1:
        return render_template('admin.html')
    return render_template('404.html')
