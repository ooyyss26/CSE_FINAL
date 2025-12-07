# Flask CRUD API with JWT Authentication and MySQL Database
# This application provides REST API endpoints for managing products with JWT-based authentication
# Supports JSON and XML response formats, search functionality, and a Bootstrap web UI

import os
import sys
import xml.etree.ElementTree as ET
from flask import Flask, g, request, jsonify, make_response, render_template
from flask_cors import CORS
import jwt
from datetime import datetime, timedelta, UTC
import re

# File paths
BASE_DIR = os.path.dirname(__file__)
SCHEMA_FILE = os.path.join(BASE_DIR, 'DONGHIL.sql')

# Flask app configuration
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing
app.config['JWT_SECRET_KEY'] = 'super-secret-key-change-in-production'  # Change in production!


# Database configuration
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'antonio123'
DB_NAME = 'mydb'
DB_PORT = 3306

# JWT Token Functions
def create_access_token(identity):
    """Create a JWT access token for the given user identity"""
    payload = {
        'identity': identity,
        'iat': datetime.now(UTC)  # Issued at time
    }
    token = jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')
    return token

def jwt_required(f):
    """Decorator to require JWT authentication for protected routes"""
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid token'}), 401
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            g.user = payload['identity']  # Store user identity in Flask g object
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper





class DB:
    def __init__(self, conn, db_type):
        self._conn = conn
        self._db_type = db_type

    def execute(self, sql, params=()):
        # adapt parameter style for non-sqlite DB-API drivers
        if self._db_type != 'sqlite':
            sql = sql.replace('?', '%s')
        cur = self._conn.cursor()
        cur.execute(sql, params)
        return cur

    def commit(self):
        self._conn.commit()

    def close(self):
        try:
            self._conn.close()
        except Exception:
            pass


def get_db():
    db_wrapper = getattr(g, '_database', None)
    if db_wrapper is not None:
        return db_wrapper

    try:
        import pymysql
    except Exception as e:
        raise RuntimeError('MySQL driver not installed. Install pymysql.') from e

    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT,
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor
    )
    db_wrapper = DB(conn, 'mysql')
    g._database = db_wrapper
    return db_wrapper


@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def _execute_statements_from_file(conn_wrapper, sql_text):
    # naive split on ';' to execute multiple statements for non-sqlite drivers
    statements = [s.strip() for s in sql_text.split(';') if s.strip()]
    for stmt in statements:
        conn_wrapper.execute(stmt)
    try:
        conn_wrapper.commit()
    except Exception:
        pass


def init_db_from_file(schema_path=SCHEMA_FILE):
    if not os.path.exists(schema_path):
        return False, f"Schema file not found: {schema_path}"
    db = get_db()
    with open(schema_path, 'r', encoding='utf-8') as f:
        sql = f.read()
    _execute_statements_from_file(db, sql)
    return True, "Initialized database from DONGHIL.sql"


def validate_product_data(data):
    """Validate product data for name and price fields"""
    errors = []
    if 'name' not in data or not isinstance(data['name'], str) or not data['name'].strip():
        errors.append('Name is required and must be a non-empty string')
    if 'price' not in data:
        errors.append('Price is required')
    else:
        try:
            price = float(data['price'])
            if price < 0:
                errors.append('Price must be a non-negative number')
        except (ValueError, TypeError):
            errors.append('Price must be a valid number')
    return errors


def dict_to_xml(data, root='response'):
    """Convert dictionary data to XML format"""
    def build_xml(element, data):
        if isinstance(data, dict):
            for key, value in data.items():
                sub = ET.SubElement(element, key)
                build_xml(sub, value)
        elif isinstance(data, list):
            for item in data:
                sub = ET.SubElement(element, 'item')
                build_xml(sub, item)
        else:
            element.text = str(data)
    root_element = ET.Element(root)
    build_xml(root_element, data)
    return ET.tostring(root_element, encoding='unicode')

