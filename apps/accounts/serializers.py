from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    role_label = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "department", "hourly_rate", "role", "role_label"]

    def get_role_label(self, obj):
        return "Admin" if obj.role == User.Role.MANAGER else "Employee"


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["username", "password", "first_name", "last_name", "email", "department", "hourly_rate", "role"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class EmployeeAccountCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["username", "password", "first_name", "last_name", "email", "department", "hourly_rate"]

    def create(self, validated_data):
        return User.objects.create_user(
            **validated_data,
            role=User.Role.EMPLOYEE,
            is_staff=False,
            is_superuser=False,
        )


class ProfileUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True, min_length=8)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "department", "password"]

    def validate_username(self, value):
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError("This username is already in use.")
        return value

    def update(self, instance, validated_data):
        password = validated_data.pop("password", "")
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
