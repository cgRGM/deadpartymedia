# Dead Party Media Backend

Django REST API backend for the Dead Party Media music blog platform.

## Features

- **Django Admin** with Jazzmin theming for content management
- **Django REST Framework** API with full CRUD operations
- **Django Allauth** for user authentication and social logins
- **PostgreSQL** database with proper models for articles, artists, events
- **AWS S3** integration for media file storage
- **Redis** caching and rate limiting
- **Email notifications** via Resend
- **SMS notifications** via Twilio
- **CKEditor** rich text editing for articles and events

## Tech Stack

- Django 5.1+
- Django REST Framework
- PostgreSQL
- Redis
- AWS S3
- UV (package manager)

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL
- Redis (optional, for caching)
- UV package manager

### Installation

1. **Install UV** (if not already installed):

   ```bash
   pip install uv
   ```

2. **Install dependencies**:

   ```bash
   cd apps/backend
   uv pip install -r pyproject.toml
   ```

3. **Set up environment variables**:

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run migrations**:

   ```bash
   python manage.py migrate
   ```

5. **Create superuser**:

   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**:
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/api/`
The admin panel will be available at `http://localhost:8000/admin/`

## Docker Development

For a complete development environment with PostgreSQL and Redis:

```bash
cd apps/backend
docker-compose up --build
```

## API Endpoints

### Public Endpoints

- `GET /api/articles/` - List articles
- `GET /api/articles/{id}/` - Article detail
- `GET /api/articles/featured/` - Featured article
- `GET /api/artists/` - List artists
- `GET /api/authors/` - List authors
- `GET /api/events/` - List events
- `GET /api/events/upcoming/` - Upcoming events
- `GET /api/events/past/` - Past events
- `POST /api/comments/` - Create comment (authenticated)
- `GET /api/health/` - Health check

### Admin Endpoints (Authenticated)

- `POST /api/admin/articles/` - Create article
- `PUT /api/admin/articles/{id}/` - Update article
- `POST /api/interview-requests/` - Create interview request

## Models

### Core Models

- **Article**: Blog posts with rich text content
- **Artist**: Music artists with social media links
- **Author**: Article writers
- **Event**: Music events and concerts
- **Comment**: User comments on articles
- **InterviewRequest**: Interview requests to artists

### Key Features

- Automatic email/SMS notifications for interview requests
- Featured article management (only one featured at a time)
- Rich text editing with CKEditor
- Image upload to S3
- User roles and permissions
- Social authentication (Google, Spotify)

## Environment Variables

See `.env.example` for all required environment variables.

## Development Commands

```bash
# Run development server
pnpm backend:dev

# Run migrations
pnpm backend:migrate

# Create migrations
pnpm backend:makemigrations

# Create superuser
pnpm backend:createsuperuser

# Django shell
pnpm backend:shell

# Collect static files
pnpm backend:collectstatic
```

## Deployment

The backend is configured for production deployment with:

- Gunicorn WSGI server
- Whitenoise for static files
- PostgreSQL database
- Redis caching
- AWS S3 media storage
- Security headers and HTTPS enforcement

## Contributing

1. Follow the existing code style
2. Write tests for new features
3. Update documentation as needed
4. Use proper commit messages following conventional commits
