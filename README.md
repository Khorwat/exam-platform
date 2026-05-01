# Online Examination Platform

A comprehensive Django-based online examination platform for educational institutions, featuring secure exam delivery, automated grading, and performance analytics.

## Documentation

- [**User Guide**](docs/USER_GUIDE.md): For Students and Instructors.
- [**Developer Guide**](docs/DEVELOPER_GUIDE.md): For Developers (Scripts, Testing, Workflow).

## Features

- **User Management**: Role-based access control (Student, Instructor, Administrator)
- **Question Bank**: Support for multiple question types (MCQ, True/False, Short Answer)
- **Exam Management**: Create, schedule, and manage exams with flexible configuration
- **Secure Examination**: Time-limited exams with anti-cheating measures
- **Automated Grading**: Instant grading for objective questions
- **Analytics Dashboard**: Performance tracking and statistics
- **Notifications**: Exam schedule and result notifications
- **RESTful API**: Complete API for frontend integration
- **Responsive Design**: Mobile-friendly interface

## Technology Stack

- **Backend**: Django 4.2, Django REST Framework
- **Database**: PostgreSQL
- **Cache**: Redis
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Deployment**: Docker, Nginx, Gunicorn

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker and Docker Compose (for containerized deployment)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd CODES
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database and other settings
   ```

5. **Set up database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

### Docker Deployment

1. **Build and start containers**
   ```bash
   docker-compose up -d --build
   ```

2. **Run migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```

3. **Access the application**
   - Frontend: http://localhost
   - API: http://localhost/api/
   - Admin: http://localhost/admin/

## Project Structure

```
.
├── accounts/          # User management and authentication
├── questions/         # Question bank management
├── exams/             # Exam creation and scheduling
├── examinations/      # Exam-taking engine
├── results/           # Grading and analytics
├── notifications/     # Notification system
├── exam_platform/     # Main Django project settings
├── templates/         
│   └── frontend/      # Frontend HTML templates
├── static/            # Static files (CSS, JS)
├── docs/              # Detailed documentation
├── manage.py          # Django management script
├── requirements.txt   # Python dependencies
├── Dockerfile         # Docker configuration
├── docker-compose.yml # Docker Compose configuration
└── nginx.conf         # Nginx configuration
```

## API Documentation

API documentation is available at `/api/docs/` when the server is running.

### Authentication

All API endpoints (except registration and login) require JWT authentication:

```bash
# Login
POST /api/auth/login/
{
    "username": "student",
    "password": "password123"
}

# Use token in subsequent requests
Authorization: Bearer <access_token>
```

### Key Endpoints

- **Authentication**: `/api/auth/`
- **Questions**: `/api/questions/`
- **Exams**: `/api/exams/`
- **Examinations**: `/api/examinations/`
- **Results**: `/api/results/`
- **Notifications**: `/api/notifications/`

## Security Features

- JWT-based authentication
- Role-based access control
- Rate limiting on API endpoints
- IP address tracking for exam sessions
- Time limit enforcement
- Session security checks
- CSRF protection
- XSS prevention
- SQL injection prevention (Django ORM)

## Testing

Run tests with:

```bash
python manage.py test
```

Or with coverage:

```bash
coverage run --source='.' manage.py test
coverage report
```

## Configuration

Key settings in `exam_platform/settings.py`:

- Database configuration
- Redis cache settings
- JWT token lifetime
- CORS settings
- Security settings
- Static/media file handling

## Deployment

### Production Checklist

1. Set `DEBUG = False` in settings
2. Configure `ALLOWED_HOSTS`
3. Set up SSL/TLS certificates
4. Configure secure database credentials
5. Set up proper backup strategy
6. Configure email settings for notifications
7. Set up monitoring and logging
8. Configure firewall rules

### Environment Variables

Required environment variables (see `.env.example`):

- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (False in production)
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: Database settings
- `REDIS_HOST`, `REDIS_PORT`: Redis settings
- `EMAIL_*`: Email configuration (optional)

## Usage

### For Students

1. Register/Login to the platform
2. View scheduled exams on dashboard
3. Start and take exams
4. View results and performance

### For Instructors/Administrators

1. Create question bank with categories
2. Create exams and assign questions
3. Schedule exams with start/end dates
4. View analytics and results
5. Manage users and permissions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## License

This project is developed for educational purposes.

## Support

For issues and questions, please contact the development team.

## Future Enhancements

- Mobile application (iOS/Android)
- Advanced AI-based proctoring
- Integration with university systems
- Multi-language support
- Advanced analytics with machine learning
- Programming question support
- File upload questions

# exam-platform
# exam-platform
