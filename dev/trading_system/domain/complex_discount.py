import trading_system.domain.domain as dom
from store.models import ComplexDiscount as m_ComplexDiscount
from trading_system.domain.discount import Discount


class ComplexDiscount:
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

	def update(self, item_dict):
		for field in self._model._meta.fields:
			if field.attname in item_dict.keys():
				setattr(self._model, field.attname, item_dict[field.attname])

		try:
			self._model.save()
		except Exception:
			raise dom.dom.dom.DBFailedExceptionDomainToService(msg='DB Failed')

	def delete(self):

		try:
			self._model.delete()
		except Exception:
			raise dom.dom.dom.DBFailedExceptionDomainToService(msg='DB Failed')

	def apply_operator(self, left, right):
		if self.operator == "AND" and (left != -1 and right != -1):
			return 1 - ((1 - left) * (1 - right))
		elif self.operator == "OR":
			if left != -1 and right != -1:
				return 1 - ((1 - left) * (1 - right))
			elif left != -1:
				return left
			elif right != -1:
				return right
		elif self.operator == "XOR":
			return max(left, right)
		else:
			return -1

	def apply(self, base_arr, complex_arr, curr_item, amount):
		if self.left[0] == '_':
			base_arr.append(int(self.left[1:]))
			left = Discount.get_discount(disc_id=int(self.left[1:])).apply(curr_item=curr_item, amount=amount)

		else:
			complex_arr.append(int(self.left))
			tosend = ComplexDiscount.get_complex_discount(disc_id=int(self.left))
			left = tosend.apply(base_arr, complex_arr, curr_item, amount)
		if self.right[0] == '_':
			base_arr.append(int(self.right[1:]))
			right = Discount.get_discount(disc_id=int(self.right[1:])).apply(curr_item=curr_item, amount=amount)
		else:

			tosend = ComplexDiscount.get_complex_discount(disc_id=int(self.right))
			right = tosend.apply(base_arr, complex_arr, curr_item, amount)

		return self.apply_operator(left=left, right=right)

	@staticmethod
	def get_store_cs_discoint(store_id):

		try:
			cir_models = m_ComplexDiscount.objects.filter(store_id=store_id)
			return list(map(lambda cir_model: ComplexDiscount(model=cir_model), list(cir_models)))
		except Exception:
			raise dom.dom.dom.DBFailedExceptionDomainToService(msg='DB Failed')

	@staticmethod
	def get_complex_discount(disc_id):

		try:
			return ComplexDiscount(model=m_ComplexDiscount.objects.filter(pk=disc_id))
		except Exception:
			raise dom.dom.dom.DBFailedExceptionDomainToService(msg='DB Failed')
