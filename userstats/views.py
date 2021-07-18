import datetime
from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from expenses.models import Expense
from income.models import Income

class ExpensesSummaryStats(APIView):

	def get_total_amount(self,category,expenses_list):
		expenses = expenses_list.filter(category=category)

		amount = 0

		for expense in expenses:
			amount+=expense.amount

		return {'amount':amount}

	def get_category(self,expense):
		return expense.category

	def get(self,request):
		todays_date = datetime.date.today()
		ayear_ago = todays_date - datetime.timedelta(days=30*12)

		expenses = Expense.objects.filter(owner=request.user, date__gte=ayear_ago, date__lte=todays_date)


		final = {}
		categories = list(set(map(self.get_category,expenses)))


		for expense in expenses:
			for category in categories:
				final[category] = self.get_total_amount(category,expenses)

		return Response({'category_data':final},status=status.HTTP_200_OK)


class IncomeSourceSummaryStats(APIView):

	def get_total_amount_for_source(self,source,income_list):
		income = income_list.filter(source=source)

		amount = 0

		for i in income:
			amount+=i.amount

		return {'amount':amount}

	def get_source(self,income):
		return income.source

	def get(self,request):
		todays_date = datetime.date.today()
		ayear_ago = todays_date - datetime.timedelta(days=30*12)
		income = Income.objects.filter(owner=request.user, date__gte=ayear_ago, date__lte=todays_date)

		final = {}
		sources = list(set(map(self.get_source, income)))

		for i in income:
			for source in sources:
				final[source] = self.get_total_amount_for_source(source,income)

		return Response({'income_source_data':final},status=status.HTTP_200_OK)
