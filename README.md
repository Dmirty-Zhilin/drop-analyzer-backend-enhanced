# Drop Analyzer Backend Enhanced

Enhanced version of the Drop Analyzer backend with the following features:

## New Features

### 🔐 Authentication & Authorization
- User registration and login with JWT tokens
- Role-based access control (user/admin)
- Secure password hashing
- Token blacklisting for logout

### 🗄️ Database Integration
- SQLAlchemy models for users, tasks, results, and reports
- MySQL/PostgreSQL support for Coolify deployment
- Database migrations with Flask-Migrate
- Proper relationships and constraints

### 🤖 AI Integration
- Thematic analysis of domains using AI
- Configurable AI analysis (can be enabled/disabled)
- Fallback mechanisms for AI service failures
- Extensible for different AI providers

### ✅ Domain Selection
- Checkbox functionality for individual domains
- Save selected domains as custom reports
- Bulk operations on selected domains
- Selection state persistence

### 📊 Enhanced Reports
- Save analysis results as named reports
- Public/private report sharing
- Multiple export formats (Excel, CSV, JSON, PDF)
- Report management and organization

### 👨‍💼 Admin Panel
- User management (view, edit, deactivate)
- Role assignment and permissions
- System statistics and monitoring
- Task management across all users

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/logout` - Logout user
- `GET /api/v1/auth/profile` - Get user profile
- `PUT /api/v1/auth/profile` - Update user profile

### Analysis
- `POST /api/v1/analysis/analyze` - Start domain analysis
- `GET /api/v1/analysis/tasks/{task_id}` - Get task status
- `GET /api/v1/analysis/tasks` - List user tasks
- `POST /api/v1/analysis/results/{task_id}/select` - Update domain selection
- `GET /api/v1/analysis/export/{task_id}` - Export results

### Reports
- `GET /api/v1/reports/` - List user reports
- `POST /api/v1/reports/` - Save new report
- `GET /api/v1/reports/{report_id}` - Get specific report
- `PUT /api/v1/reports/{report_id}` - Update report
- `DELETE /api/v1/reports/{report_id}` - Delete report
- `GET /api/v1/reports/public` - List public reports

### Admin (Admin only)
- `GET /api/v1/admin/users` - List all users
- `PUT /api/v1/admin/users/{user_id}/role` - Update user role
- `PUT /api/v1/admin/users/{user_id}/status` - Update user status
- `DELETE /api/v1/admin/users/{user_id}` - Delete user
- `GET /api/v1/admin/stats` - Get system statistics
- `GET /api/v1/admin/tasks` - List all tasks

## Database Schema

### Users
- id, username, email, password_hash
- role (user/admin), is_active, created_at, last_login

### Analysis Tasks
- id (UUID), user_id, task_name, status
- progress, current_domain, error_message
- domains_count, use_test_data, ai_analysis_enabled
- created_at, started_at, completed_at

### Domain Results
- id, task_id, domain_name
- Wayback Machine data (snapshots, intervals, etc.)
- AI analysis data (category, confidence, description)
- SEO metrics, assessment scores
- is_selected flag for checkboxes

### Reports
- id (UUID), user_id, task_id, name, description
- domains_data (JSON), is_public, created_at

## Environment Variables

```bash
# Database (for Coolify)
DB_HOST=localhost
DB_PORT=3306
DB_NAME=drop_analyzer
DB_USERNAME=root
DB_PASSWORD=password

# Security
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=jwt-secret-string-change-in-production

# AI Service (optional)
OPENAI_API_KEY=your-openai-api-key
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables in `.env` file

3. Initialize database:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

4. Run the application:
```bash
python src/main.py
```

## Default Admin User

The system creates a default admin user on first run:
- Email: admin@dropanalyzer.com
- Password: admin123
- Role: admin

**Important:** Change the default admin password in production!

## Deployment

The application is configured for deployment on Coolify with:
- MySQL database support
- Environment variable configuration
- CORS enabled for frontend integration
- Health check endpoint at `/api/v1/health`

## Security Features

- Password hashing with Werkzeug
- JWT token authentication
- Role-based access control
- CORS protection
- Input validation and sanitization
- SQL injection prevention with SQLAlchemy ORM

