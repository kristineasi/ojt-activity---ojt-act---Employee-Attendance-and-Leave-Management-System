from django.urls import path

from .views import UserLogoutView, dashboard_view, login_view

urlpatterns = [
    path("", login_view, name="login"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
]
