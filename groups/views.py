# groups/views.py
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Group, Membership
from .serializers import GroupSerializer, MembershipSerializer
from django.db import IntegrityError


# -------- Permissions --------
class IsGroupAdmin(permissions.BasePermission):
    """
    Allow access only if the user is group creator or has admin membership.
    """

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Group):
            return (
                obj.created_by == request.user
                or Membership.objects.filter(
                    user=request.user, group=obj, role="admin"
                ).exists()
            )
        elif isinstance(obj, Membership):
            return (
                obj.group.created_by == request.user
                or Membership.objects.filter(
                    user=request.user, group=obj.group, role="admin"
                ).exists()
            )
        return False


# -------- Group Views --------
class GroupListCreateView(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        group = serializer.save(created_by=self.request.user)
        # Add creator as admin member automatically
        Membership.objects.create(user=self.request.user, group=group, role="admin")


class GroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated, IsGroupAdmin]


# -------- Membership Views --------
class MembershipListCreateView(generics.ListCreateAPIView):
    serializer_class = MembershipSerializer
    permission_classes = [permissions.IsAuthenticated, IsGroupAdmin]

    def get_queryset(self):
        group = get_object_or_404(Group, pk=self.kwargs["group_id"])
        return Membership.objects.filter(group=group)

    def perform_create(self, serializer):
        group = get_object_or_404(Group, pk=self.kwargs["group_id"])
        try:
            serializer.save(group=group)
        except IntegrityError:
            raise serializers.ValidationError("User is already a member of this group.")


class MembershipDeleteView(generics.DestroyAPIView):
    serializer_class = MembershipSerializer
    permission_classes = [permissions.IsAuthenticated, IsGroupAdmin]

    def get_object(self):
        group = get_object_or_404(Group, pk=self.kwargs["group_id"])
        return get_object_or_404(Membership, pk=self.kwargs["pk"], group=group)
