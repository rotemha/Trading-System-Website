from django import forms

from .models import Author
from .models import TITLE_CHOICES


class NameForm(forms.Form):
	your_name = forms.CharField(label='Your name', max_length=100)


from django import forms


class ContactForm(forms.Form):
	name = forms.CharField()
	message = forms.CharField(widget=forms.Textarea)

	def send_email(self):
		# send email using the self.cleaned_data dictionary
		pass


class AuthorForm(forms.Form):
	name = forms.CharField(max_length=100)
	title = forms.CharField(
		max_length=3,
		widget=forms.Select(choices=TITLE_CHOICES),
	)
	birth_date = forms.DateField(required=False)


class BookForm(forms.Form):
	name = forms.CharField(max_length=100)
	authors = forms.ModelMultipleChoiceField(queryset=Author.objects.all())
