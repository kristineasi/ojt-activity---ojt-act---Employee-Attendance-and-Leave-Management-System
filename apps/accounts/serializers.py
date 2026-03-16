from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    role_label = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "department", "role", "role_label"]

    def get_role_label(self, obj):
        return "Admin" if obj.role == User.Role.MANAGER else "Employee"


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["username", "password", "first_name", "last_name", "email", "department", "role"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class EmployeeAccountCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["username", "password", "first_name", "last_name", "email", "department"]

    def create(self, validated_data):
        return User.objects.create_user(
            **validated_data,
            role=User.Role.EMPLOYEE,
            is_staff=False,
            is_superuser=False,
        )
