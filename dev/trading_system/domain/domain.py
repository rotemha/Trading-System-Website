import datetime

from django.contrib.auth.models import User, Group
from guardian.shortcuts import assign_perm

from external_systems.money_collector.payment_system import Payment
from external_systems.supply_system.supply_system import Supply
from store.forms import AddManagerForm
from store.models import BaseRule, ComplexStoreRule, BaseItemRule, ComplexItemRule, Discount, Store, Item, \
	ComplexDiscount
from trading_system.domain.cart import Cart as c_Cart
from trading_system.domain.item import Item as c_Item
from trading_system.domain.store import Store as c_Store
from trading_system.domain.user import User as c_User
# from store.models import Item, BaseRule, ComplexStoreRule, BaseItemRule, ComplexItemRule, Discount
from trading_system.models import ObserverUser, NotificationUser, Notification
from trading_system.observer import ItemSubject

# import traceback

pay_system = Payment()
supply_system = Supply()

from store.models import WaitToAgreement, ManagersWhoWait


def add_manager(wanna_be_manager, picked, is_owner, store_pk, store_manager, is_partner):
	print('--------------------------------------------------------is_p----', is_partner)

	if not User.objects.get(username=store_manager).has_perm('ADD_MANAGER', Store.objects.get(id=store_pk)):
		return [True, "Store manager don't have the permission to add another manager"]
	messages_ = ''
	store = c_Store.get_store(store_id=store_pk)

	try:
		user_ = User.objects.get(username=wanna_be_manager)
	except:
		fail = True
		messages_ += 'no such user'
		return [fail, messages_]

	if wanna_be_manager == store_manager:
		fail = True
		messages_ += 'can`t add yourself as a manager!'
		return [fail, messages_]
	# messages.warning(request, 'can`t add yourself as a manager!')
	# return redirect('/store/home_page_owner/')
	pre_store_owners_ids = store.all_owners_ids()
	pre_store_managers_ids = store.all_managers_ids()
	pre_partners_ids = store.all_partners_ids()
	all_pre_m_o = pre_store_managers_ids + pre_store_owners_ids + pre_partners_ids

	# print('\n owners: ' ,pre_store_owners)
	for owner_id in all_pre_m_o:
		if c_User.get_user(user_id=owner_id).username == wanna_be_manager:
			fail = True
			messages_ += 'allready owner'
			return [fail, messages_]
	# messages.warning(request, 'allready owner')
	# return redirect('/store/home_page_owner/')

	if user_ is None:
		fail = True
		messages_ += 'No such user'
		return [fail, messages_]

	if (is_partner):

		all_partners = store.all_partners_ids()
		if (len(all_partners) > 1):  # there is other partner besids curr
			store_obj = Store.objects.get(id=store_pk)
			wanna_be_manager_user_obg = User.objects.get(username=wanna_be_manager)
			store_manager_user_obg = User.objects.get(username=store_manager)
			wait_obj = WaitToAgreement(user_to_wait=wanna_be_manager_user_obg, store=store_obj)
			wait_obj.save()
			for m_id in all_partners:
				pre_manager_user_obg = User.objects.get(id=m_id)
				m_obj = ManagersWhoWait(user_who_wait=pre_manager_user_obg)
				m_obj.save()
				wait_obj.managers_who_wait.add(m_obj)
			wait_obj_for_this_manager = wait_obj.managers_who_wait.get(
				user_who_wait=store_manager_user_obg)  # remove curr manager from wait list
			wait_obj.managers_who_wait.remove(wait_obj_for_this_manager)
			wait_obj.save()
			messages_ += ' . wait to approve partnership . '
			return [False, messages_]
		else:
			if approved_user_to_store_manager(wanna_be_manager, store_pk):
				return [False, 'approved']
			else:
				return [True, 'can`t complete']

	# messages.warning(request, 'No such user')
	# return redirect('/store/home_page_owner/')

	if is_partner or is_owner:
		for perm in list(AddManagerForm.CHOICES):
			store.assign_perm(perm=perm[0], user_id=user_.pk)
	else:
		for perm in picked:
			store.assign_perm(perm=perm, user_id=user_.pk)

	if is_owner:

		try:
			store_owners_group = Group.objects.get(name="store_owners")
			user_.groups.add(store_owners_group)
			# store_.owners.add(user_)
			store.add_owner(user_.pk)
			try:
				ObserverUser.objects.create(user_id=user_.pk,
				                            address="ws://127.0.0.1:8000/ws/store_owner/{}/".format(user_.pk)).save()
			except Exception as e:
				messages_ += str(e)

		except Exception as e:
			messages_ += str(e)
	else:
		try:
			store_managers = Group.objects.get_or_create(name="store_managers")[0]
			# store_managers = Group.objects.get(name="store_managers")
			user_.groups.add(store_managers)
			store.add_manager(user_.pk)
			try:
				ObserverUser.objects.create(user_id=user_.pk,
				                            address="ws://127.0.0.1:8000/ws/store_owner/{}/".format(user_.pk)).save()
			except Exception as e:
				messages_ += str(e)

		except Exception as e:
			messages_ += str(e)
			return [True, messages_]

	return [False, messages_]


