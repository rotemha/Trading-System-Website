import json
from decimal import Decimal
from unittest import skip, expectedFailure

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db import DataError

from store.models import Store
from tests.mainTest import MyUnitTesting
from trading_system import service


def user_with_default_password_generator():
	user_num = 0
	while True:
		yield User.objects.create(username="new_user%d" % user_num,
		                          password=make_password(MyUnitTesting.default_password))
		user_num += 1


def store_generator():
	store_num = 0
	while True:
		user_pk = yield
		yield service.open_store("bla%d" % store_num, "blabla", user_pk)
		store_num += 1


class TestTradingSystem(MyUnitTesting):
	generate_user_with_default_password = user_with_default_password_generator()
	generate_store1 = store_generator()

	@classmethod
	def generate_store(cls, user):
		next(cls.generate_store1)
		return cls.generate_store1.send(user.pk)

	@skip("Not ready")
	def test_admin_register(self):  # 1.1-1
		pass

	@skip("Not ready")
	def test_admin_register_failed_username_or_password(self):  # 1.1-2
		pass

	@skip("Not ready")
	def test_admin_register_failed_money_collector(self):  # 1.1-3
		pass

	@skip("Not ready")
	def test_admin_register_failed_supply_system(self):  # 1.1-4
		pass

	@skip("Not ready")
	def test_admin_register_failed_supply_system(self):  # 1.1-5
		pass

	@skip("Not ready")
	def test_guest_register_none_existing_user(self):  # 2.2-1
		pass

	@skip("Not ready")
	def test_guest_register_with_existing_user(self):  # 2.2-2
		pass

	@skip("Not ready")
	def test_guest_register_none_existing_user_illegal_password(self):  # 2.2-3
		pass

	@skip("Not ready")
	def test_guest_login_with_existing_user(self):  # 2.3-1
		pass

	@skip("Not ready")
	def test_guest_login_none_existing_user(self):  # 2.3-2
		pass

	@skip("Not ready")
	def test_guest_login_with_existing_user_illegal_password(self):  # 2.3-3
		pass

	@skip("Not ready")
	def test_member_login(self):  # 2.3-4
		pass

	def test_search_by_name_fur_shampoo_exists(self):  # 2.5-1
		service.add_item_to_store(json.dumps({"price": 12.34,
		                                      "name": "fur shampoo",
		                                      "description": "This is a fur shampoo",
		                                      "category": "HOME",
		                                      "quantity": 12}), self.store.pk, self.user.pk)
		self.assertTrue(list(service.search("fur shampoo")))

	@skip("Not relevant")
	def test_search_with_empty_field(self):  # 2.5-2
		pass

	def test_search_none_existing_item(self):  # 2.5-3...
		self.assertFalse(list(service.search("A none relevant item")))

	@skip("Not ready: missing function related to cart in service")
	def test_member_adds_to_empty_cart_an_existing_product(self):  # 2.6-1...
		service.add_item_to_store(json.dumps({"price": 12.34,
		                                      "name": "fur shampoo 2",
		                                      "description": "This is a fur shampoo 2",
		                                      "category": "HOME",
		                                      "quantity": 12}), self.store.pk, self.user.pk)
		self.login(self.default_user, self.default_password)

	@skip("Not ready: can't buy item at all")
	def test_buy_existing_item(self):  # 2.8.1-1
		pass

	@skip("Not ready: can't buy item at all")
	def test_buy_existing_item_x2_but_only_exists_1_in_inventory(self):  # 2.8.1-2...
		pass

	@skip("Can't check if user is logged in (probably only through request")
	def test_member_logout(self):  # 3.1-1...
		pass

	def test_store_owner_adds_item_to_store(self):  # 4.1.1-1
		self.assertTrue(self.user.groups.filter(name='store_owners').exists())
		item_name = "fur shampoo 3"
		self.assertFalse(self.store.items.filter(name=item_name).exists())
		output = service.add_item_to_store(json.dumps({"price": 12.34,
		                                               "name": item_name,
		                                               "description": "This is a %s" % item_name,
		                                               "category": "HOME",
		                                               "quantity": 12}), self.store.pk, self.user.pk)
		self.assertTrue(self.store.items.filter(name=item_name).exists())

	def test_not_store_owner_adds_item_to_store(self):  # 4.1.1-2
		user = next(self.generate_user_with_default_password)
		self.assertFalse(user.groups.filter(name='store_owners').exists())
		item_name = "fur shampoo 4"
		self.assertFalse(self.store.items.filter(name=item_name).exists())
		service.add_item_to_store(json.dumps({"price": 12.34,
		                                      "name": item_name,
		                                      "description": "This is a %s" % item_name,
		                                      "category": "HOME",
		                                      "quantity": 12}), self.store.pk, user.pk)
		self.assertFalse(self.store.items.filter(name=item_name).exists())

	@skip("Not relevant")
	def test_store_owner_adds_already_existing_item_to_store(self):  # 4.1.1
		self.assertTrue(self.user.groups.filter(name='store_owners').exists())
		item_name: str = "fur shampoo 5"
		self.assertFalse(self.store.items.filter(name=item_name).exists())
		service.add_item_to_store(json.dumps({"price": 12.34,
		                                      "name": item_name,
		                                      "description": "This is a %s" % item_name,
		                                      "category": "HOME",
		                                      "quantity": 12}), self.store.pk, self.user.pk)
		self.assertTrue(self.store.items.filter(name=item_name).exists())
		service.add_item_to_store(json.dumps({"price": 12.34,
		                                      "name": item_name,
		                                      "description": "This is a %s" % item_name,
		                                      "category": "HOME",
		                                      "quantity": 12}), self.store.pk, self.user.pk)

	def test_adding_item_with_negative_quantity(self):  # 4.1.1-5
		self.assertTrue(self.user.groups.filter(name='store_owners').exists())
		item_name = "fur shampoo 6"
		self.assertFalse(self.store.items.filter(name=item_name).exists())
		with self.assertRaises(DataError):
			service.add_item_to_store(json.dumps({"price": 12.34,
			                                      "name": item_name,
			                                      "description": "This is a %s" % item_name,
			                                      "category": "HOME",
			                                      "quantity": -12}), self.store.pk, self.user.pk)
		self.assertFalse(self.store.items.filter(name=item_name).exists())

	@expectedFailure
	def test_adding_item_with_float_quantity(self):  # 4.1.1-6
		self.assertTrue(self.user.groups.filter(name='store_owners').exists())
		item_name = "fur shampoo 7"
		self.assertFalse(self.store.items.filter(name=item_name).exists())
		# with self.assertRaises(DataError):
		service.add_item_to_store(json.dumps({"price": 12.34,
		                                      "name": item_name,
		                                      "description": "This is a %s" % item_name,
		                                      "category": "HOME",
		                                      "quantity": 0.3}), self.store.pk, self.user.pk)

		self.assertFalse(self.store.items.filter(name=item_name).exists())

	def test_delete_existing_item_by_owner(self):  # 4.1.2-1
		user = next(self.generate_user_with_default_password)
		self.assertFalse(user.groups.filter(name='store_owners').exists())
		item_name = "fur shampoo 4"
		self.assertFalse(self.store.items.filter(name=item_name).exists())
		service.add_item_to_store(json.dumps({"price": 12.34,
		                                      "name": item_name,
		                                      "description": "This is a %s" % item_name,
		                                      "category": "HOME",
		                                      "quantity": 12}), self.store.pk, self.user.pk)
		added_items = self.store.items.filter(name=item_name)
		self.assertTrue(added_items.exists())
		service.delete_item(added_items[0].pk, self.user.pk)
		self.assertFalse(added_items.exists())

	def test_delete_none_existing_item(self):  # 4.1.2-2
		user = next(self.generate_user_with_default_password)
		self.assertFalse(user.groups.filter(name='store_owners').exists())
		self.assertFalse(service.delete_item(999, self.user.pk)[0])

	def test_delete_existing_item_by_none_owner(self):  # 4.1.2-3
		user = next(self.generate_user_with_default_password)
		self.assertFalse(user.groups.filter(name='store_owners').exists())
		item_name = "fur shampoo 5"
		self.assertFalse(self.store.items.filter(name=item_name).exists())
		service.add_item_to_store(json.dumps({"price": 12.34,
		                                      "name": item_name,
		                                      "description": "This is a %s" % item_name,
		                                      "category": "HOME",
		                                      "quantity": 12}), self.store.pk, self.user.pk)
		added_items = self.store.items.filter(name=item_name)
		self.assertTrue(added_items.exists())
		service.delete_item(added_items[0].pk, user.pk)
		self.assertTrue(added_items.exists())

	def test_edit_an_existing_item_by_owner(self):  # 4.1.3-1
		item_name = "fur shampoo 6"
		self.assertFalse(self.store.items.filter(name=item_name).exists())
		service.add_item_to_store(json.dumps({"price": 12.34,
		                                      "name": item_name,
		                                      "description": "This is a %s" % item_name,
		                                      "category": "HOME",
		                                      "quantity": 12}), self.store.pk, self.user.pk)
		added_items = self.store.items.filter(name=item_name)
		self.assertTrue(added_items.exists())
		service.update_item(added_items[0].pk, {"quantity": 99}, self.user.pk)
		self.assertEqual(added_items[0].quantity, 99)

	def test_edit_an_existing_item_by_none_owner(self):  # 4.1.3-2
		user = next(self.generate_user_with_default_password)
		item_name = "fur shampoo 7"
		self.assertFalse(self.store.items.filter(name=item_name).exists())
		service.add_item_to_store(json.dumps({"price": 12.34,
		                                      "name": item_name,
		                                      "description": "This is a %s" % item_name,
		                                      "category": "HOME",
		                                      "quantity": 12}), self.store.pk, self.user.pk)
		added_items = self.store.items.filter(name=item_name)
		self.assertTrue(added_items.exists())
		service.update_item(added_items[0].pk, {"quantity": 99}, user.pk)
		self.assertEqual(added_items[0].quantity, 12)

	def test_edit_an_none_existing_item_by_owner(self):  # 4.1.3-3
		self.assertFalse(service.update_item(666, {"quantity": 99}, self.user.pk)[0])

	def test_edit_an_existing_item_by_owner_with_negative_price(self):  # 4.1.3-4
		item_name = "fur shampoo 8"
		self.assertFalse(self.store.items.filter(name=item_name).exists())
		service.add_item_to_store(json.dumps({"price": 12.34,
		                                      "name": item_name,
		                                      "description": "This is a %s" % item_name,
		                                      "category": "HOME",
		                                      "quantity": 12}), self.store.pk, self.user.pk)
		added_items = self.store.items.filter(name=item_name)
		self.assertTrue(added_items.exists())
		service.update_item(added_items[0].pk, {"price": -5}, self.user.pk)
		self.assertEqual(added_items[0].price, 12.34)

	def test_edit_an_existing_item_by_owner_with_float_quantity(self):  # 4.1.3-5
		item_name = "fur shampoo 9"
		self.assertFalse(self.store.items.filter(name=item_name).exists())
		service.add_item_to_store(json.dumps({"price": 12.34,
		                                      "name": item_name,
		                                      "description": "This is a %s" % item_name,
		                                      "category": "HOME",
		                                      "quantity": 12}), self.store.pk, self.user.pk)
		added_items = self.store.items.filter(name=item_name)
		self.assertTrue(added_items.exists())
		service.update_item(added_items[0].pk, {"quantity": 20.5}, self.user.pk)
		self.assertEqual(added_items[0].quantity, 12)

	def test_add_owner_to_store(self):  # 4.3-1
		new_user = next(self.generate_user_with_default_password)
		self.assertFalse(service.get_user_store_list(new_user.pk))
		self.assertFalse(service.add_manager(new_user.username, [], True, self.store.pk, self.default_user, False)[0])
		self.assertTrue(service.get_user_store_list(new_user.pk))

	def test_add_owner_to_store_by_none_owner(self):  # 4.3-2
		new_user = next(self.generate_user_with_default_password)
		new_user2 = next(self.generate_user_with_default_password)
		self.assertFalse(service.get_user_store_list(new_user.pk))
		self.assertTrue(service.add_manager(new_user.username, [], True, self.store.pk, new_user2.username, False)[0])
		self.assertFalse(service.get_user_store_list(new_user.pk))

	def test_add_guest_to_store_by_store_owner(self):  # 4.3-3
		self.assertTrue(service.add_manager("Moshe", [], True, self.store.pk, self.default_user, False)[0])

	def test_make_reflexive_ownership(self):  # 4.3-2
		new_user = next(self.generate_user_with_default_password)
		self.assertFalse(service.get_user_store_list(new_user.pk))
		self.assertFalse(service.add_manager(new_user.username, [], True, self.store.pk, self.user.username, False)[0])
		self.assertTrue(service.get_user_store_list(new_user.pk))
		self.assertTrue(service.add_manager(self.user.username, [], True, self.store.pk, new_user.username, False)[0])

	def test_delete_owner_by_another_owner(self):  # 4.4-1
		new_user = next(self.generate_user_with_default_password)
		self.assertFalse(service.add_manager(new_user.username, [], True, self.store.pk, self.user.username, False)[0])
		self.assertTrue(service.remove_manager_from_store(self.store.pk, new_user.pk))

	@skip("chain of ownership doesn't implemented")
	def test_delete_first_owner_by_second_owner_that_didnt_ownered_the_first_owner(self):  # 4.4-2
		pass

	@skip("chain of ownership doesn't implemented")
	def test_delete_an_owner_by_none_owner(self):  # 4.4-3
		new_user = next(self.generate_user_with_default_password)
		new_user2 = next(self.generate_user_with_default_password)
		self.assertFalse(service.get_user_store_list(new_user.pk))
		self.assertTrue(service.add_manager(new_user.username, [], True, self.store.pk, self.user.username, False)[0])
		self.assertFalse(service.remove_manager_from_store(self.store.pk, new_user.pk))
		self.assertFalse(service.get_user_store_list(new_user.pk))

	@skip("chain of ownership doesn't implemented, not ready")
	def test_delete_a_none_owner_by_owner(self):  # 4.4-4
		new_user = next(self.generate_user_with_default_password)
		self.assertFalse(service.get_user_store_list(new_user.pk))

	def test_add_manager_with_edit_permission(self):  # 4.5-1
		store_pk = self.generate_store(self.user)
		new_user = next(self.generate_user_with_default_password)
		self.assertFalse(
			service.add_manager(new_user.username, [self.Perms.ADD_ITEM.value, self.Perms.EDIT_ITEM.value], False,
			                    store_pk,
			                    self.default_user, False)[0])
		self.assertTrue(new_user.has_perm(self.Perms.EDIT_ITEM.value, Store.objects.get(pk=store_pk)))

	def test_add_manager_by_none_owner(self):  # 4.5-2
		store_pk = self.generate_store(self.user)
		new_user = next(self.generate_user_with_default_password)
		new_user2 = next(self.generate_user_with_default_password)
		self.assertTrue(
			service.add_manager(new_user.username, [self.Perms.ADD_ITEM.value, self.Perms.EDIT_ITEM.value], False,
			                    store_pk,
			                    new_user2.username, False)[0])
		self.assertFalse(new_user.has_perm(self.Perms.EDIT_ITEM.value, Store.objects.get(pk=store_pk)))

	def test_add_manager_that_already_manages_the_store(self):  # 4.5-3
		store_pk = self.generate_store(self.user)
		new_user = next(self.generate_user_with_default_password)
		self.assertFalse(
			service.add_manager(new_user.username, [self.Perms.ADD_ITEM.value, self.Perms.EDIT_ITEM.value], False,
			                    store_pk,
			                    self.default_user, False)[0])
		self.assertTrue(new_user.has_perm(self.Perms.EDIT_ITEM.value, Store.objects.get(pk=store_pk)))
		self.assertTrue(
			service.add_manager(new_user.username, [self.Perms.ADD_ITEM.value, self.Perms.EDIT_ITEM.value], False,
			                    store_pk,
			                    self.default_user, False)[0])

	@skip("permission checking doesn't exist")
	def test_remove_manager(self):  # 4.6-1
		pass

	def test_delete_existing_item_by_manager(self):  # 5.1-1
		new_user = next(self.generate_user_with_default_password)
		self.assertFalse(
			service.add_manager(new_user.username, [self.Perms.REMOVE_ITEM.value], False,
			                    self.store.pk,
			                    self.default_user, False)[0])
		item_name = "bbb2"
		item_dict = {"price": 12.34,
		             "name": item_name,
		             "description": "This is a %s" % item_name,
		             "category": "HOME",
		             "quantity": 12}
		service.add_item_to_store(json.dumps(item_dict), self.store.pk, self.user.pk)
		self.assertEqual(item_dict["name"], service.get_store_items(self.store.pk)[0]["name"])
		self.assertTrue(service.delete_item(service.get_store_items(self.store.pk)[0]["id"], new_user.pk))
		self.assertFalse(service.get_store_items(self.store.pk))

	def test_delete_none_existing_item_by_manager(self):  # 5.1-2
		new_user = next(self.generate_user_with_default_password)
		self.assertFalse(
			service.add_manager(new_user.username, [self.Perms.REMOVE_ITEM.value], False,
			                    self.store.pk,
			                    self.default_user, False)[0])
		self.assertFalse(service.delete_item(666, new_user.pk)[0])

	def test_delete_existing_item_by_manager_without_permission(self):  # 5.1-3
		new_user = next(self.generate_user_with_default_password)
		self.assertFalse(
			service.add_manager(new_user.username, [self.Perms.ADD_ITEM.value], False,
			                    self.store.pk,
			                    self.default_user, False)[0])
		item_name = "bbb2"
		item_dict = {"price": 12.34,
		             "name": item_name,
		             "description": "This is a %s" % item_name,
		             "category": "HOME",
		             "quantity": 12}
		service.add_item_to_store(json.dumps(item_dict), self.store.pk, self.user.pk)
		self.assertEqual(item_dict["name"], service.get_store_items(self.store.pk)[0]["name"])
		self.assertFalse(service.delete_item(service.get_store_items(self.store.pk)[0]["id"], new_user.pk)[0])
		self.assertTrue(service.get_store_items(self.store.pk))

	def test_delete_existing_item_by_member(self):  # 5.1-4
		new_user = next(self.generate_user_with_default_password)
		item_name = "bbb2"
		item_dict = {"price": 12.34,
		             "name": item_name,
		             "description": "This is a %s" % item_name,
		             "category": "HOME",
		             "quantity": 12}
		service.add_item_to_store(json.dumps(item_dict), self.store.pk, self.user.pk)
		self.assertEqual(item_dict["name"], service.get_store_items(self.store.pk)[0]["name"])
		self.assertFalse(service.delete_item(service.get_store_items(self.store.pk)[0]["id"], new_user.pk)[0])
		self.assertTrue(service.get_store_items(self.store.pk))

	def test_buy_logic_all_ok(self):  # 7-1
		item_name = "fur shampoo 10"
		quantity = 12
		amount_to_buy = 6
		self.assertFalse(self.store.items.filter(name=item_name).exists())
		service.add_item_to_store(json.dumps({"price": 12.34,
		                                      "name": item_name,
		                                      "description": "This is a %s" % item_name,
		                                      "category": "HOME",
		                                      "quantity": quantity}), self.store.pk, self.user.pk)
		added_items = self.store.items.filter(name=item_name)
		self.assertTrue(added_items.exists())
		shipping_details = {'country': "Israel", 'city': "Nahariyya", 'zip': 2242676, 'address': "Blafour 113",
		                    'name': "Roy Ash"}
		card_details = {'card_number': "222", 'month': 6, 'year': 2020, 'holder': "Roy Ash", 'cvc': 234,
		                'id': 308007749}
		valid, total, total_after_discount, messages_ = service.buy_logic(pk=added_items[0].pk,
		                                                                  amount=amount_to_buy,
		                                                                  amount_in_db=added_items[0],
		                                                                  is_auth=self.user.is_authenticated,
		                                                                  username=self.user.username,
		                                                                  shipping_details=shipping_details,
		                                                                  card_details=card_details,
		                                                                  is_cart=False,
		                                                                  user_id=self.user)
		self.assertTrue(valid)
		self.assertEqual(total, Decimal(12.34 * amount_to_buy).quantize(Decimal('1.00')))
		self.assertEqual(added_items[0].quantity, quantity - amount_to_buy)

	def test_buy_logic_all_wrong_payment_info(self):  # 7-2
		item_name = "fur shampoo 11"
		quantity = 12
		amount_to_buy = 6
		self.assertFalse(self.store.items.filter(name=item_name).exists())
		service.add_item_to_store(json.dumps({"price": 12.34,
		                                      "name": item_name,
		                                      "description": "This is a %s" % item_name,
		                                      "category": "HOME",
		                                      "quantity": quantity}), self.store.pk, self.user.pk)
		added_items = self.store.items.filter(name=item_name)
		self.assertTrue(added_items.exists())
		shipping_details = {'country': "Israel", 'city': "Nahariyya", 'zip': 2242676, 'address': "Blafour 113",
		                    'name': "Roy Ash"}
		card_details = {'card_number': "222", 'month': -1, 'year': 0, 'holder': "", 'cvc': 0,
		                'id1': 308007749}

		valid, total, total_after_discount, messages_ = service.buy_logic(pk=added_items[0].pk,
		                                                                  amount=amount_to_buy,
		                                                                  amount_in_db=added_items[0],
		                                                                  is_auth=self.user.is_authenticated,
		                                                                  username=self.user.username,
		                                                                  shipping_details=shipping_details,
		                                                                  card_details=card_details,
		                                                                  is_cart=False,
		                                                                  user_id=self.user)
		self.assertFalse(valid)
		self.assertEqual(total, 0)
		self.assertEqual(added_items[0].quantity, quantity)
