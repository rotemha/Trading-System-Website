from enum import Enum

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from store.models import Store
from trading_system.service import open_store


class MyUnitTesting(StaticLiveServerTestCase):
	default_password = "q2w44r32c1"
	default_user = "qqq"
	default_store = "rrr"

	class Perms(Enum):
		ADD_ITEM = 'ADD_ITEM'
		REMOVE_ITEM = 'REMOVE_ITEM'
		EDIT_ITEM = "EDIT_ITEM"
		ADD_MANAGER = "ADD_MANAGER"
		REMOVE_STORE = "REMOVE_STORE"
		ADD_DISCOUNT = "ADD_DISCOUNT"
		ADD_RULE = "ADD_RULE"

	# @classmethod
	# def setUpClass(cls) -> None:
	# 	super().setUpClass()
	# 	cls.driver = webdriver.Chrome(ChromeDriverManager().install())
	#
	# @classmethod
	# def tearDownClass(cls) -> None:
	# 	cls.driver.close()
	# 	super().tearDownClass()

	def setUp(self) -> None:
		super().setUp()
		self.user = User.objects.create(username=self.default_user, password=make_password(self.default_password))
		self.store = Store.objects.get(pk=open_store(self.default_store, "bla bla bla", self.user.pk))

# @classmethod
# def login(cls, user: str, password: str) -> None:
# 	cls.driver.get(cls.live_server_url + "/accounts/login/")
# 	cls.driver.find_element_by_name("username").send_keys(user)
# 	element = cls.driver.find_element_by_name("password")
# 	element.send_keys(password)
# 	element.submit()
