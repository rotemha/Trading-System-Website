from django.db.models import Q

import trading_system.domain.domain as dom
from store.models import Item as m_Item
from trading_system.domain.base_item_rule import BaseItemRule
from trading_system.domain.complex_item_rule import ComplexItemRule


class Item:
	def __init__(self, price=None, name=None, category=None, description=None, quantity=None, model=None):
		if model != None:
			self._model = model
			return
		self._model = m_Item.objects.create(price=price, name=name, category=category, description=description,
		                                    quantity=quantity)
		self._model.save()

	def to_dict(self):
		return self._model.__dict__

	@property
	def pk(self):
		return self._model.pk

	@property
	def id(self):
		return self._model.pk

	@property
	def quantity(self):
		return self._model.quantity

	@property
	def name(self):
		return self._model.name

	@property
	def base_rules(self):
		return BaseItemRule.get_item_bi_rules(item_id=self.pk)

	@property
	def complex_rules(self):
		return ComplexItemRule.get_item_ci_rules(item_id=self.pk)

	@quantity.setter
	def quantity(self, value):
		self._model.quantity = value

	def has_available_amount(self, amount):
		return amount <= self._model.quantity

	def calc_total(self, amount):
		return amount * self._model.price

	def check_rules(self, amount):
		base_arr = []
		complex_arr = []
		itemRules = self.complex_rules
		for rule in reversed(itemRules):
			if rule.id in complex_arr:
				continue
			if not rule.check(amount, base_arr, complex_arr):
				return False
		itemBaseRules = self.base_rules
		for rule in itemBaseRules:
			if rule.id in base_arr:
				continue
			if not rule.check(amount=amount):
				return False
		return True

	def get_details(self):
		return {"pk": self._model.pk,
		        "name": self._model.name,
		        "category": self._model.get_category_display,
		        "description": self._model.description,
		        "price": self._model.price,
		        "quantity": self._model.quantity}

	def update(self, item_dict):
		for field in self._model._meta.fields:
			if field.attname in item_dict.keys():
				setattr(self._model, field.attname, item_dict[field.attname])
		try:
			self._model.save()
		except Exception:
			raise dom.DBFailedExceptionDomainToService(msg='DB Failed')

	def delete(self):
		try:
			self._model.delete()
		except Exception:
			raise dom.DBFailedExceptionDomainToService(msg='DB Failed')

	def save(self):
		try:
			self._model.save()
		except Exception:
			raise dom.DBFailedExceptionDomainToService(msg='DB Failed')

	@staticmethod
	def get_item(item_id):
		return Item(model=m_Item.objects.get(pk=item_id))

	@staticmethod
	def search(txt):
		try:
			items_models = m_Item.objects.filter(Q(name__contains=txt) | Q(
				description__contains=txt) | Q(category__contains=txt))
			items = list(map(lambda im: Item(model=im), items_models))
			return list(map(lambda i: i.get_details(), items))
		except Exception:
			raise dom.DBFailedExceptionDomainToService(msg='DB Failed')
