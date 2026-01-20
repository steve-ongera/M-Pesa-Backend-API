# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Transaction
from decimal import Decimal

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone_number', 'full_name', 'balance', 'created_at']
        read_only_fields = ['id', 'balance', 'created_at']


class RegisterSerializer(serializers.ModelSerializer):
    pin = serializers.CharField(write_only=True, min_length=4, max_length=6)
    confirm_pin = serializers.CharField(write_only=True, min_length=4, max_length=6)

    class Meta:
        model = User
        fields = ['phone_number', 'full_name', 'pin', 'confirm_pin']

    def validate(self, data):
        if data['pin'] != data['confirm_pin']:
            raise serializers.ValidationError({"pin": "PINs do not match"})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_pin')
        pin = validated_data.pop('pin')
        user = User.objects.create_user(
            phone_number=validated_data['phone_number'],
            full_name=validated_data['full_name'],
            pin=pin
        )
        return user


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    pin = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['phone_number'], password=data['pin'])
        if not user:
            raise serializers.ValidationError("Invalid phone number or PIN")
        if not user.is_active:
            raise serializers.ValidationError("Account is inactive")
        data['user'] = user
        return data


class TransactionSerializer(serializers.ModelSerializer):
    sender_phone = serializers.CharField(source='sender.phone_number', read_only=True)
    receiver_phone = serializers.CharField(source='receiver.phone_number', read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'transaction_code', 'sender_phone', 'receiver_phone', 
                  'amount', 'transaction_type', 'status', 'description', 'created_at']
        read_only_fields = ['id', 'transaction_code', 'status', 'created_at']


class SendMoneySerializer(serializers.Serializer):
    receiver_phone = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    description = serializers.CharField(required=False, allow_blank=True)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero")
        return value

    def validate_receiver_phone(self, value):
        try:
            User.objects.get(phone_number=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Receiver phone number not found")
        return value


class DepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    description = serializers.CharField(required=False, allow_blank=True)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero")
        if value > 300000:
            raise serializers.ValidationError("Maximum deposit amount is 300,000")
        return value


class WithdrawSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    description = serializers.CharField(required=False, allow_blank=True)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero")
        return value


class BalanceSerializer(serializers.Serializer):
    phone_number = serializers.CharField(read_only=True)
    balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    full_name = serializers.CharField(read_only=True)