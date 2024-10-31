from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import User, Restaurant, MenuItem, Order, Review
from forms import RegistrationForm, LoginForm, ReviewForm
from forms import OrderForm
from extensions import db, migrate, login_manager
import os
import email_validator
from werkzeug.security import generate_password_hash, check_password_hash
from flask import abort
from functools import wraps


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pydeliveryapp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)
migrate.init_app(app, db)
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    restaurants = Restaurant.query.all()
    return render_template('home.html', restaurants=restaurants)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        #hashed_password = generate_password_hash(form.password.data, method='sha256')
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('تم تسجيل حسابك بنجاح!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('تم تسجيل الدخول بنجاح!', 'success')
            return redirect(url_for('home'))
        else:
            flash('البريد الإلكتروني أو كلمة المرور خاطئة.', 'danger')

    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم تسجيل الخروج بنجاح.', 'success')
    return redirect(url_for('home'))

@app.route('/restaurant/<int:restaurant_id>')
def restaurant_menu(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    menu_items = MenuItem.query.filter_by(restaurant_id=restaurant.id).all()
    reviews = DishReview.query.filter_by(menu_item_id=menu_item.id).all()
    return render_template('restaurant_menu.html', restaurant=restaurant, menu_items=menu_items)


@app.route('/order/<int:menu_item_id>', methods=['POST'])
@login_required
def order(menu_item_id):
    menu_item = MenuItem.query.get_or_404(menu_item_id)
    new_order = Order(
        user_id=current_user.id,
        restaurant_id=menu_item.restaurant_id,
        items=menu_item.name,
        total_price=menu_item.price,
        status='Pending'
    )
    db.session.add(new_order)
    db.session.commit()
    flash('تم إنشاء الطلب بنجاح!', 'success')
    return redirect(url_for('home'))

@app.route('/orders')
@login_required
def orders():
    user_orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template('orders.html', orders=user_orders)


@app.route('/add_to_order/<int:menu_item_id>', methods=['POST'])
@login_required
def add_to_order(menu_item_id):
    menu_item = MenuItem.query.get(menu_item_id)
    if menu_item:
        order = Order(user_id=current_user.id, restaurant_id=menu_item.restaurant_id, items=menu_item.name,
                      total_price=menu_item.price, status='Pending')
        db.session.add(order)
        db.session.commit()
        flash('تمت إضافة الطبق إلى الطلبات بنجاح!', 'success')
    else:
        flash('الطبق غير موجود', 'danger')

    return redirect(url_for('view_restaurants'))


@app.route('/orders', methods=['GET'])
@login_required
def view_orders():
    orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template('orders.html', orders=orders)


@app.route('/restaurant/<int:restaurant_id>/review', methods=['GET', 'POST'])
@login_required
def add_review(restaurant_id):
    form = ReviewForm()
    restaurant = Restaurant.query.get_or_404(restaurant_id)

    if form.validate_on_submit():
        review = Review(
            rating=form.rating.data,
            comment=form.comment.data,
            user_id=current_user.id,
            restaurant_id=restaurant_id
        )
        db.session.add(review)
        db.session.commit()
        flash('تمت إضافة تقييمك بنجاح!', 'success')
        return redirect(url_for('view_restaurants'))

    return render_template('add_review.html', form=form, restaurant=restaurant)


@app.route('/restaurants', methods=['GET'])
def view_restaurants():
    restaurants = Restaurant.query.all()
    reviews = Review.query.all()
    return render_template('restaurants.html', restaurants=restaurants, reviews=reviews)


@app.route('/update_order_status/<int:order_id>', methods=['POST'])
@login_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')

    if new_status in ['في الانتظار', 'قيد التحضير', 'تم التوصيل']:
        order.status = new_status
        db.session.commit()
        flash(f'تم تحديث حالة الطلب إلى: {new_status}', 'success')
    else:
        flash('الحالة غير صالحة', 'danger')

    return redirect(url_for('view_orders'))


@app.route('/menu_item/<int:menu_item_id>/review', methods=['GET', 'POST'])
@login_required
def add_dish_review(menu_item_id):
    form = DishReviewForm()
    menu_item = MenuItem.query.get_or_404(menu_item_id)

    if form.validate_on_submit():
        dish_review = DishReview(
            rating=form.rating.data,
            comment=form.comment.data,
            user_id=current_user.id,
            menu_item_id=menu_item_id
        )
        db.session.add(dish_review)
        db.session.commit()
        flash('تمت إضافة تقييمك للطبق بنجاح!', 'success')
        return redirect(url_for('restaurant_menu', restaurant_id=menu_item.restaurant_id))

    return render_template('add_dish_review.html', form=form, menu_item=menu_item)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@app.route('/admin')
@admin_required
def admin_dashboard():
    users = User.query.all()
    orders = Order.query.all()
    reviews = Review.query.all()
    return render_template('admin_dashboard.html', users=users, orders=orders, reviews=reviews)


@app.route('/admin/delete_order/<int:order_id>', methods=['POST'])
@admin_required
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    flash('تم حذف الطلب بنجاح!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_review/<int:review_id>', methods=['POST'])
@admin_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    flash('تم حذف التقييم بنجاح!', 'success')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)

