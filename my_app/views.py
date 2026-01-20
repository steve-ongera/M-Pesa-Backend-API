# accounts/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.db import transaction as db_transaction
from .models import User, Transaction
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer,
    TransactionSerializer, SendMoneySerializer,
    DepositSerializer, WithdrawSerializer, BalanceSerializer
)


class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'User registered successfully',
                'token': token.key,
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'Login successful',
                'token': token.key,
                'user': UserSerializer(user).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        request.user.auth_token.delete()
        return Response({'message': 'Logout successful'})


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.filter(
            sender=user
        ) | Transaction.objects.filter(receiver=user)

    @action(detail=False, methods=['post'])
    def send_money(self, request):
        serializer = SendMoneySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        sender = request.user
        receiver_phone = serializer.validated_data['receiver_phone']
        amount = serializer.validated_data['amount']
        description = serializer.validated_data.get('description', '')

        # Check if sending to self
        if sender.phone_number == receiver_phone:
            return Response({
                'error': 'Cannot send money to yourself'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check sufficient balance
        if sender.balance < amount:
            return Response({
                'error': 'Insufficient balance'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            receiver = User.objects.get(phone_number=receiver_phone)
        except User.DoesNotExist:
            return Response({
                'error': 'Receiver not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Perform transaction
        with db_transaction.atomic():
            # Deduct from sender
            sender.balance -= amount
            sender.save()

            # Add to receiver
            receiver.balance += amount
            receiver.save()

            # Create transaction record
            txn = Transaction.objects.create(
                sender=sender,
                receiver=receiver,
                amount=amount,
                transaction_type='SEND',
                status='COMPLETED',
                description=description
            )

        return Response({
            'message': 'Money sent successfully',
            'transaction': TransactionSerializer(txn).data,
            'new_balance': sender.balance
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def deposit(self, request):
        serializer = DepositSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        amount = serializer.validated_data['amount']
        description = serializer.validated_data.get('description', 'Deposit')

        with db_transaction.atomic():
            user.balance += amount
            user.save()

            txn = Transaction.objects.create(
                receiver=user,
                amount=amount,
                transaction_type='DEPOSIT',
                status='COMPLETED',
                description=description
            )

        return Response({
            'message': 'Deposit successful',
            'transaction': TransactionSerializer(txn).data,
            'new_balance': user.balance
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def withdraw(self, request):
        serializer = WithdrawSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        amount = serializer.validated_data['amount']
        description = serializer.validated_data.get('description', 'Withdrawal')

        if user.balance < amount:
            return Response({
                'error': 'Insufficient balance'
            }, status=status.HTTP_400_BAD_REQUEST)

        with db_transaction.atomic():
            user.balance -= amount
            user.save()

            txn = Transaction.objects.create(
                sender=user,
                amount=amount,
                transaction_type='WITHDRAW',
                status='COMPLETED',
                description=description
            )

        return Response({
            'message': 'Withdrawal successful',
            'transaction': TransactionSerializer(txn).data,
            'new_balance': user.balance
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def balance(self, request):
        user = request.user
        serializer = BalanceSerializer({
            'phone_number': user.phone_number,
            'balance': user.balance,
            'full_name': user.full_name
        })
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def history(self, request):
        transactions = self.get_queryset()[:20]  # Last 20 transactions
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)