def check_if_user_is_approved(user_id, store_id):
	user_ = User.objects.get(id=user_id)
	store = Store.objects.get(id=store_id)
	wait_to_agg_obj = WaitToAgreement.objects.get(user_to_wait=user_, store=store)
	managers_list = wait_to_agg_obj.managers_who_wait.all()
	for obj in managers_list:
		if not obj.is_approve:
			return False
	return True


def agreement_by_partner(partner_id, store_pk, user_pk):
	try:
		user = User.objects.get(id=user_pk)
		partner = User.objects.get(id=partner_id)
		store = Store.objects.get(id=store_pk)
		wait_to_agg_obj = WaitToAgreement.objects.get(user_to_wait=user, store=store)
		partner_wait_obg = wait_to_agg_obj.managers_who_wait.get(user_who_wait=partner)
		partner_wait_obg.is_approve = True
		partner_wait_obg.save()
		if (check_if_user_is_approved(user_pk, store_pk)):
			approved_user_to_store_manager(user.username, store_pk)
		wait_to_agg_obj.managers_who_wait.remove(partner_wait_obg)
		wait_to_agg_obj.save()
		return True
	except:
		return False


def get_all_wait_agreement_t_need_to_approve(manager_id):
	manager = User.objects.get(id=manager_id)
	return WaitToAgreement.objects.filter(managers_who_wait__user_who_wait__in=[manager])


def approved_user_to_store_manager(wanna_be_manager, store_pk):
	try:
		store_obj = Store.objects.get(id=store_pk)
		wanna_be_manager_user_obg = User.objects.get(username=wanna_be_manager)
		store_obj.owners.add(User.objects.get(pk=wanna_be_manager_user_obg.id))
		store_obj.partners.add(User.objects.get(pk=wanna_be_manager_user_obg.id))
		store_obj.save()
		my_group = Group.objects.get_or_create(name="store_owners")[0]
		# my_group = Group.objects.get(name="store_owners")
		try:
			if len(ObserverUser.objects.filter(user_id=wanna_be_manager_user_obg.pk)) == 0:
				ObserverUser.objects.create(user_id=wanna_be_manager_user_obg.pk,
				                            address="ws://127.0.0.1:8000/ws/store_owner/{}/".format(
					                            wanna_be_manager_user_obg.pk)).save()
		except:
			pass
		wanna_be_manager_user_obg.groups.add(my_group)
		assign_perm('ADD_ITEM', wanna_be_manager_user_obg, store_obj)
		assign_perm('REMOVE_ITEM', wanna_be_manager_user_obg, store_obj)
		assign_perm('EDIT_ITEM', wanna_be_manager_user_obg, store_obj)
		assign_perm('ADD_MANAGER', wanna_be_manager_user_obg, store_obj)
		assign_perm('REMOVE_STORE', wanna_be_manager_user_obg, store_obj)
		assign_perm('ADD_DISCOUNT', wanna_be_manager_user_obg, store_obj)
		assign_perm('ADD_RULE', wanna_be_manager_user_obg, store_obj)
		store_obj.save()
		try:
			approved_user = User.objects.get(username=wanna_be_manager)
			wait_ = WaitToAgreement.objects.filter(user_to_wait=approved_user, store=store_obj)
			wait_.delete()
		except:
			pass
		return True
	except:
		return False


def search(txt):
	return c_Item.search(txt=txt)


def open_store(store_name, desc, user_id):
	store = c_Store(name=store_name, desc=desc, owner_id=user_id)
	return store.pk


def add_base_rule_to_store(rule_type, store_id, parameter, user_id):
	if not User.objects.get(id=user_id).has_perm('ADD_RULE', Store.objects.get(pk=store_id)):
		return [False, "you don't have the permission to add base rule to store!"]

	if rule_type == 'MAX_QUANTITY' or rule_type == 'MIN_QUANTITY':
		try:
			int(parameter)
			if int(parameter) > 0:
				pass
			else:
				# messages.warning(request, 'Enter a number please')
				return [False, 'Enter a positive number please']
		except ValueError:
			# messages.warning(request, 'Enter a number please')
			return [False, 'Enter a number please']
	brule = BaseRule(store_id=store_id, type=rule_type[:3], parameter=parameter)
	brule.save()
	return [True, brule.id]


def add_complex_rule_to_store_1(rule_type, prev_rule, store_id, operator, parameter, user_id):
	if not User.objects.get(id=user_id).has_perm('ADD_RULE', Store.objects.get(pk=store_id)):
		return [False, "you don't have the permission to add complex rule to store!"]

	if rule_type == 'MAX_QUANTITY' or rule_type == 'MIN_QUANTITY':
		try:
			int(parameter)
			if int(parameter) > 0:
				pass
			else:
				return [False, 'Enter a positive number please']
		except ValueError:
			return [False, 'Enter a number please']
	base_rule = BaseRule(store_id=store_id, type=rule_type[:3], parameter=parameter)
	base_rule.save()
	rule_id2 = base_rule.id
	rule2_temp = '_' + str(rule_id2)
	cr = ComplexStoreRule(left=prev_rule, right=rule2_temp, operator=operator, store_id=store_id)
	cr.save()
	return [True, cr.id]


def get_store_details(store_id):
	return c_Store.get_store(store_id).get_details()


