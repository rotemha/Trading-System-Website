from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.edit import FormView, UpdateView, DeleteView
from django.views.generic.list import ListView

from .forms import AuthorForm
from .forms import ContactForm
from .forms import NameForm
from .models import Article
from .models import Author


def get_name(request):
	# if this is a POST request we need to process the form data
	if request.method == 'POST':
		# create a form instance and populate it with data from the request:
		form = NameForm(request.POST)
		# check whether it's valid:
		if form.is_valid():
			# process the data in form.cleaned_data as required
			# ...
			# redirect to a new URL:
			tmp = form.cleaned_data['your_name']
			return HttpResponseRedirect('/test/test1/thanks/')

	# if a GET (or any other method) we'll create a blank form
	else:
		form = NameForm()

	return render(request, 'test_app/test_page1.html', {'form': form})


def thanks(request):
	return render(request, 'test_app/response.html')


def get_contact(request):
	if request.method == 'POST':
		form = NameForm(request.POST)
		if form.is_valid():
			return HttpResponseRedirect('/test/test1/thanks/')
	else:
		form = ContactForm()

	return render(request, 'test_app/test_page2.html', {'form': form})


def noa(request):
	return render(request, 'test_app/test_page3.html')


def test4(request):
	if request.method == 'POST':
		form = AuthorForm(request.POST)
		if form.is_valid():
			return HttpResponseRedirect('/test/test1/thanks/')
	else:
		form = AuthorForm()

	return render(request, 'test_app/test_page4.html', {'form': form})


def test5(request):
	if request.method == 'POST':
		form = ContactForm(request.POST)
		if form.is_valid():
			return HttpResponseRedirect('/test/test1/thanks/')
	else:
		form = ContactForm()

	return render(request, 'test_app/test_page5.html', {'form': form})


class ContactView(FormView):
	template_name = 'test_app/contact.html'
	form_class = ContactForm
	success_url = '/thanks/'

	def form_valid(self, form):
		# This method is called when valid form data has been POSTed.
		# It should return an HttpResponse.
		form.send_email()
		return super().form_valid(form)


class ArticleDetailView(DetailView):
	model = Article

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['now'] = timezone.now()
		return context


class ArticleListView(ListView):
	model = Article
	paginate_by = 100  # if pagination is desired

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['now'] = timezone.now()
		return context


class ArticleUpdate(UpdateView):
	model = Article
	fields = ['content']
	template_name_suffix = '_update_form'


class ArticleDelete(DeleteView):
	model = Article
	template_name_suffix = '_delete_form'


class AuthorCreate(CreateView):
	model = Author
	fields = ['name']

	def form_valid(self, form):
		# This method is called when valid form data has been POSTed.
		# It should return an HttpResponse.
		x = 1
		return super().form_valid(form)


class AuthorUpdate(UpdateView):
	model = Author
	template_name_suffix = '_update_form'


class AuthorDelete(DeleteView):
	model = Author
	success_url = reverse_lazy('author-list')


def author_detail(request):
	x = 1
	pass


def test_9(request, pk):
	x = 1
	pass
