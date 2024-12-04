This is a Django project that provides a platform for managing club bookings

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Yerassylzh/gamehub.git
cd gamehub
```

### 2. Create and Activate a Virtual Environment
#### On macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

#### On Windows
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up the Database and load fixtures
```bash
python manage.py migrate
python manage.py loaddata fixtures/data.json
```

### 5. Create a Superuser
#### Create an admin user to access the Django admin interface.
```bash
python manage.py createsuperuser
```

### 6. Environment Variables
#### Create .env file in the current directory
```bash
DJANGO_SECRET_KEY=<PUT HERE YOUR SECRET KEY>
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1, localhost
```

### 7. Run the Development Server
```bash
cd gamehub
python manage.py runserver
```

### 8. Access the Project
```bash
http://127.0.0.1:8000/
```