def add_complex_rule_to_store_2(rule1, parameter1, rule2, parameter2, store_id, operator1, operator2, prev_rule,
                                user_id):
	if not User.objects.get(id=user_id).has_perm('ADD_RULE', Store.objects.get(pk=store_id)):
		return [False, "you don't have the permission to add complex rule to store!"]

	if rule1 == 'MAX_QUANTITY' or rule1 == 'MIN_QUANTITY':
		try:
			int(parameter1)
			if int(parameter1) > 0:
				pass
			else:
				return [False, 'Enter a positive number please for first parameter']
		except ValueError:
			return [False, 'Enter a number please for first parameter']
	if rule2 == 'MAX_QUANTITY' or rule2 == 'MIN_QUANTITY':
		try:
			int(parameter2)
			if int(parameter2) > 0:
				pass
			else:
				return [False, 'Enter a positive number please for second parameter']
		except ValueError:
			return [False, 'Enter a number please for second parameter']
	base_rule1 = BaseRule(store_id=store_id, type=rule1[:3], parameter=parameter1)
	base_rule1.save()
	rule_id1 = base_rule1.id
	rule1_temp = '_' + str(rule_id1)
	base_rule2 = BaseRule(store_id=store_id, type=rule2[:3], parameter=parameter2)
	base_rule2.save()
	rule_id2 = base_rule2.id
	rule2_temp = '_' + str(rule_id2)
	cr = ComplexStoreRule(left=rule1_temp, right=rule2_temp, operator=operator1, store_id=store_id)
	cr.save()
	cr_id = cr.id
	cr2 = ComplexStoreRule(left=prev_rule, right=cr_id, operator=operator2, store_id=store_id)
	cr2.save()
	return [True, cr2.id]


def add_base_rule_to_item(item_id, rule, parameter, user_id):
	if not (Store.objects.filter(items__id=item_id).exists() and
	        User.objects.get(id=user_id).has_perm('ADD_RULE', Store.objects.filter(items__id=item_id)[0])):
		return [False, "you don't have the permission to add base rule to store or the item doesn't exists!"]

	brule = BaseItemRule(item_id=item_id, type=rule[:3], parameter=parameter)
	brule.save()
	return [True, brule.id]


def add_complex_rule_to_item_1(item_id, prev_rule, rule, operator, parameter, user_id):
	if not (Store.objects.filter(items__id=item_id).exists() and
	        User.objects.get(id=user_id).has_perm('ADD_RULE', Store.objects.filter(items__id=item_id)[0])):
		return [False, "you don't have the permission to add complex rule to store or the item doesn't exists!"]

	base_rule = BaseItemRule(item_id=item_id, type=rule[:3], parameter=parameter)
	base_rule.save()
	rule_id2 = base_rule.id
	rule2_temp = '_' + str(rule_id2)
	cr = ComplexItemRule(left=prev_rule, right=rule2_temp, operator=operator, item_id=item_id)
	cr.save()
	return [True, cr.id]


def add_complex_rule_to_item_2(item_id, prev_rule, rule1, parameter1, rule2, parameter2, operator1, operator2, user_id):
	if not (Store.objects.filter(items__id=item_id).exists() and
	        User.objects.get(id=user_id).has_perm('ADD_RULE', Store.objects.filter(items__id=item_id)[0])):
		return [False, "you don't have the permission to add complex rule to store or the item doesn't exists!"]

	base_rule1 = BaseItemRule(item_id=item_id, type=rule1[:3], parameter=parameter1)
	base_rule1.save()
	rule_id1 = base_rule1.id
	rule1_temp = '_' + str(rule_id1)
	base_rule2 = BaseItemRule(item_id=item_id, type=rule2[:3], parameter=parameter2)
	base_rule2.save()
	rule_id2 = base_rule2.id
	rule2_temp = '_' + str(rule_id2)
	cr = ComplexItemRule(left=rule1_temp, right=rule2_temp, operator=operator1, item_id=item_id)
	cr.save()
	cr_id = cr.id
	cr2 = ComplexItemRule(left=prev_rule, right=cr_id, operator=operator2, item_id=item_id)
	cr2.save()
	return [True, cr2.id]


def add_item_to_store(price, name, description, category, quantity, store_id, user_id):
	if not User.objects.get(id=user_id).has_perm('ADD_ITEM', Store.objects.get(pk=store_id)):
		return [False, "you don't have the permission to add an item!"]

	item = c_Item(price=price, name=name, category=category, description=description, quantity=quantity)
	c_Store.get_store(store_id).add_item(item_pk=item.pk)
	return [True, 'Your Item was added successfully!', item.pk]


def can_remove_store(store_id, user_id):
	return c_Store.get_store(store_id=store_id).has_perm(perm='REMOVE_STORE', user_id=user_id)


def delete_store(store_id, user_id):
	if not can_remove_store(store_id, user_id):
		return [False, "you don't have the permission to delete the store!"]

	s = c_Store.get_store(store_id)
	s.delete()
	return [True, 'store was deleted : ' + s.name]


def get_user_store_list(user_id):
	return c_User.get_user(user_id=user_id).get_stores()


def get_item_details(item_id):
	return c_Item.get_item(item_id=item_id).get_details()


