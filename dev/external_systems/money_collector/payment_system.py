import requests


class Payment:
	def handshake(self):
		try:
			r = requests.post("https://cs-bgu-wsep.herokuapp.com/", data={'action_type': 'handshake'})
			print(r.status_code, r.reason)
			return r.reason == 'OK'
		except:
			return False

	def pay(self, card_number, month, year, holder, ccv, id1):
		try:
			r = requests.post("https://cs-bgu-wsep.herokuapp.com/",
			                  data={'action_type': 'pay', 'card_number': card_number, 'month': month, 'year': year,
			                        'holder': holder
				                  , 'ccv': ccv, 'id': id1})
			print(r.status_code, r.reason)
			print(r.text)
			return r.text
		except:
			return '-1'

	def cancel_pay(self, transaction_id):
		try:
			r = requests.post("https://cs-bgu-wsep.herokuapp.com/",
			                  data={'action_type': 'cancel_pay', 'transaction_id': transaction_id})
			print(r.status_code, r.reason)
			print(r.text)
			return r.text
		except:
			return '-1'
