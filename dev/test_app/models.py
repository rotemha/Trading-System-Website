from django.db import models
from django.urls import reverse

# Create your models here.

TITLE_CHOICES = (
	('MR', 'Mr.'),
	('MRS', 'Mrs.'),
	('MS', 'Ms.'),
)


class Author(models.Model):
	name = models.CharField(max_length=200)

	def get_absolute_url(self):
		return reverse('author-detail', kwargs={'pk': self.pk})


class Book(models.Model):
	name = models.CharField(max_length=100)
	authors = models.ManyToManyField(Author)


class Reporter(models.Model):
	full_name = models.CharField(max_length=70)

	def __str__(self):
		return self.full_name


class Article(models.Model):
	pub_date = models.DateField()
	headline = models.CharField(max_length=200)
	content = models.TextField()
	reporter = models.ForeignKey(Reporter, on_delete=models.CASCADE)

	def __str__(self):
		return self.headline