def add_item_to_cart(user_id, item_id):
	if user_id is not None:
		item_store_pk = c_Store.get_item_store(item_pk=item_id).pk
		cart = c_Cart.get_cart(store_pk=item_store_pk, user_id=user_id)
		if cart is None:
			cart = c_Cart(store_pk=item_store_pk, user_pk=user_id)
		cart.add_item(item_id=item_id)
		return True
	else:
		return False


def get_item(id1):
	return Item.objects.get(id=id1)


def is_authenticated(user_id):
	return c_User.get_user(user_id=user_id).is_authenticated


def amount_in_db(item_id):
	return c_Item.get_item(item_id=item_id).quantity > 0


# TODO - FOR WHAT PURPOSE
def make_cart_2(item_id):
	item = Item.objects.get(id=item_id)
	item.quantity = Item.objects.get(id=item_id).quantity - 1
	item.save()


def remove_item_from_cart(user_id, item_id):
	c_Cart.get_cart(user_id=user_id).remove_item(item_id=item_id)
	item = c_Item.get_item(item_id=item_id)
	if item.quantity == 0:
		item.delete()


def user_has_cart_for_store(store_pk, user_pk):
	return c_Cart.get_cart(store_pk=store_pk, user_id=user_pk) != None


def len_of_super():
	return c_User.len_of_super()


def add_discount(store_id, percentage, end_date, type=None, amount=None, item_id=None, user_id=None):
	if not User.objects.get(id=user_id).has_perm('ADD_DISCOUNT', Store.objects.get(pk=store_id)):
		return [False, "you don't have the permission to add discount to store!"]
	d = Discount(store_id=store_id, type=type[:3], percentage=percentage, end_date=end_date, amount=amount, item_id=item_id)
	d.save()
	return [True, d.id]


def add_complex_discount_to_store(store_id, left, right, operator):
	d = ComplexDiscount(store_id=store_id, left=left, right=right, operator=operator)
	d.save()
	return [True, d.pk]


def update_item(item_id, item_dict, user_id):
	if not (Store.objects.filter(items__id=item_id).exists() and
	        User.objects.get(id=user_id).has_perm('EDIT_ITEM', Store.objects.filter(items__id=item_id)[0])):
		return [False, "you don't have the permission to update an item or the item doesn't exists!"]
	c_Item.get_item(item_id=item_id).update(item_dict=item_dict)
	return True


def item_rules_string(item_id):
	base_arr = []
	complex_arr = []
	base = []
	complex1 = []
	# item = Item.objects.get(id=item_id)
	for rule in reversed(ComplexItemRule.objects.all().filter(item_id=item_id)):
		if rule.id in complex_arr:
			continue
		res = {"id": rule.id, "type": 2, "item": item_id, "name": string_item_rule(rule, base_arr, complex_arr)}
		complex1.append(res)
	for rule in BaseItemRule.objects.all().filter(item_id=item_id):
		if rule.id in base_arr:
			continue
		res = {"id": rule.id, "type": 1, "item": item_id, "name": get_base_rule_item(rule.id)}
		base.append(res)
	return complex1 + base


def string_item_rule(rule, base_arr, complex_arr):
	curr = '('
	if rule.left[0] == '_':
		base_arr.append(int(rule.left[1:]))
		curr += get_base_rule_item(int(rule.left[1:]))
	else:
		complex_arr.append(int(rule.left))
		tosend = ComplexItemRule.objects.get(id=int(rule.left))
		curr += string_item_rule(tosend, base_arr, complex_arr)
	curr += ' ' + rule.operator + ' '
	if rule.right[0] == '_':
		base_arr.append(int(rule.right[1:]))
		curr += get_base_rule_item(int(rule.right[1:]))
	else:
		complex_arr.append(int(rule.right))
		tosend = ComplexItemRule.objects.get(id=int(rule.right))
		curr += string_item_rule(tosend, base_arr, complex_arr)
	curr += ')'
	return curr


def get_base_rule_item(rule_id):
	rule = BaseItemRule.objects.get(id=rule_id)
	return rule.type + ': ' + rule.parameter


def store_rules_string(store_id):
	base_arr = []
	complex_arr = []
	base = []
	complex1 = []
	for rule in reversed(ComplexStoreRule.objects.all().filter(store_id=store_id)):
		if rule.id in complex_arr:
			continue
		res = {"id": rule.id, "type": 2, "store": store_id, "name": string_store_rule(rule, base_arr, complex_arr)}
		complex1.append(res)
	for rule in BaseRule.objects.all().filter(store_id=store_id):
		if rule.id in base_arr:
			continue
		res = {"id": rule.id, "type": 1, "store": store_id, "name": get_base_rule(rule.id)}
		base.append(res)
	return complex1 + base


def string_store_rule(rule, base_arr, complex_arr):
	curr = '('
	if rule.left[0] == '_':
		base_arr.append(int(rule.left[1:]))
		curr += get_base_rule(int(rule.left[1:]))
	else:
		complex_arr.append(int(rule.left))
		tosend = ComplexStoreRule.objects.get(id=int(rule.left))
		curr += string_store_rule(tosend, base_arr, complex_arr)
	curr += ' ' + rule.operator + ' '
	if rule.right[0] == '_':
		base_arr.append(int(rule.right[1:]))
		curr += get_base_rule(int(rule.right[1:]))
	else:
		complex_arr.append(int(rule.right))
		tosend = ComplexStoreRule.objects.get(id=int(rule.right))
		curr += string_store_rule(tosend, base_arr, complex_arr)
	curr += ')'
	return curr


