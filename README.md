# Airport Flight Management API

REST API for managing airport flights, crews, airplanes and bookings.

## Features

- Manage airports, routes, flights, crews, and airplanes
- Book flight tickets with seat validation
- Check available seats on flights (custom action)
- JWT authentication
- Swagger API documentation

## Installation

### 1. Clone repository
```bash
git clone https://github.com/Grzechu700/airport-flight-management-API.git
cd airport-flight-management-API
```

### 2. Initialize project
```bash
make init
```

This will create `.env` file from `.env.sample`. Update it with your database credentials.

### 3. Setup virtual environment
```bash
python -m venv venv
source venv/Scripts/activate  # Windows Git Bash
make install
```

### 4. Setup database

Create PostgreSQL database `airport_db`, then update `.env` with your credentials.

### 5. Run migrations
```bash
make migrate
python manage.py createsuperuser
```

### 6. Run development server
```bash
make run
```

Visit `http://127.0.0.1:8000/api/doc/` for API documentation.

## Authentication

Get JWT token:
```bash
POST /api/user/token/
{
  "username": "your_username",
  "password": "your_password"
}
```

Use token in headers:
```
Authorization: Bearer <your_token>
```

## API Endpoints

### Public (Read-only)
- `GET /api/airports/` - List airports
- `GET /api/airplane-types/` - List airplane types
- `GET /api/crews/` - List crew members
- `GET /api/airplanes/` - List airplanes
- `GET /api/routes/` - List routes
- `GET /api/flights/` - List flights
- `GET /api/flights/{id}/available_seats/` - Check available seats

### Authenticated
- `POST /api/booking/orders/` - Create order
- `POST /api/booking/tickets/` - Book ticket

## Database Schema

![Database Schema](airport_diagram.png)

## Screenshots

### Swagger Documentation
![Swagger](screenshots/swagger.png)

### Flights Endpoint
![Flights](screenshots/flights.png)

### Available Seats Endpoint (custom action)
![Available seats](screenshots/available_seats.png)

## Running Tests

### Run all tests locally:
```bash
python manage.py test
```

### Run tests in Docker:
```bash
docker-compose run app sh -c "python manage.py test"
```

### Run specific test:
```bash
python manage.py test airport.tests.AirportAPITest
```

## Technologies

- Django 5.2
- Django REST Framework
- PostgreSQL
- JWT Authentication
- drf-spectacular