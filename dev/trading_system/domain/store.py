from django.contrib.auth.models import User, Group
from django.db.models import Q
from guardian.shortcuts import assign_perm

import trading_system.domain.domain as dom
from store.models import Store as m_Store, Item
from trading_system.domain.base_store_rule import BaseStoreRule
from trading_system.domain.complex_discount import ComplexDiscount
from trading_system.domain.complex_store_rule import ComplexStoreRule
from trading_system.domain.discount import Discount
from trading_system.domain.item import Item as c_Item
from trading_system.domain.user import User as c_User
from trading_system.models import ObserverUser


class Store:
	def __init__(self, name=None, desc=None, owner_id=None, model=None):
		if model is not None:
			self._model = model
			return
		self._model = m_Store.objects.create(name=name, description=desc)
		self._model.owners.add(User.objects.get(pk=owner_id))
		self._model.partners.add(User.objects.get(pk=owner_id))
		self._model.save()
		_user = User.objects.get(pk=owner_id)
		my_group = Group.objects.get_or_create(name="store_owners")[0]
		# my_group = Group.objects.get(name="store_owners")
		if len(ObserverUser.objects.filter(user_id=_user.pk)) == 0:
			ObserverUser.objects.create(user_id=_user.pk,
			                            address="ws://127.0.0.1:8000/ws/store_owner/{}/".format(_user.pk)).save()
		_user.groups.add(my_group)
		assign_perm('ADD_ITEM', _user, self._model)
		assign_perm('REMOVE_ITEM', _user, self._model)
		assign_perm('EDIT_ITEM', _user, self._model)
		assign_perm('ADD_MANAGER', _user, self._model)
		assign_perm('REMOVE_STORE', _user, self._model)
		assign_perm('ADD_DISCOUNT', _user, self._model)
		assign_perm('ADD_RULE', _user, self._model)

	@property
	def pk(self):
		return self._model.pk

	@property
	def name(self):
		return self._model.name

	@property
	def complex_discounts(self):
		return ComplexDiscount.get_store_cs_discoint(store_id=self.pk)

	@property
	def discounts(self):
		return Discount.get_store_discounts(store_id=self.pk)

	@property
	def complex_rules(self):
		return ComplexStoreRule.get_item_si_rules(store_id=self.pk)

	@property
	def base_rules(self):
		return BaseStoreRule.get_store_bs_rules(store_id=self.pk)

	@property
	def items(self):
		return list(map(lambda i: c_Item.get_item(item_id=i.pk), list(self._model.items.all())))

	@property
	def managers(self):
		return list(map(lambda u: c_User.get_user(user_id=u.pk), list(self._model.managers.all())))

	@property
	def owners(self):
		return list(map(lambda u: c_User.get_user(user_id=u.pk), list(self._model.owners.all())))

	def all_owners_ids(self):
		return list(map(lambda o: o.pk, self.owners))

	def all_managers_ids(self):
		return list(map(lambda o: o.pk, self.managers))

	def all_partners_ids(self):
		partners = list(self._model.partners.all())
		return list(map(lambda o: o.id, partners))

	def all_items_ids(self):
		return list(map(lambda i: i.id, self.items))

	def add_item(self, item_pk):
		item = Item.objects.get(pk=item_pk)
		self._model.items.add(item)

	def assign_perm(self, perm, user_id):
		assign_perm(perm, User.objects.get(pk=user_id), self._model)

	def has_perm(self, perm, user_id):
		return User.objects.get(pk=user_id).has_perm(perm, self._model)

	def is_already_owner(self, user_id):
		return self._model.owners.filter(id=user_id).exists()

	def is_already_manager(self, user_id):
		return self._model.managers.filter(id=user_id).exists()

	def add_owner(self, user_id):
		self._model.owners.add(User.objects.get(pk=user_id))

	def add_manager(self, user_id):
		self._model.managers.add(User.objects.get(pk=user_id))

	def delete(self):
		items_to_delete = self._model.items.all()
		owners_ids = self.all_owners_ids()
		managers_ids = self.all_managers_ids()
		partners_ids = self.all_partners_ids()
		owners_objs = list(map(lambda id1: c_User.get_user(user_id=id1), owners_ids))
		managers_objs = list(map(lambda id1: c_User.get_user(user_id=id1), managers_ids))
		partners_objs = list(map(lambda id1: c_User.get_user(user_id=id1), partners_ids))
		for item_ in items_to_delete:
			item_.delete()
		for owner in owners_objs:
			if owner.owns_no_more_stores():
				owner.remove_from_owners()
		for manager in managers_objs:
			if manager.manages_no_more_stores():
				manager.remove_from_managers()
		for partner in partners_objs:
			if partner.manages_no_more_stores():
				partner.remove_from_owners()
		self._model.delete()

	def update(self, store_dict):
		for field in self._model._meta.fields:
			if field.attname in store_dict.keys():
				setattr(self._model, field.attname, store_dict[field.attname])
		try:

			self._model.save()
		except Exception:
			raise dom.DBFailedExceptionDomainToService(msg='DB Failed')

	def check_rules(self, amount, country, is_auth):
		base_arr = []
		complex_arr = []
		storeRules = self.complex_rules
		for rule in reversed(storeRules):
			if rule.id in complex_arr:
				continue
			# if check_store_rule(rule, amount, country, base_arr, complex_arr, is_auth) is False:
			if not rule.check(amount, country, base_arr, complex_arr, is_auth):
				return False
		storeBaseRules = self.base_rules
		for rule in storeBaseRules:
			if rule.id in base_arr:
				continue
			if rule.check(amount=amount, country=country, is_auth=is_auth):
				return False
		return True

	def get_details(self):
		return {"name": self._model.name, "description": self._model.description, "owners":
			list(map(lambda o_id: User.objects.get(pk=o_id).username, self.all_owners_ids())), "managers":
			        list(map(lambda m_id: User.objects.get(pk=m_id).username, self.all_managers_ids())),
		        "items": list(map(lambda i_id: str(Item.objects.get(pk=i_id)), self.all_items_ids()))}

	def get_creator(self):
		return c_User(self._model.owners.all()[0])

	def apply_discounts(self, c_item, amount):
		base_arr = []
		complex_arr = []
		price = c_item.calc_total(amount=amount)
		store_complex_discountes = self.complex_discounts
		for disc in reversed(store_complex_discountes):
			if disc.id in complex_arr:
				continue

			discount = disc.apply(base_arr, complex_arr, c_item, amount)
			if (discount != -1):
				price = (1 - discount) * float(price)
		store_base_discountes = self.discounts
		for disc in store_base_discountes:
			if disc.id in base_arr:
				continue
			discount = float(disc.apply(curr_item=c_item, amount=amount))
			if (discount != -1):
				price = (1 - discount) * float(price)
		return price

	@staticmethod
	def get_store(store_id):
		try:
			return Store(model=m_Store.objects.get(pk=store_id))
		except Exception:
			raise dom.DBFailedExceptionDomainToService(msg='DB Failed')

	@staticmethod
	def owns_stores(user_id):
		try:
			tmp = m_Store.objects.filter(owners__username__contains=user_id)
			return len(tmp) == 0
		except Exception:
			raise dom.DBFailedExceptionDomainToService(msg='DB Failed')

	@staticmethod
	def manages_stores(user_id):
		try:
			tmp = m_Store.objects.filter(managers__username__contains=user_id)
			return len(tmp) == 0
		except Exception:
			raise dom.DBFailedExceptionDomainToService(msg='DB Failed')

	@staticmethod
	def get_owned_stores(user_id):
		try:
			return list(map(lambda s: {'id': s.pk, 'name': s.name},
			                m_Store.objects.filter(Q(managers__id__in=[user_id]) | Q(owners__id__in=[user_id]))))
		except Exception:
			raise dom.DBFailedExceptionDomainToService(msg='DB Failed')

	@staticmethod
	def get_item_store(item_pk):
		try:
			model = list(filter(lambda s: item_pk in map(lambda i: i.pk, s.items.all()), m_Store.objects.all()))[0]
			return Store(model=model)
		except Exception:
			raise dom.DBFailedExceptionDomainToService(msg='DB Failed')
