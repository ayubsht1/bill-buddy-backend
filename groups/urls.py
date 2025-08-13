
# groups/urls.py
from django.urls import path
from .views import (
    GroupListCreateView,
    GroupDetailView,
    MembershipListCreateView,
    MembershipDeleteView,
)

urlpatterns = [
    path("", GroupListCreateView.as_view(), name="group-list-create"),
    path("<int:pk>/", GroupDetailView.as_view(), name="group-detail"),
    path("<int:group_id>/members/", MembershipListCreateView.as_view(), name="membership-list-create"),
    path("<int:group_id>/members/<int:pk>/", MembershipDeleteView.as_view(), name="membership-delete"),
]
