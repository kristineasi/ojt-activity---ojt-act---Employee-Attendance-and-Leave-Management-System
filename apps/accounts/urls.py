from django.urls import path

from .views import EmployeeAccountCreateAPIView, LoginAPIView, LogoutAPIView, MeAPIView, MeUpdateAPIView, RegisterAPIView

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="api-register"),
    path("login/", LoginAPIView.as_view(), name="api-login"),
    path("logout/", LogoutAPIView.as_view(), name="api-logout"),
    path("me/", MeAPIView.as_view(), name="api-me"),
    path("me/update/", MeUpdateAPIView.as_view(), name="api-me-update"),
    path("employees/create/", EmployeeAccountCreateAPIView.as_view(), name="api-employee-create"),
]