def get_base_rule(rule_id):
	rule = BaseRule.objects.get(id=rule_id)
	if rule.type == "REG":
		return rule.type + ': Only'
	return rule.type + ': ' + rule.parameter


# sss-----------------------------------------------------------------------------------------
def store_discounts_string(store_id):
	base_arr = []
	complex_arr = []
	base = []
	complex = []
	for discount in reversed(ComplexDiscount.objects.all().filter(store_id=store_id)):
		if discount.id in complex_arr:
			continue
		res = {"id": discount.id, "type": 2, "store": store_id,
		       "name": string_store_discount(discount, base_arr, complex_arr)}
		complex.append(res)
	for discount in Discount.objects.all().filter(store_id=store_id):
		if discount.id in base_arr:
			continue
		res = {"id": discount.id, "type": 1, "store": store_id, "name": get_base_discount(discount.id)}
		base.append(res)
	return complex + base


def string_store_discount(disc, base_arr, complex_arr):
	curr = '('
	if disc.left[0] == '_':
		base_arr.append(int(disc.left[1:]))
		curr += get_base_discount(int(disc.left[1:]))
	else:
		complex_arr.append(int(disc.left))
		tosend = ComplexDiscount.objects.get(id=int(disc.left))
		curr += string_store_discount(tosend, base_arr, complex_arr)
	curr += ' ' + disc.operator + ' '
	if disc.right[0] == '_':
		base_arr.append(int(disc.right[1:]))
		curr += get_base_discount(int(disc.right[1:]))
	else:
		complex_arr.append(int(disc.right))
		tosend = ComplexDiscount.objects.get(id=int(disc.right))
		curr += string_store_discount(tosend, base_arr, complex_arr)
	curr += ')'
	return curr


def get_base_discount(disc_id):
	discount = Discount.objects.get(id=disc_id)
	if discount.type == 'MAX':
		if discount.item is None:
			res = str(discount.percentage) + ' % off, up to ' + str(discount.amount) + ' items.'
		else:
			item = Item.objects.get(id=discount.item.id)
			res = str(discount.percentage) + ' % off on ' + item.name + ', up to ' + str(discount.amount) + ' of these.'
	elif discount.type == 'MIN':
		if discount.item is None:
			res = 'Buy at least ' + str(discount.amount) + ' items and get ' + str(discount.percentage) + ' % off.'
		else:
			item = Item.objects.get(id=discount.item.id)
			res = 'Buy at least ' + str(discount.amount) + ' copies of ' + item.name + ' and get ' + str(
				discount.percentage) + ' % off.'
	else:
		if discount.item is None:
			res = str(discount.percentage) + ' % off on the entire store.'
		else:
			item = Item.objects.get(id=discount.item.id)
			res = str(discount.percentage) + ' % off on ' + item.name

	return res


def get_store_items(store_id):
	return list(
		map(lambda i_d: c_Item.get_item(item_id=i_d).to_dict(), c_Store.get_store(store_id=store_id).all_items_ids()))


def get_store_managers(store_id):
	store = Store.objects.get(pk=store_id)
	managers = store.managers.all()
	return list(map(lambda i: i.__dict__, managers))


def get_store_owners(store_id):
	store = Store.objects.get(pk=store_id)
	owners = store.owners.all()
	return list(map(lambda i: i.__dict__, owners))


def update_store(store_id, store_dict):
	c_Store.get_store(store_id=store_id).update(store_dict=store_dict)
	return True


def delete_item(item_id, user_id):
	if not (Store.objects.filter(items__id=item_id).exists() and
	        User.objects.get(id=user_id).has_perm('REMOVE_ITEM', Store.objects.filter(items__id=item_id)[0])):
		return [False, "you don't have the permission to delete this item from the store or the item doesn't exists!"]

	c_Item.get_item(item_id=item_id).delete()
	return True


def get_store_creator(store_id):
	return c_Store.get_store(store_id=store_id).get_creator().pk


def get_store_by_id(store_id):
	return Store.objects.get(pk=store_id)


# TODO - REFACTOR
def remove_manager_from_store(store_id, m_id):
	try:
		store_ = Store.objects.get(pk=store_id)
		user = User.objects.get(id=m_id)
		print('---------------remove manager : ', user.username)
		is_manager = len(Store.objects.filter(id=store_id, owners__id__in=[m_id])) == 0
		if is_manager:
			store_.managers.remove(user)
			if have_no_more_stores(m_id):
				print('[[[[[[[[[[[[[[[[[[[[[')
				owners_group = Group.objects.get(name="store_owners")
				managers_group = Group.objects.get_or_create(name="store_managers")[0]
				# managers_group = Group.objects.get(name="store_managers")
				# user = User.objects.get(id = owner)
				managers_group.user_set.remove(user)
				owners_group.user_set.remove(user)
			return True
		else:
			store_.owners.remove(user)
			if have_no_more_stores(m_id):
				print('[[[[[[[[[999999999999999999[[[[[[[[[[[[')
				owners_group = Group.objects.get(name="store_owners")
				managers_group = Group.objects.get_or_create(name="store_managers")[0]
				# managers_group = Group.objects.get(name="store_managers")
				managers_group.user_set.remove(user)
				owners_group.user_set.remove(user)
			return True
	except:
		return False


