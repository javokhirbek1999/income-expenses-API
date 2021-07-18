from django.db import models

from authentication.models import User

class Income(models.Model):
	SOURCE_OPTIONS = [
		('SALARY','SALARY'),
		('BUSINESS','BUSINESS'),
		('SIDE-HUSTLES','SIDE-HUSTLES'),
		('OTHERS','OTHERS'),
	]

	source = models.CharField(choices=SOURCE_OPTIONS, max_length=255)
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	description = models.TextField(default=None)
	owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
	date = models.DateField(null=False, blank=False)

	class Meta:
		ordering = ['-date']

	def __str__(self):
		return str(self.owner)