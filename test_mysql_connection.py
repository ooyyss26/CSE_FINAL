import os
import urllib.parse as urlparse
import MySQLdb

# Set the same DATABASE_URL as in app.py
os.environ['DATABASE_URL'] = 'mysql://root:password@localhost:3306/mydb'

def _parse_database_url():
    url = os.environ.get('DATABASE_URL') or os.environ.get('DB_URL')
    if not url:
        return None
    return urlparse.urlparse(url)

def test_mysql_connection():
    try:
        parsed = _parse_database_url()
        if not parsed:
            print("❌ DATABASE_URL not set")
            return False

        user = parsed.username
        password = parsed.password
        host = parsed.hostname
        port = parsed.port or 3306
        dbname = (parsed.path or '').lstrip('/')

        print(f"🔍 Testing connection to MySQL...")
        print(f"   Host: {host}")
        print(f"   Port: {port}")
        print(f"   User: {user}")
        print(f"   Database: {dbname}")

        # Try to connect
        conn = MySQLdb.connect(
            host=host,
            user=user,
            passwd=password,
            db=dbname,
            port=port,
            charset='utf8'
        )

        # Test the connection
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"✅ MySQL connection successful!")
        print(f"   MySQL Version: {version[0]}")

        # Check if products table exists
        cursor.execute("SHOW TABLES LIKE 'products'")
        table_exists = cursor.fetchone()
        if table_exists:
            print("✅ Products table exists")
            # Count records
            cursor.execute("SELECT COUNT(*) FROM products")
            count = cursor.fetchone()[0]
            print(f"   Records in products table: {count}")
        else:
            print("⚠️  Products table does not exist")

        conn.close()
        return True

    except MySQLdb.Error as e:
        print(f"❌ MySQL connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_mysql_connection()
