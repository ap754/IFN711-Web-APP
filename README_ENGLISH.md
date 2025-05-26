# Device Information Query and Prediction System

A Flask-based device information management system that allows users to log in, register, view, and add device details.

## Features

- User login and registration
- Device information display and search
- Add new device
- Supports exact purchase date or estimated date range

## Tech Stack

- Flask (Python Web framework)
- MySQL (Database)
- HTML/CSS
- Tailwind CSS (Styling utility)
- Font Awesome (Icons)

## Installation and Running

1. Ensure Python and MySQL are installed

2. Create MySQL database

```sql
CREATE DATABASE device_management;
```

3. Install required Python packages

```bash
pip install flask pymysql
```

4. Run the application

```bash
python app.py
```

5. Open your browser and visit http://127.0.0.1:5000

## Database Configuration

- Database name: device_management
- Username: root
- Password: 987654321

## Page Descriptions

1. Login Page - User login
2. Registration Page - New user registration
3. Device Information Page - Displays a list of devices with search support
4. Add Device Page - Add new device information
