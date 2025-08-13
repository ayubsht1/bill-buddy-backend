# expenses/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Expense, ExpenseShare
from groups.models import Group, Membership
from .serializers import ExpenseSerializer, ExpenseShareSerializer


class IsGroupMember(permissions.BasePermission):
    """Checks if the user is a member of the expense's group."""

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Expense):
            return Membership.objects.filter(group=obj.group, user=request.user).exists()
        elif isinstance(obj, ExpenseShare):
            return Membership.objects.filter(group=obj.expense.group, user=request.user).exists()
        return False


class IsExpenseAdminOrPayer(permissions.BasePermission):
    """Allow only group admins or the person who paid to edit/delete."""

    def has_object_permission(self, request, view, obj):
        return (
            obj.paid_by == request.user
            or Membership.objects.filter(group=obj.group, user=request.user, role="admin").exists()
        )


# -------- Expense Views --------
class ExpenseListCreateView(generics.ListCreateAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        group = get_object_or_404(Group, pk=self.kwargs["group_id"])
        # User must be a member to view expenses
        if not Membership.objects.filter(group=group, user=self.request.user).exists():
            return Expense.objects.none()
        return Expense.objects.filter(group=group).order_by("-date")

    @transaction.atomic
    def perform_create(self, serializer):
        group = get_object_or_404(Group, pk=self.kwargs["group_id"])
        # Must be a member to create expense
        if not Membership.objects.filter(group=group, user=self.request.user).exists():
            raise permissions.PermissionDenied("You are not a member of this group.")

        expense = serializer.save(group=group, paid_by=self.request.user)

        # Optional: Automatically split equally among members
        members = Membership.objects.filter(group=group).values_list("user", flat=True)
        share_amount = expense.amount / len(members)
        shares = [
            ExpenseShare(expense=expense, user_id=user_id, amount=share_amount)
            for user_id in members
        ]
        ExpenseShare.objects.bulk_create(shares)


class ExpenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated, IsGroupMember, IsExpenseAdminOrPayer]


# -------- Expense Share Views --------
class ExpenseShareListView(generics.ListAPIView):
    serializer_class = ExpenseShareSerializer
    permission_classes = [permissions.IsAuthenticated, IsGroupMember]

    def get_queryset(self):
        expense = get_object_or_404(Expense, pk=self.kwargs["expense_id"])
        return ExpenseShare.objects.filter(expense=expense)
