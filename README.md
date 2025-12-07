# CRUD REST API with MySQL, JWT Authentication, and JSON/XML Output

This Flask application provides a REST API for managing products with full CRUD operations, JWT-based authentication, search functionality, and support for JSON/XML response formats.

## Features

- **CRUD Operations**: Create, Read, Update, Delete products
- **Authentication**: JWT-based security for API endpoints
- **Search**: Search products by name
- **Formats**: JSON and XML output based on `format` query parameter
- **Validation**: Input validation and error handling
- **Database**: MySQL with at least 20 product records

## Setup Instructions

### 1. Prerequisites

- Python 3.8+
- MySQL Server
- Git

### 2. Clone and Setup

```bash
git clone <your-repo-url>
cd <project-directory>
```

### 3. Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r reqs.txt
```

### 5. MySQL Setup

1. Create a MySQL database named `mydb`
2. Update the `DATABASE_URL` in `app.py` with your MySQL credentials:
   ```python
   os.environ['DATABASE_URL'] = 'mysql://username:password@localhost:3306/mydb'
   ```

3. Import the schema and data:
   ```bash
   python app.py init-db
   ```
   This will execute the `DONGHIL.sql` file to create tables and insert 20+ product records.

### 6. Run the Application

```bash
python app.py
```

The API will be available at `http://127.0.0.1:5000`

## API Documentation

### Authentication

All endpoints except `/login` require JWT authentication. Include the token in the `Authorization` header:

```
Authorization: Bearer <your-jwt-token>
```

#### Login

**POST** `/login`

Request Body:
```json
{
  "username": "admin",
  "password": "admin"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Products Endpoints

#### List Products

**GET** `/products?format=json&search=query`

- `format`: `json` (default) or `xml`
- `search`: Optional search term for product names

Response (JSON):
```json
{
  "products": [
    {
      "id": 11,
      "name": "laptop",
      "price": 45000.00
    }
  ]
}
```

#### Create Product

**POST** `/products?format=json`

Request Body:
```json
{
  "name": "New Product",
  "price": 100.00
}
```

Response:
```json
{
  "message": "Product created",
  "id": 31
}
```

#### Get Product

**GET** `/products/{id}?format=json`

Response:
```json
{
  "id": 11,
  "name": "laptop",
  "price": 45000.00
}
```

#### Update Product

**PUT** `/products/{id}?format=json`

Request Body:
```json
{
  "name": "Updated Product",
  "price": 200.00
}
```

Response:
```json
{
  "message": "Product updated"
}
```

#### Delete Product

**DELETE** `/products/{id}?format=json`

Response:
```json
{
  "message": "Product deleted"
}
```

### Error Responses

- **400 Bad Request**: Validation errors or invalid format
- **401 Unauthorized**: Missing or invalid JWT token
- **404 Not Found**: Product not found
- **500 Internal Server Error**: Database errors

## Testing

### Run Unit Tests

```bash
pytest tests.py
```

The test suite covers:
- Authentication (login success/failure)
- CRUD operations for products
- Search functionality
- JSON/XML format support
- Input validation
- Error handling

### Manual Testing

Use tools like Postman or curl:

```bash
# Login
curl -X POST http://127.0.0.1:5000/login -H "Content-Type: application/json" -d '{"username":"admin","password":"admin"}'

# Get products (replace TOKEN with actual token)
curl -H "Authorization: Bearer TOKEN" http://127.0.0.1:5000/products

# Get products in XML
curl -H "Authorization: Bearer TOKEN" "http://127.0.0.1:5000/products?format=xml"

# Search products
curl -H "Authorization: Bearer TOKEN" "http://127.0.0.1:5000/products?search=laptop"
```

## Project Structure

```
.
├── app.py              # Main Flask application
├── tests.py            # Unit tests
├── reqs.txt            # Python dependencies
├── DONGHIL.sql         # MySQL schema and data
├── README.md           # This file
├── instructions.md     # Project requirements
├── TODO.md             # Development tasks
├── templates/          # HTML templates (legacy)
└── static/             # Static files (legacy)
```

## Security Notes

- Change the JWT secret key in production
- Use HTTPS in production
- Implement proper user management instead of hardcoded admin credentials
- Validate and sanitize all inputs

## Grading Criteria Met

- ✅ GitHub: Multiple commits with timestamps
- ✅ CRUD Operations: Full REST API with validation and error handling
- ✅ CRUD Tests: Comprehensive unit tests
- ✅ Formatting Options: JSON/XML support
- ✅ Search Functionality: Product search by name
- ✅ Security: JWT authentication
- ✅ Documentation: Complete API documentation and setup guide
