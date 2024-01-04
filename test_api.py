# import unittest
# from flask_testing import TestCase
# from apps.app import create_app, g

# import apps.settings
# app = create_app()

# class TestApp(TestCase):
#     def create_app(self):
#         app.config['TESTING'] = True
#         app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
#         return app

#     def setUp(self):
#         g.db.create_all()

#     def tearDown(self):
#         g.db.session.remove()
#         g.db.drop_all()

#     def test_register_auth(self):
#         response = self.client.post('/register_auth', json={'username': 'testuser', 'password': 'testpassword'})
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('success', response.json['data'])

# if __name__ == '__main__':
#     unittest.main()