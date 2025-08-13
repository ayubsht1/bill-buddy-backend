# settlements/urls.py
from django.urls import path
from .views import (
    SettlementListCreateView,
    SettlementDetailView,
    NotificationListView,
    MarkNotificationReadView,
)

urlpatterns = [
    path("groups/<int:group_id>/settlements/", SettlementListCreateView.as_view(), name="settlement-list-create"),
    path("settlements/<int:pk>/", SettlementDetailView.as_view(), name="settlement-detail"),
    path("notifications/", NotificationListView.as_view(), name="notification-list"),
    path("notifications/<int:pk>/read/", MarkNotificationReadView.as_view(), name="notification-read"),
]
