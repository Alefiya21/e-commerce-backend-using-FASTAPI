# E-commerce Backend API

A robust FastAPI-based e-commerce backend system with comprehensive features including authentication, product management, shopping cart, and order processing.

## Features

### 🔐 Authentication & User Management
- User signup/signin with JWT tokens
- Role-based access control (Admin/User)
- Password reset functionality with email integration
- Secure password hashing with bcrypt

### 📦 Product Management
- **Admin Features**: Full CRUD operations for products
- **Public Features**: Product listing, search, filtering, and detail views
- Category-based filtering and price range filtering

### 🛒 Shopping Cart
- Add/remove/update cart items
- Real-time stock validation
- Cart persistence per user

### 💳 Checkout & Orders
- Dummy payment processing
- Order creation with detailed line items
- Stock management during checkout
- Order history and detailed order views

### 🛡️ Security & Best Practices
- JWT-based authentication
- Input validation with Pydantic
- Comprehensive error handling
- Request/response logging
- SQL injection protection with SQLAlchemy ORM

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with PyJWT
- **Validation**: Pydantic schemas
- **Password Hashing**: bcrypt via passlib
- **Email**: SMTP integration for password reset
- **Migrations**: Alembic for database migrations

## Installation & Setup

### Prerequisites
- Python
- PostgreSQL database


### 1. Clone and Setup Environment

\`\`\`bash
# Create project directory
mkdir ecommerce-backend
cd ecommerce-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
\`\`\`

### 2. Database Setup

\`\`\`bash
# Create PostgreSQL database
createdb ecommerce_db

# Update DATABASE_URL in .env file
DATABASE_URL=postgresql://username:password@localhost:5432/ecommerce_db
\`\`\`

### 3. Environment Configuration

Create a `.env` file in the root directory:

\`\`\`env
DATABASE_URL=postgresql://username:password@localhost:5432/ecommerce_db
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
\`\`\`

### 4. Initialize Database with Alembic

\`\`\`bash
# Initialize Alembic (if not already done)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
\`\`\`

### 5. Seed Database with Sample Data

\`\`\`bash
# Run the seed script
python scripts/seed_data.py
\`\`\`

### 6. Run the Application

\`\`\`bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
\`\`\`

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /auth/signup` - User registration
- `POST /auth/signin` - User login
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password with token

### Admin Product Management
- `POST /admin/products` - Create product (Admin only)
- `GET /admin/products` - List all products with pagination (Admin only)
- `GET /admin/products/{id}` - Get product details (Admin only)
- `PUT /admin/products/{id}` - Update product (Admin only)
- `DELETE /admin/products/{id}` - Delete product (Admin only)

### Public Product APIs
- `GET /products` - List products with filters and pagination
- `GET /products/search` - Search products by keyword
- `GET /products/{id}` - Get product details

### Cart Management
- `POST /cart` - Add item to cart (User only)
- `GET /cart` - View cart (User only)
- `PUT /cart/{product_id}` - Update cart item quantity (User only)
- `DELETE /cart/{product_id}` - Remove item from cart (User only)

### Checkout & Orders
- `POST /checkout` - Process checkout (User only)
- `GET /orders` - Get order history (User only)
- `GET /orders/{order_id}` - Get order details (User only)

## Test Accounts

After running the seed script, you can use these test accounts:

- **Admin**: admin@example.com / admin123
- **User**: user@example.com / user123

## Testing

### Manual Testing with Postman

1. Import the API endpoints from the OpenAPI documentation at `/docs`
2. Sign in to get JWT tokens
3. Use the `access_token` in the Authorization header: `Bearer <token>`
4. Test all endpoints according to the role-based access control

### Automated Testing

\`\`\`bash
# Run all tests
python -m pytest app/tests/ -v

# Run specific test file
python -m pytest app/tests/test_auth.py -v

# Run with coverage
python -m pytest app/tests/ --cov=app --cov-report=html
\`\`\`

## Error Handling

All errors follow a consistent format:

\`\`\`json
{
  "error": true,
  "message": "Error description",
  "code": 400
}
\`\`\`

## Logging

The application logs:
- API access logs (IP, endpoint, method, response time)
- Authentication attempts
- Errors and exceptions
- Business logic events

Logs are written to both console and `app.log` file.

## Security Features

- Password hashing with bcrypt
- JWT token-based authentication
- Role-based access control
- Input validation and sanitization
- SQL injection protection
- CORS configuration
- Secure password reset tokens

## Database Migrations

\`\`\`bash
# Create new migration after model changes
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback to previous migration
alembic downgrade -1

# View migration history
alembic history
\`\`\`

## Production Deployment

For production deployment:

1. Use a production-grade WSGI server like Gunicorn:
   \`\`\`bash
   pip install gunicorn
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   \`\`\`

2. Set strong environment variables:
   - Generate a secure `SECRET_KEY`
   - Use production database credentials
   - Configure proper SMTP settings

3. Enable HTTPS and configure proper CORS origins

4. Set up database connection pooling and monitoring

5. Configure proper logging levels for production

## API Documentation

The API automatically generates interactive documentation:
- **Swagger UI**: http://localhost:8000/docs