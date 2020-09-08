import trading_system.domain.domain as dom
from store.models import ComplexItemRule as m_ComplexItemRule
from trading_system.domain.base_item_rule import BaseItemRule


class ComplexItemRule:
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

	def check(self, amount, base_arr, complex_arr):
		if self.left[0] == '_':
			base_arr.append(int(self.left[1:]))
			left = BaseItemRule.get_b_rule(rule_id=int(self.left[1:])).check(amount=amount)
		else:
			complex_arr.append(int(self.left))
			tosend = ComplexItemRule.get_ci_rule(rule_id=int(self.left))
			left = tosend.check(amount=amount, base_arr=base_arr, complex_arr=complex_arr)
		if self.right[0] == '_':
			base_arr.append(int(self.right[1:]))
			right = BaseItemRule.get_b_rule(rule_id=int(int(self.right[1:]))).check(amount=amount)
		else:
			complex_arr.append(int(self.right))
			tosend = ComplexItemRule.get_ci_rule(rule_id=int(self.right))
			right = tosend.check(amount=amount, base_arr=base_arr, complex_arr=complex_arr)
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
	def get_item_ci_rules(item_id):

		try:
			cir_models = m_ComplexItemRule.objects.filter(item_id=item_id)
			return list(map(lambda cir_model: ComplexItemRule(model=cir_model), list(cir_models)))
		except Exception:
			raise dom.DBFailedExceptionDomainToService(msg='DB Failed')

	@staticmethod
	def get_ci_rule(rule_id):

		try:
			return ComplexItemRule(model=m_ComplexItemRule.objects.get(pk=rule_id))
			# return list(map(lambda cir_model: ComplexItemRule(model=cir_model), list(cir_models)))
		except Exception:
			raise dom.DBFailedExceptionDomainToService(msg='DB Failed')
