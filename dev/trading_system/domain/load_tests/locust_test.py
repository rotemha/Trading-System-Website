from locust import HttpLocust, TaskSet, task


class UserActions(TaskSet):

	def on_start(self):
		self.login()

	# pass

	def login(self):
		# login to the application
		response = self.client.get('/accounts/login/')
		csrftoken = response.cookies['csrftoken']
		self.client.post('/accounts/login/',
		                 {'username': 'username', 'password': 'prlPel24'},
		                 headers={'X-CSRFToken': csrftoken})

	@task(1)
	def index(self):
		self.client.get('/')

	@task(2)
	def add_store(self):
		self.client.get('/store/add_store/')


class ApplicationUser(HttpLocust):
	task_set = UserActions
	min_wait = 0
	max_wait = 0
