from flask import Flask, render_template, redirect, url_for, flash, current_app, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import User, Restaurant, MenuItem, Order, Review, Notification
from forms import RegistrationForm, LoginForm, ReviewForm
from forms import OrderForm
from extensions import db, migrate, login_manager
import os
import email_validator
from werkzeug.security import generate_password_hash, check_password_hash
from flask import abort
from functools import wraps
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pydeliveryapp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)
migrate.init_app(app, db)
with app.test_request_context():
    db.create_all()
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

        notification = Notification(
            user_id=order.user_id,
            message=f'تم تحديث حالة طلبك رقم {order.id} إلى: {new_status}'
        )
        db.session.add(notification)
        db.session.commit()

        flash(f'تم تحديث حالة الطلب إلى: {new_status}', 'success')
    else:
        flash('الحالة غير صالحة', 'danger')

    return redirect(url_for('admin_dashboard'))



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


@app.route('/search')
def search():
    query = request.args.get('query', '')
    sort_by = request.args.get('sort_by', 'name')

    if sort_by == 'price':
        menu_items = MenuItem.query.filter(MenuItem.name.contains(query)).order_by(MenuItem.price).all()
    elif sort_by == 'rating':
        menu_items = MenuItem.query.filter(MenuItem.name.contains(query)).order_by(MenuItem.rating.desc()).all()
    else:
        menu_items = MenuItem.query.filter(MenuItem.name.contains(query)).order_by(MenuItem.name).all()

    restaurants = Restaurant.query.filter(Restaurant.name.contains(query)).all()
    return render_template('search_results.html', menu_items=menu_items, restaurants=restaurants, query=query, sort_by=sort_by)



@app.context_processor
def inject_unread_notifications():
    if current_user.is_authenticated:
        unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        return dict(unread_notifications=unread_count)
    return dict(unread_notifications=0)


def save_image(image_file):
    filename = secure_filename(image_file.filename)
    image_path = os.path.join(current_app.root_path, 'static/images', filename)
    image_file.save(image_path)
    return f'images/{filename}'

@app.route('/add_restaurant', methods=['GET', 'POST'])
@login_required
def add_restaurant():
    form = RestaurantForm()
    if form.validate_on_submit():
        image_url = save_image(form.image.data) if form.image.data else None
        new_restaurant = Restaurant(name=form.name.data, address=form.address.data, image_url=image_url)
        db.session.add(new_restaurant)
        db.session.commit()
        flash('تم إضافة المطعم بنجاح!', 'success')
        return redirect(url_for('home'))
    return render_template('add_restaurant.html', form=form)

@app.route('/add_menu_item', methods=['GET', 'POST'])
@login_required
def add_menu_item():
    form = MenuItemForm()
    if form.validate_on_submit():
        image_url = save_image(form.image.data) if form.image.data else None
        new_menu_item = MenuItem(name=form.name.data, price=form.price.data, restaurant_id=form.restaurant_id.data, image_url=image_url)
        db.session.add(new_menu_item)
        db.session.commit()
        flash('تم إضافة الطبق بنجاح!', 'success')
        return redirect(url_for('home'))
    return render_template('add_menu_item.html', form=form)


@app.route('/edit_restaurant/<int:restaurant_id>', methods=['GET', 'POST'])
@login_required
def edit_restaurant(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    form = RestaurantForm(obj=restaurant)

    if form.validate_on_submit():
        restaurant.name = form.name.data
        restaurant.address = form.address.data
        if form.image.data:
            restaurant.image_url = save_image(form.image.data)
        db.session.commit()
        flash('تم تعديل المطعم بنجاح!', 'success')
        return redirect(url_for('home'))

    return render_template('edit_restaurant.html', form=form, restaurant=restaurant)


@app.route('/delete_restaurant/<int:restaurant_id>', methods=['POST'])
@login_required
def delete_restaurant(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    db.session.delete(restaurant)
    db.session.commit()
    flash('تم حذف المطعم بنجاح!', 'success')
    return redirect(url_for('home'))


@app.route('/edit_menu_item/<int:menu_item_id>', methods=['GET', 'POST'])
@login_required
def edit_menu_item(menu_item_id):
    menu_item = MenuItem.query.get_or_404(menu_item_id)
    form = MenuItemForm(obj=menu_item)

    if form.validate_on_submit():
        menu_item.name = form.name.data
        menu_item.price = form.price.data
        if form.image.data:
            menu_item.image_url = save_image(form.image.data)
        db.session.commit()
        flash('تم تعديل الطبق بنجاح!', 'success')
        return redirect(url_for('restaurant_menu', restaurant_id=menu_item.restaurant_id))

    return render_template('edit_menu_item.html', form=form, menu_item=menu_item)


@app.route('/delete_menu_item/<int:menu_item_id>', methods=['POST'])
@login_required
def delete_menu_item(menu_item_id):
    menu_item = MenuItem.query.get_or_404(menu_item_id)
    db.session.delete(menu_item)
    db.session.commit()
    flash('تم حذف الطبق بنجاح!', 'success')
    return redirect(url_for('restaurant_menu', restaurant_id=menu_item.restaurant_id))


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

        notification = Notification(
            user_id=current_user.id,
            message=f"تم إضافة تقييم جديد في {restaurant.name}."
        )
        db.session.add(notification)
        db.session.commit()

        flash('تمت إضافة تقييمك بنجاح!', 'success')
        return redirect(url_for('view_restaurants'))

    return render_template('add_review.html', form=form, restaurant=restaurant)


@app.route('/notifications')
@login_required
def notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.date_created.desc()).all()
    return render_template('notifications.html', notifications=notifications)

@app.route('/notifications/read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_as_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id == current_user.id:
        notification.is_read = True
        db.session.commit()
    return redirect(url_for('notifications'))


@app.before_request
def load_notifications():
    if current_user.is_authenticated:
        unread_notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        g.unread_notifications = unread_notifications
    else:
        g.unread_notifications = 0


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)

    if form.validate_on_submit():
        if form.email.data != current_user.email:
            current_user.email = form.email.data
            flash('تم تحديث البريد الإلكتروني بنجاح', 'success')

        if form.password.data:
            current_user.password = generate_password_hash(form.password.data)
            flash('تم تحديث كلمة المرور بنجاح', 'success')

        db.session.commit()
        return redirect(url_for('profile'))

    return render_template('profile.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
