import unittest
import json
from app import app, init_db_from_file

class TestAPI(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        # Initialize DB for testing
        with app.app_context():
            init_db_from_file()

    def get_token(self):
        response = self.client.post('/login', json={'username': 'admin', 'password': 'admin'})
        return json.loads(response.data)['access_token']

    def test_login_success(self):
        response = self.client.post('/login', json={'username': 'admin', 'password': 'admin'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data)

    def test_login_failure(self):
        response = self.client.post('/login', json={'username': 'wrong', 'password': 'wrong'})
        self.assertEqual(response.status_code, 401)

    def test_get_products_json(self):
        token = self.get_token()
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.get('/products', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('products', data)
        self.assertIsInstance(data['products'], list)

    def test_get_products_xml(self):
        token = self.get_token()
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.get('/products?format=xml', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/xml', response.headers['Content-Type'])

    def test_create_product(self):
        token = self.get_token()
        headers = {'Authorization': f'Bearer {token}'}
        data = {'name': 'Test Product', 'price': 99.99}
        response = self.client.post('/products', json=data, headers=headers)
        self.assertEqual(response.status_code, 201)
        resp_data = json.loads(response.data)
        self.assertIn('id', resp_data)

    def test_create_product_validation_error(self):
        token = self.get_token()
        headers = {'Authorization': f'Bearer {token}'}
        data = {'name': '', 'price': -10}
        response = self.client.post('/products', json=data, headers=headers)
        self.assertEqual(response.status_code, 400)

    def test_get_product(self):
        token = self.get_token()
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.get('/products/11', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('id', data)
        self.assertIn('name', data)
        self.assertIn('price', data)

    def test_get_product_not_found(self):
        token = self.get_token()
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.get('/products/9999', headers=headers)
        self.assertEqual(response.status_code, 404)

    def test_update_product(self):
        token = self.get_token()
        headers = {'Authorization': f'Bearer {token}'}
        data = {'name': 'Updated Product', 'price': 199.99}
        response = self.client.put('/products/11', json=data, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_update_product_not_found(self):
        token = self.get_token()
        headers = {'Authorization': f'Bearer {token}'}
        data = {'name': 'Updated Product', 'price': 199.99}
        response = self.client.put('/products/9999', json=data, headers=headers)
        self.assertEqual(response.status_code, 404)

    def test_delete_product(self):
        token = self.get_token()
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.delete('/products/11', headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_delete_product_not_found(self):
        token = self.get_token()
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.delete('/products/9999', headers=headers)
        self.assertEqual(response.status_code, 404)

    def test_search_products(self):
        token = self.get_token()
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.get('/products?search=laptop', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('products', data)
        # Assuming 'laptop' exists in the data

    def test_unauthorized_access(self):
        response = self.client.get('/products')
        self.assertEqual(response.status_code, 401)

    def test_invalid_format(self):
        token = self.get_token()
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.get('/products?format=invalid', headers=headers)
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
