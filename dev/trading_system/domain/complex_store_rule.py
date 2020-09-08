import trading_system.domain.domain as dom
from store.models import ComplexStoreRule as m_ComplexStoreRule
from trading_system.domain.base_store_rule import BaseStoreRule


class ComplexStoreRule:
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
	def left(self):
		return self._model.left

	@property
	def right(self):
		return self._model.right

	@property
	def operator(self):
		return self._model.operator

	def check(self, amount, country, base_arr, complex_arr, is_auth):
		if self.left[0] == '_':
			base_arr.append(int(self.left[1:]))
			# left = check_base_rule(int(rule.left[1:]), amount, country, is_auth)
			left = BaseStoreRule.get_b_rule(rule_id=int(self.left[1:])).check(amount=amount, country=country,
			                                                                  is_auth=is_auth)
		else:
			complex_arr.append(int(self.left))
			tosend = ComplexStoreRule.get_si_rule(rule_id=int(self.left))
			left = tosend.check(amount, country, base_arr, complex_arr, is_auth)
		if self.right[0] == '_':
			base_arr.append(int(self.right[1:]))
			right = BaseStoreRule.get_b_rule(rule_id=int(self.right[1:])).check(amount=amount, country=country,
			                                                                    is_auth=is_auth)
		else:
			complex_arr.append(int(self.right))
			tosend = ComplexStoreRule.get_si_rule(rule_id=int(self.right))
			right = tosend.check(amount, country, base_arr, complex_arr, is_auth)
		return self.apply_op(left=left, right=right)

	def apply_op(self, left, right):
		if self.operator == "AND" and (left is False or right is False):
			return False
		if self.operator == "OR" and (left is False and right is False):
			return False
		if self.operator == "XOR" and ((left is False and right is False) or (left is True and right is True)):
			return False
		return True

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
	def get_item_si_rules(store_id):

		try:
			cir_models = m_ComplexStoreRule.objects.filter(store_id=store_id)
			return list(map(lambda cir_model: ComplexStoreRule(model=cir_model), list(cir_models)))
		except Exception:
			raise dom.DBFailedExceptionDomainToService(msg='DB Failed')

	@staticmethod
	def get_si_rule(rule_id):

		try:
			return ComplexStoreRule(model=m_ComplexStoreRule.objects.filter(pk=rule_id))
		except Exception:
			raise dom.DBFailedExceptionDomainToService(msg='DB Failed')
