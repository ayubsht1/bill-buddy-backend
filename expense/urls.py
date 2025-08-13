# expenses/urls.py
from django.urls import path
from .views import ExpenseListCreateView, ExpenseDetailView, ExpenseShareListView

urlpatterns = [
    path("groups/<int:group_id>/expenses/", ExpenseListCreateView.as_view(), name="expense-list-create"),
    path("expenses/<int:pk>/", ExpenseDetailView.as_view(), name="expense-detail"),
    path("expenses/<int:expense_id>/shares/", ExpenseShareListView.as_view(), name="expense-share-list"),
]
