# expenses/serializers.py
from rest_framework import serializers
from .models import Expense, ExpenseShare


class ExpenseShareSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = ExpenseShare
        fields = ["id", "user", "user_email", "amount"]
        read_only_fields = ["id", "user_email"]


class ExpenseSerializer(serializers.ModelSerializer):
    shares = ExpenseShareSerializer(many=True, read_only=True)
    paid_by_email = serializers.EmailField(source="paid_by.email", read_only=True)

    class Meta:
        model = Expense
        fields = [
            "id",
            "group",
            "description",
            "amount",
            "paid_by",
            "paid_by_email",
            "date",
            "created_at",
            "shares",
        ]
        read_only_fields = ["id", "created_at", "group", "shares", "paid_by_email"]
