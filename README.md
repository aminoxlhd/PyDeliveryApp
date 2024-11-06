# PyDeliveryApp

PyDeliveryApp is a web application for restaurant and menu management, allowing users to search for different restaurants, view menus, place orders, and leave reviews.

## Features

- **User Authentication**: Supports account registration, login, and logout.
- **Restaurant Management**: Displays a list of restaurants, with options to add, edit, or delete (admin only).
- **Menu Management**: Shows the menu for each restaurant with options to edit and delete menu items.
- **Orders**: Allows users to create and view orders.
- **Reviews**: Users can leave reviews on menu items and view others' reviews.
- **Notifications**: Shows notifications for recent orders and reviews.

## Requirements

- Python 3.10 or higher
- Node.js and npm (for the frontend)

## Installation

### 1. Backend Setup (Flask)

1. **Install Packages**:
   ```bash
   pip install -r requirements.txt
Initialize Database:

bash

flask db init
flask db migrate -m "Initial migration"
flask db upgrade
Run the Application:

bash
flask run
2. Frontend Setup (React)
Install Packages:

bash
cd client
npm install
Run the Frontend:

bash
npm start
Usage
Run both the backend and frontend servers. The app will be accessible in the browser at http://localhost:3000 for the frontend, and the backend can run on http://localhost:5000.
Technologies Used
Backend: Flask, SQLAlchemy, Flask-Login
Frontend: React, TypeScript, Bootstrap
Contributions
Contributions to this project are welcome! Feel free to open new issues on GitHub or create pull requests to help improve the project.

Notes
Make sure to include a .env file for sensitive variables, such as SECRET_KEY.
Consider setting up security configurations such as SSL when deploying the application.
Copyright © 2024 PyDeliveryApp. All rights reserved.

sql

You can further customize the details if necessary. Let me know if there are any specific changes you'd like!