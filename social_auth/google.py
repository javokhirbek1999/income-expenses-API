from google.auth.transport import requests
from google.oauth2 import id_token


class Google:
	""" class to fetch user info and return it using google oath """

	@staticmethod
	def validate(auth_token):
		"""
		Queries the Google oAUTH2 api to fetch user info and validate it
		"""

		try:
			id_info = id_token.verify_oauth2_token(auth_token,requests.Request())
			if 'accounts.google.com' in id_info['iss']:
				return id_info
		except Exception as e:
			return 'Token is either invalid or expired'