# Create your tests here.
from django.contrib.auth.models import User

from tests.mainTest import MyUnitTesting


class AccountUnitTesting(MyUnitTesting):
	def test_signup(self):
		password = "q2w44r32c1"
		user = "silvFire"
		self.driver.get(self.live_server_url + "/accounts/signup/")
		self.driver.find_element_by_name("username").send_keys(user)
		self.driver.find_element_by_name("password1").send_keys(password)
		element = self.driver.find_element_by_name("password2")
		element.send_keys(password)
		element.submit()
		self.assertTrue(User.objects.filter(username=user).exists())

		self.driver.get(self.live_server_url + "/accounts/signup/")
		self.driver.find_element_by_name("username").send_keys(user)
		self.driver.find_element_by_name("password1").send_keys(password)
		element = self.driver.find_element_by_name("password2")
		element.send_keys(password)
		element.submit()
		self.assertTrue("A user with that username already exists." in self.driver.page_source)

	def test_login(self):
		self.login(user=self.default_user, password=self.default_password)
		# user1 = User.objects.filter(username=default_user)[0].is_authenticated
		self.assertTrue(User.objects.filter(username=self.default_user)[0].is_authenticated)
