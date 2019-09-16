#!/usr/bin/env python
from datetime import datetime, timedelta
import unittest
from app import create_app, db
#from app.models import User
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

#    def test_avatar(self):
#        u = User(username='john', email='john@example.com')
#        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
#                                         'd4c74594d841139328695756648b6bd6'
#                                         '?d=identicon&s=128'))
#
#
#        # check the followed posts of each user
#        f1 = u1.followed_posts().all()
#        f2 = u2.followed_posts().all()
#        f3 = u3.followed_posts().all()
#        f4 = u4.followed_posts().all()
#        self.assertEqual(f1, [p2, p4, p1])
#        self.assertEqual(f2, [p2, p3])
#        self.assertEqual(f3, [p3, p4])
#        self.assertEqual(f4, [p4])


if __name__ == '__main__':
    unittest.main(verbosity=2)
