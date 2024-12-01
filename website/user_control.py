from flask import Blueprint, render_template, flash, redirect, request, jsonify,session
from .classes import Product, Cart, Order
from flask_login import login_required, current_user
from . import db
from intasend import APIService
import json
UserController = Blueprint('UserController', __name__)

API_PUBLISHABLE_KEY = 'pk_test_51QQutyCYxENXdwFJ7AmTEV537FLWrPZyf12HnJekFGc1Bt1NNg5i90tVSaa9ZbNaocX89uAMGe9n3IlQq23OhaNW00xTeoFK4o'
API_TOKEN = 'sk_test_51QQutyCYxENXdwFJ2wgpp9k183dBnS0UrRy3MnJ9YVmgYFuZDqTfZ65WijziNUUy8E0EIojFcPnF25V3noUgKXXI00VoSQ6EZK'

@UserController.route('/')
def home():
    
    return render_template('home.html',session = session.get("user"), pretty = json.dumps(session.get("user"),
                                               indent = 4))