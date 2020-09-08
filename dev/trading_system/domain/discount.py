import datetime

import trading_system.domain.domain as dom
import trading_system.domain.item as ItemModule
from store.models import Discount as m_Discount


class Discount:
	def __init__(self, model=None):
		if model != None:
			self._model = model
			return

	@property
	def pk(self):
		return self._model.pk

	@property
	def id(self):
		return self._model.pk

	@property
	def type(self):
		return self._model.type

	@property
	def parameter(self):
		return self._model.parameter

	@property
	def percentage(self):
		return self._model.percentage

	@property
	def end_date(self):
		return self._model.end_date

	@property
	def item(self):
		if self._model.item is None:
			return None
		else:
			return ItemModule.Item.get_item(item_id=self._model.item.pk)

	@property
	def amount(self):
		return self._model.amount

	def apply(self, curr_item, amount):
		per = float(self.percentage)
		today = datetime.date.today()
		if self.end_date < today:
			return -1
		if self.item == None:
			if self.type == 'MIN':
				if amount >= self.amount:
					return per / 100
				else:
					return -1
			if self.type == 'MAX':
				if amount <= self.amount:
					return per / 100
				else:
					return -1
			else:
				return per / 100
		elif self.item.id == curr_item.id:
			if self.type == 'MIN':
				if amount >= self.amount:
					return per / 100
				else:
					return -1
			if self.type == 'MAX':
				if amount <= self.amount:
					return per / 100
				else:
					return -1
			else:
				return per / 100
		else:
			return -1

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

	@staticmethod
	def get_discount(disc_id):
		return Discount(model=m_Discount.objects.get(id=disc_id))

	@staticmethod
	def get_store_discounts(store_id):

		try:
			models = m_Discount.objects.filter(store_id=store_id)
			return list(map(lambda m: Discount(model=m), models))
		except Exception:
			raise dom.DBFailedExceptionDomainToService(msg='DB Failed')
