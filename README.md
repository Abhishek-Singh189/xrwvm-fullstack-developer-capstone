# xrwvm-fullstack-developer-capstone

## Project name

**Dealership Capstone Application**

This project is a full-stack dealership review application built with Django, React, Node.js, Express, MongoDB, and a Flask sentiment-analysis service.

## Features

- User registration, login, and logout
- Dealership listing and state filtering
- Dealer detail and review views
- Authenticated review submission
- Car make and model inventory
- Positive, neutral, and negative sentiment labels
- Django administration for car makes and models
- GitHub Actions CI for frontend builds and Django checks

## Repository structure

- `server/djangoapp` - Django application, APIs, models, and sentiment integration
- `server/djangoproj` - Django project configuration
- `server/frontend` - React application and Django static pages
- `server/database` - Express/MongoDB dealership API
- `.github/workflows/ci.yml` - GitHub Actions workflow

## Running locally

### Django server

```bash
cd server
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### React frontend

```bash
cd server/frontend
npm ci
npm start
```

### MongoDB dealership API

```bash
cd server/database
npm ci
npm start
```

The API uses `MONGO_URL` and defaults to `mongodb://localhost:27017/dealershipsDB`.

### Sentiment analyzer

```bash
cd server/djangoapp/microservices
pip install -r requirements.txt
python app.py
```

Configure the Django integration with `server/djangoapp/.env`:

```text
backend_url=http://localhost:3030
sentiment_analyzer_url=http://localhost:5000
```