def get_user_notifications(user_id):
	return list(map(lambda n: n.__dict__, list(map(lambda pk: Notification.objects.get(id=pk),
	                                               list(map(lambda n: n.notification_id,
	                                                        NotificationUser.objects.filter(user=user_id)))))))


def mark_notification_read(user_id):
	for n in NotificationUser.objects.filter(user=user_id):
		n.been_read = True
		n.save()
	return True


def have_no_more_stores(user_pk):
	return c_User.get_user(user_id=user_pk).have_no_more_stores()


def buy_logic(item_id, amount, amount_in_db, is_auth, username, shipping_details, card_details, is_cart, user_id, total_amount):
	pay_transaction_id = -1
	supply_transaction_id = -1
	messages_ = ''
	c_item = c_Item.get_item(item_id=item_id)
	amount_in_db1 = Item.objects.get(id=item_id).quantity
	if c_item.has_available_amount(amount):
		total = c_item.calc_total(amount=amount)
		if not c_item.check_rules(amount=amount):
			messages_ += "you can't buy due to item policies"
			return False, 0, 0, messages_

		store_of_item = c_Store.get_item_store(item_pk=item_id)
		if not store_of_item.check_rules(total_amount, shipping_details['country'], is_auth):
			messages_ += "you can't buy due to store policies"
			return False, 0, 0, messages_
		total_after_discount = "" if is_cart else store_of_item.apply_discounts(c_item=c_item, amount=int(amount))
		# if (is_cart is False):
		# 	total_after_discount = store_of_item.apply_discounts(c_item=c_item, amount=int(amount))
		try:
			if pay_system.handshake():
				print("pay hand shake")

				pay_transaction_id = pay_system.pay(str(card_details['card_number']),
				                                    str(card_details['month']),
				                                    str(card_details['year']),
				                                    str(card_details['holder']),
				                                    str(card_details['cvc']),
				                                    str(card_details['id']))
				if pay_transaction_id == '-1':
					messages_ += '\n' + 'can`t pay !'
					return False, 0, 0, messages_
			else:
				messages_ += '\n' + 'can`t connect to pay system!'
				return False, 0, 0, messages_
			if supply_system.handshake():
				print("supply hand shake")
				supply_transaction_id = supply_system.supply(str(shipping_details['name']),
				                                             str(shipping_details['address']),
				                                             str(shipping_details['city']),
				                                             str(shipping_details['country']),
				                                             str(shipping_details['zip']))
				if supply_transaction_id == '-1':
					pay_system.cancel_pay(pay_transaction_id)
					messages_ += '\n' + 'can`t supply abort payment!'
					return False, 0, 0, messages_
			else:
				pay_system.cancel_pay(pay_transaction_id)
				messages_ += '\n' + 'can`t connect to supply system abort payment!'
				return False, 0, 0, messages_

			c_item.quantity = amount_in_db1 - amount
			c_item.save()
			try:
				item_subject = ItemSubject(c_item.pk)
				if (is_auth):
					notification = Notification.objects.create(
						msg=username + ' bought ' + str(amount) + ' pieces of ' + c_item.name)
					notification.save()
					item_subject.subject_state = item_subject.subject_state + [notification.pk]
				else:
					notification = Notification.objects.create(
						msg='A guest bought ' + str(amount) + ' pieces of ' + c_item.name)
					notification.save()
					item_subject.subject_state = item_subject.subject_state + [notification.pk]
			except Exception as e:
				messages_ += 'cant connect websocket ' + str(e)

			_item_name = c_item.name
			if c_item.quantity == 0:
				c_item.delete()

			messages_ += '\n' + 'Thank you! you bought ' + _item_name + '\n' + 'Total after discount: ' \
			             + str(total_after_discount) + ' $' + '\n' + 'Total before: ' + str(total) + ' $'
			return True, total, total_after_discount, messages_
		except Exception as a:
			c_item.quantity = amount_in_db1
			c_item.save()

			if not (pay_transaction_id == '-1'):
				messages_ += '\n' + 'failed and aborted pay! please try again!'
				pay_system.cancel_pay(pay_transaction_id)
			if not (supply_transaction_id == '-1'):
				messages_ += '\n' + 'failed and aborted supply! please try again!'
				supply_system.cancel_supply(supply_transaction_id)
			messages_ = "Exception! "  '  :  ' + str(a)
			return False, 0, 0, messages_
	else:
		messages_ = "no such amount for item : " + str(item_id) + '   messages_ : ' + messages_
		return False, 0, 0, messages_


def delete_complex(rule_id):
	rule = ComplexStoreRule.objects.get(id=rule_id)
	if rule.left[0] == '_':
		BaseRule.objects.get(id=int(rule.left[1:])).delete()
	else:
		delete_complex(int(rule.left))
	if rule.right[0] == '_':
		BaseRule.objects.get(id=int(rule.right[1:])).delete()
	else:
		delete_complex(int(rule.right))
	rule.delete()


