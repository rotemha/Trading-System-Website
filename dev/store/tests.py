from unittest import skip

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

from store.models import Store, Item
from tests.mainTest import MyUnitTesting


class StoreUnitTesting(MyUnitTesting):
	def setUp(self) -> None:
		super().setUp()
		self.login(user=self.default_user, password=self.default_password)

	def test_add_store(self):
		store_name = "check"
		self.assertFalse(Store.objects.filter(name=store_name).exists())
		self.driver.get(self.live_server_url + "/store/add_store/")
		self.driver.find_element_by_id("id_name").send_keys(store_name)
		element = self.driver.find_element_by_id("id_description")
		element.send_keys("bli bli bli")
		element.submit()
		self.assertTrue(Store.objects.filter(name=store_name).exists())

	def test_add_item_to_store(self):
		item_name = "qwe"
		self.driver.get(self.live_server_url + "/store/add_item_to_store/" + str(self.store.id) + "/")
		self.driver.find_element_by_id("id_name").send_keys(item_name)
		self.driver.find_element_by_id("id_description").send_keys("This is a description")
		element = self.driver.find_element_by_id("id_price")
		element.clear()
		element.send_keys("3.14")
		element.submit()
		self.assertTrue(Item.objects.filter(name=item_name).exists())

	@skip("Implementation still not fully ready")
	def test_update_store(self):
		self.driver.get(self.live_server_url + "/store/update/" + str(self.store.id) + "/")
		element = self.driver.find_element_by_id("id_name")
		element.send_keys("qwer")
		element.submit()
		not_finished = True

	def test_delete_store(self):
		self.assertTrue(Store.objects.filter(name=self.default_store).exists())
		self.driver.get(self.live_server_url + "/store/view_store/")
		self.driver.find_element_by_id("delete " + str(self.store.id)).submit()
		self.driver.find_element_by_name("csrfmiddlewaretoken").submit()
		self.assertFalse(Store.objects.filter(name=self.default_store).exists())

	def test_add_manager_to_store(self):
		new_user = 'user_to_manager'
		self.driver.get(self.live_server_url + "/store/add_manager_to_store/" + str(self.store.id) + '/')
		user = User.objects.create(username=new_user, password=make_password(self.default_password))
		self.driver.find_element_by_id('id_user_name').send_keys(new_user)
		element = self.driver.find_element_by_id("id_permissions_0")
		element.click()
		element.submit()
		self.assertTrue(user.has_perm('ADD_ITEM', self.store))
