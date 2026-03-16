from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    fieldsets = UserAdmin.fieldsets + (("Profile", {"fields": ("role", "department")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Profile", {"fields": ("first_name", "last_name", "email", "role", "department")}),)
    list_display = ("username", "email", "first_name", "last_name", "role", "department", "is_staff")
    list_filter = ("role", "department", "is_staff")
    search_fields = ("username", "first_name", "last_name", "email", "department")
