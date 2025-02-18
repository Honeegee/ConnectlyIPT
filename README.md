# Connectly API

A Django REST Framework API with enhanced security features and design patterns, utilizing Django's built-in User model for authentication and authorization.

## Features

### Authentication & User Management
- Uses Django's built-in User model (`django.contrib.auth.models.User`)
- Secure password hashing with Argon2
- Token-based authentication
- User roles and permissions

- Full CRUD operations for Posts and Comments
- Role-Based Access Control (RBAC)
- Token-based authentication
- Password encryption
- SSL/HTTPS support
- Design Patterns:
  - Singleton Pattern (Configuration & Logging)
  - Factory Pattern (Post Creation)

## Setup

1. Create and activate virtual environment:
```bash
python -m venv env
source env/Scripts/activate  # Windows
source env/bin/activate     # Unix or MacOS
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create superuser:
```bash
python manage.py createsuperuser
```

5. Run with SSL:
```bash
python manage.py runserver_plus --cert-file cert.pem --key-file key.pem
```

## API Endpoints

### Authentication & Users
- `POST /api/users/` - Create user (uses Django's User model)
- `POST /api/login/` - Login and get token
- Fields available:
  * username (required)
  * email (required)
  * password (hashed using Argon2)
  * date_joined (automatic)

### Posts
- `GET /api/posts/` - List all posts
- `POST /api/posts/` - Create post
- `GET /api/posts/{id}/` - Get specific post
- `PUT /api/posts/{id}/` - Update post (author only)
- `DELETE /api/posts/{id}/` - Delete post (author only)

### Comments
- `GET /api/comments/` - List all comments
- `POST /api/comments/` - Create comment
- `GET /api/comments/{id}/` - Get specific comment
- `PUT /api/comments/{id}/` - Update comment (author only)
- `DELETE /api/comments/{id}/` - Delete comment (author only)

## Security Features

1. HTTPS Support
2. Token Authentication
3. Password Hashing
4. Role-Based Access Control
5. Input Validation
6. Secure Cookie Handling

## Models

### User Model
- Django's built-in User model provides:
  * Username and password authentication
  * Email field
  * User permissions
  * Groups for role-based access
  * Admin interface integration

### Post Model
- Foreign Key to User model (author)
- Post types: text, image, video
- Metadata handling
- Author-only permissions

### Comment Model
- Foreign Key to User model (author)
- Foreign Key to Post model
- Author-only permissions

## Design Patterns

### Singleton Pattern
- ConfigManager: Centralized configuration
- LoggerSingleton: Centralized logging

### Factory Pattern
- PostFactory: Creates different types of posts (text, image, video)
- Handles validation and metadata requirements
