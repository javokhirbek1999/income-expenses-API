from django.urls import reverse

from rest_framework.test import APITestCase
from faker import Faker


class TestSetup(APITestCase):

	def setUp(self):
		self.register_url = reverse('register')
		self.login_url = reverse('login')

		self.faker = Faker()
		self.user_data = {
			'email': self.faker.email(),
			'username': self.faker.email().split('@')[0],
			'password': self.faker.email()
		}

	def tearDown(self):
		pass