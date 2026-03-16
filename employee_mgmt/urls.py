from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.dashboard.urls")),
    path("api/accounts/", include("apps.accounts.urls")),
    path("api/attendance/", include("apps.attendance.urls")),
    path("api/leaves/", include("apps.leaves.urls")),
]
