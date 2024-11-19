from flask import Flask, jsonify, send_from_directory
from flask_migrate import Migrate
from flask_login import login_user, login_required, logout_user, current_user
from models import User, Restaurant, MenuItem, Order, Review, Notification
from extensions import db, migrate, login_manager
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='client/build', static_url_path='/')
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pydeliveryapp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)

db.init_app(app)
migrate = Migrate(app, db, compare_type=True)
migrate.init_app(app, db)

login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/api/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    data = [
        {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address,
            "image_url": restaurant.image_url
        }
        for restaurant in restaurants
    ]
    return jsonify(data), 200

@app.route('/api/menu/<int:restaurant_id>', methods=['GET'])
def get_menu_items(restaurant_id):
    menu_items = MenuItem.query.filter_by(restaurant_id=restaurant_id).all()
    data = [
        {
            "id": item.id,
            "name": item.name,
            "price": item.price,
            "image_url": item.image_url
        }
        for item in menu_items
    ]
    return jsonify(data), 200

@app.route('/api/orders', methods=['GET'])
@login_required
def get_orders():
    orders = Order.query.filter_by(user_id=current_user.id).all()
    data = [
        {
            "id": order.id,
            "items": order.items,
            "total_price": order.total_price,
            "status": order.status
        }
        for order in orders
    ]
    return jsonify(data), 200

@app.route('/api/notifications', methods=['GET'])
@login_required
def get_notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.date_created.desc()).all()
    data = [
        {
            "id": notification.id,
            "message": notification.message,
            "is_read": notification.is_read,
            "date_created": notification.date_created
        }
        for notification in notifications
    ]
    return jsonify(data), 200

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('client/build/static', filename)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
