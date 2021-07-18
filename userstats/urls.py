from django.urls import path

from .views import ExpensesSummaryStats, IncomeSourceSummaryStats


urlpatterns = [
	path('expenses-stats/',ExpensesSummaryStats.as_view(),name='expense-stats'),
	path('income-stats/', IncomeSourceSummaryStats.as_view(), name='income-stats'),
]