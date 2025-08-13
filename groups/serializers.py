# groups/serializers.py
from rest_framework import serializers
from .models import Group, Membership
from django.contrib.auth import get_user_model

User = get_user_model()


class GroupSerializer(serializers.ModelSerializer):
    members_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ["id", "name", "description", "created_by", "created_at", "members_count"]
        read_only_fields = ["created_by", "created_at"]

    def get_members_count(self, obj):
        return obj.members.count()


class MembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Membership
        fields = ["id", "user", "user_email", "role", "joined_at", "group"]
        read_only_fields = ["joined_at", "group"]
