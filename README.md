# Connectly API

A Django REST Framework API with enhanced security features and design patterns, including a modern frontend interface. Utilizes Django's built-in User model extended with custom UserProfile for enhanced user features.

## Features

### Authentication & User Management
- Uses Django's built-in User model with custom UserProfile extension
- OAuth2 integration with Google
- Secure password hashing with Argon2
- Token-based authentication
- User roles and permissions
- Profile customization (avatar, cover photo)

### Core Features
- Full CRUD operations for Posts and Comments
- Social features (Like, Follow)
- Role-Based Access Control (RBAC)
- Token-based authentication
- Password encryption
- SSL/HTTPS support
- Modern frontend templates
- Responsive design
- Real-time updates
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
- Media attachments
- Metadata handling
- Author-only permissions
- Like functionality
- Comment threading

### Comment Model
- Foreign Key to User model (author)
- Foreign Key to Post model
- Author-only permissions
- Like functionality

### UserProfile Model
- One-to-One with User model
- Customizable avatar
- Cover photo
- Bio and additional user info
- Follow functionality

### Like Model
- Generic foreign key (supports both posts and comments)
- User relationship tracking

### UserFollow Model
- Follower-Following relationship tracking
- User stats (followers count, following count)

## Design Patterns

### Singleton Pattern
- ConfigManager: Centralized configuration
- LoggerSingleton: Centralized logging

### Factory Pattern
- PostFactory: Creates different types of posts (text, image, video)
- Handles validation and metadata requirements