def delete_base(rule_id):
	rule = BaseRule.objects.get(id=rule_id)
	rule.delete()


def delete_complex_item(rule_id):
	rule = ComplexItemRule.objects.get(id=rule_id)
	if rule.left[0] == '_':
		BaseItemRule.objects.get(id=int(rule.left[1:])).delete()
	else:
		delete_complex_item(int(rule.left))
	if rule.right[0] == '_':
		BaseItemRule.objects.get(id=int(rule.right[1:])).delete()
	else:
		delete_complex_item(int(rule.right))
	rule.delete()


def delete_base_item(rule_id):
	rule = BaseItemRule.objects.get(id=rule_id)
	rule.delete()


def delete_complex_discount(disc_id):
	discount = ComplexDiscount.objects.get(id=disc_id)
	if discount.left[0] == '_':
		Discount.objects.get(id=int(discount.left[1:])).delete()
	else:
		delete_complex_discount(int(discount.left))
	if discount.right[0] == '_':
		Discount.objects.get(id=int(discount.right[1:])).delete()
	else:
		delete_complex_discount(int(discount.right))
	discount.delete()


def delete_base_discount(disc_id):
	discount = Discount.objects.get(id=disc_id)
	discount.delete()


def get_discounts_serach(item_id):
	store_id = Store.objects.get(items__id__contains=item_id).id
	base_arr = []
	complex_arr = []
	base = []
	complex = []
	for discount in reversed(ComplexDiscount.objects.all().filter(store_id=store_id)):
		if discount.id in complex_arr:
			continue
		check = []
		res = search_store_discount(discount, base_arr, complex_arr, item_id, check)
		if len(check) > 0:
			complex.append(res)
	for discount in Discount.objects.all().filter(store_id=store_id):
		if discount.id in base_arr:
			continue
		result = search_base_discount(discount.id, item_id)
		if result['is_item'] is True:
			base.append(result['discount'])
	return complex + base


def search_store_discount(disc, base_arr, complex_arr, item_id, check):
	curr = '('
	if disc.left[0] == '_':
		base_arr.append(int(disc.left[1:]))
		result = search_base_discount(int(disc.left[1:]), item_id)
		curr += result['discount']
		if result['is_item'] is True:
			check.append(1)
	else:
		complex_arr.append(int(disc.left))
		tosend = ComplexDiscount.objects.get(id=int(disc.left))
		curr += search_store_discount(tosend, base_arr, complex_arr, item_id, check)
	curr += ' ' + disc.operator + ' '
	if disc.right[0] == '_':
		base_arr.append(int(disc.right[1:]))
		result = search_base_discount(int(disc.right[1:]), item_id)
		curr += result['discount']
		if result['is_item'] is True:
			check.append(1)
	else:
		complex_arr.append(int(disc.right))
		tosend = ComplexDiscount.objects.get(id=int(disc.right))
		curr += search_store_discount(tosend, base_arr, complex_arr, item_id, check)
	curr += ')'
	return curr


def search_base_discount(disc_id, item_id):
	discount = Discount.objects.get(id=disc_id)
	flag = False
	today = datetime.date.today()
	if discount.end_date >= today:
		if discount.type == 'MAX':
			if discount.item is None:
				res = str(discount.percentage) + ' % off, up to ' + str(discount.amount) + ' items.'
				flag = True
			else:
				item = Item.objects.get(id=discount.item.id)
				res = str(discount.percentage) + ' % off on ' + item.name + ', up to ' + str(
					discount.amount) + ' of these.'
				if item.id == item_id:
					flag = True
		elif discount.type == 'MIN':
			if discount.item is None:
				res = 'Buy at least ' + str(discount.amount) + ' items and get ' + str(discount.percentage) + ' % off.'
				flag = True
			else:
				item = Item.objects.get(id=discount.item.id)
				res = 'Buy at least ' + str(discount.amount) + ' copies of ' + item.name + ' and get ' + str(
					discount.percentage) + ' % off.'
				if item.id == item_id:
					flag = True
		else:
			if discount.item is None:
				res = str(discount.percentage) + ' % off on the entire store.'
				flag = True
			else:
				item = Item.objects.get(id=discount.item.id)
				res = str(discount.percentage) + ' % off on ' + item.name
				if item.id == item_id:
					flag = True
	return {"is_item": flag, "discount": res}


def get_quantity(item_id):
	return Item.objects.get(id=item_id).quantity


def build_map(list_of_items):
	ret = []
	print(list_of_items)
	for i in list_of_items:
		store_id = Store.objects.get(items__id__contains=i['item_id']).id
		if store_id in list(map(lambda x: x['store_id'], ret)):
			store_detail = list(filter(lambda x: x['store_id'] == store_id, ret))[0]
			store_detail['amount'] += i['amount']
			store_detail['items'].append({'item_id': i['item_id'], 'item_amount': i['amount']})
		else:
			ret.append({'store_id': store_id, 'amount': i['amount'],
			            'items': [{'item_id': i['item_id'], 'item_amount': i['amount']}]})

	return ret


