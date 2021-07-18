from django.db import models
from authentication.models import User

class Expense(models.Model):
	CATEGORY_OPTIONS = [
		('ONLINE_SERIVICES','ONLINE_SERVICES'),
		('TRAVEL','TRAVEL'),
		('FOODS','FOODS'),
		('RENT','RENT'),
		('OTHERS','OTHERS'),
	]
	owner = models.ForeignKey(User, on_delete=models.CASCADE)
	category = models.CharField(choices=CATEGORY_OPTIONS, max_length=255)
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	description = models.TextField()
	date = models.DateField(null=False,blank=False)

	class Meta:
		ordering = ['-date']

	def __str__(self):
		return str(self.owner)