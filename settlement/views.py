# settlements/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Settlement, Notification
from groups.models import Group, Membership
from .serializers import SettlementSerializer, NotificationSerializer
from .utils import send_settlement_reminder


class IsGroupMember(permissions.BasePermission):
    """Checks if user is a member of the settlement's group."""

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Settlement):
            return Membership.objects.filter(group=obj.group, user=request.user).exists()
        elif isinstance(obj, Notification):
            return obj.user == request.user
        return False


# -------- Settlement Views --------
class SettlementListCreateView(generics.ListCreateAPIView):
    serializer_class = SettlementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        group = get_object_or_404(Group, pk=self.kwargs["group_id"])
        if not Membership.objects.filter(group=group, user=self.request.user).exists():
            return Settlement.objects.none()
        return Settlement.objects.filter(group=group).order_by("-date")

    @transaction.atomic
    def perform_create(self, serializer):
        group = get_object_or_404(Group, pk=self.kwargs["group_id"])

        # Must be a member
        if not Membership.objects.filter(group=group, user=self.request.user).exists():
            raise permissions.PermissionDenied("You are not a member of this group.")

        settlement = serializer.save(group=group, paid_by=self.request.user)

        # Create in-app notification
        Notification.objects.create(
            user=settlement.paid_to,
            message=f"{settlement.paid_by.email} paid you {settlement.amount} in group '{group.name}'"
        )

        # Send email notification
        send_settlement_reminder(
            settlement.paid_to.email,
            group.name,
            settlement.amount
        )


class SettlementDetailView(generics.RetrieveAPIView):
    queryset = Settlement.objects.all()
    serializer_class = SettlementSerializer
    permission_classes = [permissions.IsAuthenticated, IsGroupMember]


# -------- Notification Views --------
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by("-created_at")


class MarkNotificationReadView(generics.UpdateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsGroupMember]

    def update(self, request, *args, **kwargs):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({"status": "marked as read"})