def calculate_price(store_map):
	ret = []
	for item in store_map['items']:
		item_o = Item.objects.get(id=item['item_id'])
		ret.append({'item_id': item['item_id'], 'price': float(item_o.price) * float(item['item_amount'])})
	return ret


def calculate_total_price(list_price):
	ret = 0
	for i in list_price:
		ret += i['price']
	return ret


def apply_discounts_for_cart(list_of_items):
	struct = build_map(list_of_items)
	total_price = 0
	total_before = 0
	for store_map in struct:
		base_arr = []
		complex_arr = []
		store_price = calculate_price(store_map)
		total_before += calculate_total_price(store_price)
		_store = Store.objects.get(id=store_map['store_id'])
		store_complex_discountes = ComplexDiscount.objects.all().filter(store=_store)
		for disc in reversed(store_complex_discountes):
			if disc.id in complex_arr:
				continue
			discount = apply_complex_cart(disc, base_arr, complex_arr, store_map)
			if (discount != -1):
				for dis in discount:
					iprice = list(filter(lambda x: x['item_id'] == dis['product'], store_price))
					if len(iprice) != 0:
						iprice[0]['price'] = float(iprice[0]['price']) * float((1 - dis['discount']))
					else:
						for i in store_price:
							i['price'] = float(i['price']) * float((1 - dis['discount']))
		store_base_discountes = Discount.objects.filter(store=store_map['store_id'])
		for disc in store_base_discountes:
			if disc.id in base_arr:
				continue
			discount = apply_base_cart(disc.id, store_map)
			if (discount != -1):
				iprice = list(filter(lambda x: x['item_id'] == discount[0]['product'], store_price))
				if len(iprice) != 0:
					iprice[0]['price'] = float(iprice[0]['price']) * float((1 - discount[0]['discount']))
				else:
					for i in store_price:
						i['price'] = float(i['price']) * float((1 - discount[0]['discount']))
		total_store = 0
		for price in store_price:
			total_store += float(price['price'])
		total_price += total_store
	return total_price, total_before


def apply_complex_cart(disc, base_arr, complex_arr, store_map):
	if disc.left[0] == '_':
		base_arr.append(int(disc.left[1:]))
		left = apply_base_cart(int(disc.left[1:]), store_map)
	else:
		complex_arr.append(int(disc.left))
		tosend = ComplexDiscount.objects.get(id=int(disc.left))
		left = apply_complex_cart(tosend, base_arr, complex_arr, store_map)
	if disc.right[0] == '_':
		base_arr.append(int(disc.right[1:]))
		right = apply_base_cart(int(disc.right[1:]), store_map)
	else:
		complex_arr.append(int(disc.right))
		tosend = ComplexDiscount.objects.get(id=int(disc.right))
		right = apply_complex_cart(tosend, base_arr, complex_arr, store_map)
	if disc.operator == "AND" and (left != -1 and right != -1):
		res = []
		for dis in right:
			ids_left = list(map(lambda x: x['product'], left))
			if dis['product'] in ids_left:
				index = ids_left.index(dis['product'])
				res.append({'product': dis['product'],
				            'discount': 1 - ((1 - dis['discount']) * (1 - left[index]['discount']))})
				left.remove(left[index])
			else:
				res.append(dis)
		return res + left
	elif disc.operator == "OR":
		res = []
		if left != -1 and right != -1:
			for dis in right:
				ids_left = list(map(lambda x: x['product'], left))
				if dis['product'] in ids_left:
					index = ids_left.index(dis['product'])
					res.append({'product': dis['product'],
					            'discount': 1 - ((1 - dis['discount']) * (1 - left[index]['discount']))})
					left.remove(left[index])
				else:
					res.append(dis)
			return res + left
		elif left != -1:
			return left
		elif right != -1:
			return right
	elif disc.operator == "XOR":
		if (left != -1 and right != -1) or (left != -1 and right == -1):
			return left
		else:
			return right
	else:
		return -1


def apply_base_cart(disc, store_map):
	base = Discount.objects.get(id=disc)
	list_of_ids = list(map(lambda x: x['item_id'], store_map['items']))
	per = float(base.percentage)
	today = datetime.date.today()
	if base.end_date < today:
		return -1
	if base.item == None:
		if base.type == 'MIN':
			if store_map['amount'] >= base.amount:
				return [{'product': '*', 'discount': per / 100}]
			else:
				return -1
		if base.type == 'MAX':
			if store_map['amount'] <= base.amount:
				return [{'product': '*', 'discount': per / 100}]
			else:
				return -1
		else:
			return [{'product': '*', 'discount': per / 100}]
	if base.item.id in list_of_ids:
		item_index = list_of_ids.index(base.item.id)
		if base.type == 'MIN':
			if store_map['items'][item_index]['item_amount'] >= base.amount:
				return [{'product': list_of_ids[item_index], 'discount': per / 100}]
			else:
				return -1
		if base.type == 'MAX':
			if store_map['items'][item_index]['item_amount'] <= base.amount:
				return [{'product': list_of_ids[item_index], 'discount': per / 100}]
			else:
				return -1
		else:
			return [{'product': list_of_ids[item_index], 'discount': per / 100}]
	else:
		return -1


class DBFailedExceptionDomainToService(Exception):
	def __init__(self, msg=None):
		self.msg = msg
