from rest_framework import serializers
from .models import AdminUser, User, Alarm, BatteryMonitoring, BeltTracking


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminUser
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        admin = AdminUser(**validated_data)
        if password:
            admin.set_password(password)
        admin.save()
        return admin

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            # Use Django's hashing or custom method if you wish
            user.password = password  # You may implement bcrypt too if needed
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.password = password
        instance.save()
        return instance


class AlarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alarm
        fields = '__all__'


class BatteryMonitoringSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatteryMonitoring
        fields = '__all__'


class BeltTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeltTracking
        fields = '__all__'
