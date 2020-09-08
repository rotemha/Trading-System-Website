import requests


class Supply:
	def handshake(self):
		try:
			r = requests.post("https://cs-bgu-wsep.herokuapp.com/", data={'action_type': 'handshake'})
			print(r.status_code, r.reason)
			return r.reason == 'OK'
		except:
			return False

	def supply(self, name, address, city, country, zip1):
		try:
			r = requests.post("https://cs-bgu-wsep.herokuapp.com/",
			                  data={'action_type': 'supply', 'name': name, 'address': address, 'city': city,
			                        'country': country, 'zip': zip1})
			print(r.status_code, r.reason)
			print(r.text)
			return r.text
		except:
			return '-1'

	def cancel_supply(self, transaction_id):
		try:
			r = requests.post("https://cs-bgu-wsep.herokuapp.com/",
			                  data={'action_type': 'cancel_supply', 'transaction_id': transaction_id})
			print(r.status_code, r.reason)
			print(r.text)
			return r.text
		except:
			return '-1'
#
#
# class Supply:
# 	def __init__(self, filename):
# 		self._filename = filename
#
# 	def load_image_from_disk(self):
# 		print("loading " + self._filename)
#
# 	def display_image(self):
# 		print("display " + self._filename)
#
#
# class Proxy:
# 	def __init__(self, subject):
# 		self._subject = subject
# 		self._proxystate = None
#
#
# class ProxySupply(Proxy):
# 	def display_image(self):
# 		if self._proxystate == None:
# 			self._subject.load_image_from_disk()
# 			self._proxystate = 1
# 		print("display " + self._subject._filename)
