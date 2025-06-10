# Echo Backend

Echo is a backend service for a navigation application designed to assist blind users in navigating from one area to another, with additional supportive features such as learned routes and location memory. It is implemented using Django and Django REST Framework, providing a robust RESTful API for integration with mobile apps.

---

## ✨ Features

* User authentication and management
* Location-based navigation and route suggestions
* Learned route memory and personalized navigation
* User preferences storage and retrieval
* Dashboard with user-specific stats

---

## 📚 Technology Stack

* **Language:** Python 3
* **Framework:** Django, Django REST Framework
* **Database:** SQLite (default), configurable to PostgreSQL or others
* **Auth:** Token-based (likely JWT)

---

## ✅ Prerequisites

* Python 3.x
* `pip` for installing dependencies

---

## 📂 Installation

```bash
git clone https://github.com/MBinAsif/Echo_backend.git
cd Echo_backend
pip install -r requirements.txt
```

---

## 📊 Database Setup

Default: SQLite.
To set up the database:

```bash
python manage.py makemigrations
python manage.py migrate
```

To use PostgreSQL or another DB, make `.env`:

```# .env

DEBUG=True
SECRET_KEY= Django SECRET_KEY

DB_NAME=
DB_USER=myuser
DB_PASSWORD=mypassword
DB_HOST=localhost
DB_PORT=5432
```
To create Django SECRET_KEY 

In your terminal or Python shell:
```

python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

```
---

## 🚀 Running the Server

**Development:**

```bash
python manage.py runserver
```

**Production (example using Gunicorn):**

```bash
gunicorn echotrail_backend.wsgi:application --bind 0.0.0.0:8000
```

---

## 🔐 Environment Variables

| Variable                                                  | Description                          |
| --------------------------------------------------------- | ------------------------------------ |
| `SECRET_KEY`                                              | Django secret key                    |
| `DEBUG`                                                   | Set to `False` for production        |
| `DJANGO_SETTINGS_MODULE`                                  | Usually `echotrail_backend.settings` |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | For external DBs                     |

---

## 📄 API Documentation

### ✉️ Authentication

**POST /api/accounts/login/**

```json
{
  "username": "user1",
  "password": "pass123"
}
```

**Response:**

```json
{
  "access": "<jwt_token>",
  "refresh": "<refresh_token>"
}
```

### 🗺️ Navigation

**POST /api/navigation/route/**

```json
{
  "origin": {"lat": 40.7128, "lng": -74.0060},
  "destination": {"lat": 40.7306, "lng": -73.9352}
}
```

**Response:**

```json
{
  "route": [
    {"lat": 40.7128, "lng": -74.0060},
    {"lat": 40.7306, "lng": -73.9352}
  ],
  "instructions": [
    "Walk forward 200 meters",
    "Turn left on Elm St."
  ]
}
```

### 📈 Dashboard

**GET /api/dashboard/stats/**

```json
{
  "total_routes": 12,
  "favored_route": "Library Park Loop",
  "preferences": {"voice": "female", "units": "metric"}
}
```

---

## 📁 Project Structure

```
Echo_backend/
├── accounts/              # User auth and account APIs
├── dashboard/             # User dashboard APIs
├── navigation/            # Core navigation logic
├── echotrail_backend/     # Main project settings and URLs
├── manage.py              # Django project manager
├── requirements.txt       # Dependency list
├── learned_routes.pkl     # Pickled learned paths
├── location_memory.pkl    # Location memory file
├── user_preferences.json  # Default user preferences
```

---

## 🚚 Extra Features

* **Learned Routes:** `learned_routes.pkl` file contains serialized familiar paths.
* **Location Memory:** `location_memory.pkl` stores visited locations.
* **Preferences:** Default user preferences in JSON format.

---
To create admin user from shell 

```
python manage.py shell

Then Paste

from accounts.models import User
import bcrypt

# Create raw password
raw_password = 'admin123'

# Hash password using bcrypt
hashed_password = bcrypt.hashpw(
    raw_password.encode('utf-8'),
    bcrypt.gensalt()
).decode('utf-8')

# Create admin user
admin_user = User.objects.create(
    email='admin@example.com',
    name='Admin User',
    password=hashed_password,
    is_admin=True,
    status='active',
    is_staff=True,      # Allows access to Django admin
    is_superuser=True   # Gives full permissions
)

print(f"Admin user '{admin_user.email}' created successfully!")
```
---

---


## 💼 Contribution

Currently, no contribution guide is included. Fork the repo and create PRs if you’d like to contribute.

---

## 📅 License

No license file is included. Contact the repository owner for usage permissions.

---

## 🌐 Author

Developed by [MBinAsif](https://github.com/MBinAsif) for Echo — A navigation system to empower blind users.