def format_response(data, format_type='json'):
    """Format response as JSON or XML based on format_type parameter"""
    if format_type == 'xml':
        xml_data = dict_to_xml(data)
        response = make_response(xml_data)
        response.headers['Content-Type'] = 'application/xml'
        return response
    else:
        return jsonify(data)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    # Simple auth: username=admin, password=admin
    if username != 'admin' or password != 'admin':
        return jsonify({'error': 'Invalid credentials'}), 401
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200


# API Routes
@app.route('/products', methods=['GET', 'POST'])
@jwt_required
def products():
    """Handle product collection - GET lists all products (with optional search), POST creates new product"""
    format_type = request.args.get('format', 'json').lower()
    if format_type not in ['json', 'xml']:
        return format_response({'error': 'Invalid format. Use json or xml'}, format_type), 400

    db = get_db()
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return format_response({'error': 'JSON data required'}, format_type), 400
        errors = validate_product_data(data)
        if errors:
            return format_response({'error': 'Validation failed', 'details': errors}, format_type), 400
        try:
            cur = db.execute('INSERT INTO products (products_name, price) VALUES (%s, %s)', (data['name'], data['price']))
            db.commit()
            product_id = cur.lastrowid
            return format_response({'message': 'Product created', 'id': product_id}, format_type), 201
        except Exception as e:
            return format_response({'error': 'Database error', 'details': str(e)}, format_type), 500

    # GET /products
    search = request.args.get('search', '').strip()
    try:
        if search:
            # Search by name
            cur = db.execute('SELECT idproducts as id, products_name as name, price FROM products WHERE products_name LIKE %s ORDER BY idproducts', ('%' + search + '%',))
        else:
            cur = db.execute('SELECT idproducts as id, products_name as name, price FROM products ORDER BY idproducts')
        products_list = cur.fetchall()
        return format_response({'products': products_list}, format_type), 200
    except Exception as e:
        return format_response({'error': 'Database error', 'details': str(e)}, format_type), 500


@app.route('/products/<int:product_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required
def product(product_id):
    """Handle individual product operations - GET retrieves, PUT updates, DELETE removes"""
    format_type = request.args.get('format', 'json').lower()
    if format_type not in ['json', 'xml']:
        return format_response({'error': 'Invalid format. Use json or xml'}, format_type), 400

    db = get_db()
    if request.method == 'GET':
        try:
            cur = db.execute('SELECT idproducts as id, products_name as name, price FROM products WHERE idproducts = %s', (product_id,))
            product_data = cur.fetchone()
            if not product_data:
                return format_response({'error': 'Product not found'}, format_type), 404
            return format_response(product_data, format_type), 200
        except Exception as e:
            return format_response({'error': 'Database error', 'details': str(e)}, format_type), 500

    if request.method == 'PUT':
        data = request.get_json()
        if not data:
            return format_response({'error': 'JSON data required'}, format_type), 400
        errors = validate_product_data(data)
        if errors:
            return format_response({'error': 'Validation failed', 'details': errors}, format_type), 400
        try:
            cur = db.execute('UPDATE products SET products_name = %s, price = %s WHERE idproducts = %s', (data['name'], data['price'], product_id))
            if cur.rowcount == 0:
                return format_response({'error': 'Product not found'}, format_type), 404
            db.commit()
            return format_response({'message': 'Product updated'}, format_type), 200
        except Exception as e:
            return format_response({'error': 'Database error', 'details': str(e)}, format_type), 500

    if request.method == 'DELETE':
        try:
            cur = db.execute('DELETE FROM products WHERE idproducts = %s', (product_id,))
            if cur.rowcount == 0:
                return format_response({'error': 'Product not found'}, format_type), 404
            db.commit()
            return format_response({'message': 'Product deleted'}, format_type), 200
        except Exception as e:
            return format_response({'error': 'Database error', 'details': str(e)}, format_type), 500


if __name__ == '__main__':
    # Support `python app.py init-db` for convenience
    if len(sys.argv) > 1 and sys.argv[1] == 'init-db':
        with app.app_context():
            ok, msg = init_db_from_file()
            print(msg)
            sys.exit(0 if ok else 2)

    app.run(debug=True)
