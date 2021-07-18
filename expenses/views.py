from django.shortcuts import render

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import permissions

from .serializers import ExpenseSerializer
from .models import Expense
from .permissions import IsOwner


class ExpenseListAPIView(ListCreateAPIView):
	serializer_class = ExpenseSerializer
	queryset = Expense.objects.all()
	permission_classes = (permissions.IsAuthenticated, IsOwner,)

	def perform_create(self,serializer):
		return serializer.save(owner=self.request.user)

	def get_queryset(self):
		return Expense.objects.filter(owner=self.request.user)


class ExpenseDetailAPIView(RetrieveUpdateDestroyAPIView):
	serializer_class = ExpenseSerializer
	queryset = Expense.objects.all()
	permission_classes = (permissions.IsAuthenticated, IsOwner,)
	lookup_field = 'id'
