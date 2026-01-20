# my_app/management/commands/seed_data.py
from django.core.management.base import BaseCommand
from django.db import transaction
from my_app.models import User, Transaction
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Seeds the database with Kenyan user data and transactions'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database with Kenyan data...')
        
        with transaction.atomic():
            # Clear existing data
            self.stdout.write('Clearing existing data...')
            Transaction.objects.all().delete()
            User.objects.all().delete()
            
            # Create users with Kenyan phone numbers and names
            users_data = [
                {
                    'phone_number': '+254712345678',
                    'full_name': 'James Kamau',
                    'pin': '1234',
                    'balance': Decimal('15000.00')
                },
                {
                    'phone_number': '+254723456789',
                    'full_name': 'Mary Wanjiku',
                    'pin': '2345',
                    'balance': Decimal('25000.00')
                },
                {
                    'phone_number': '+254734567890',
                    'full_name': 'Peter Ochieng',
                    'pin': '3456',
                    'balance': Decimal('8500.00')
                },
                {
                    'phone_number': '+254745678901',
                    'full_name': 'Grace Akinyi',
                    'pin': '4567',
                    'balance': Decimal('32000.00')
                },
                {
                    'phone_number': '+254756789012',
                    'full_name': 'David Kipchoge',
                    'pin': '5678',
                    'balance': Decimal('12500.00')
                },
                {
                    'phone_number': '+254767890123',
                    'full_name': 'Faith Njeri',
                    'pin': '6789',
                    'balance': Decimal('45000.00')
                },
                {
                    'phone_number': '+254778901234',
                    'full_name': 'John Mwangi',
                    'pin': '7890',
                    'balance': Decimal('18000.00')
                },
                {
                    'phone_number': '+254789012345',
                    'full_name': 'Sarah Chebet',
                    'pin': '8901',
                    'balance': Decimal('22000.00')
                },
                {
                    'phone_number': '+254790123456',
                    'full_name': 'Michael Otieno',
                    'pin': '9012',
                    'balance': Decimal('9500.00')
                },
                {
                    'phone_number': '+254701234567',
                    'full_name': 'Lucy Wambui',
                    'pin': '0123',
                    'balance': Decimal('35000.00')
                },
                {
                    'phone_number': '+254722334455',
                    'full_name': 'Daniel Kimani',
                    'pin': '1122',
                    'balance': Decimal('28000.00')
                },
                {
                    'phone_number': '+254733445566',
                    'full_name': 'Anne Moraa',
                    'pin': '2233',
                    'balance': Decimal('16500.00')
                },
                {
                    'phone_number': '+254744556677',
                    'full_name': 'Robert Mutua',
                    'pin': '3344',
                    'balance': Decimal('42000.00')
                },
                {
                    'phone_number': '+254755667788',
                    'full_name': 'Catherine Wairimu',
                    'pin': '4455',
                    'balance': Decimal('19000.00')
                },
                {
                    'phone_number': '+254766778899',
                    'full_name': 'Brian Koech',
                    'pin': '5566',
                    'balance': Decimal('31000.00')
                },
                {
                    'phone_number': '+254777889900',
                    'full_name': 'Esther Nyambura',
                    'pin': '6677',
                    'balance': Decimal('14000.00')
                },
                {
                    'phone_number': '+254788990011',
                    'full_name': 'Joseph Omondi',
                    'pin': '7788',
                    'balance': Decimal('26500.00')
                },
                {
                    'phone_number': '+254799001122',
                    'full_name': 'Ruth Nduta',
                    'pin': '8899',
                    'balance': Decimal('38000.00')
                },
                {
                    'phone_number': '+254700112233',
                    'full_name': 'Patrick Kipruto',
                    'pin': '9900',
                    'balance': Decimal('21000.00')
                },
                {
                    'phone_number': '+254711223344',
                    'full_name': 'Jane Wangari',
                    'pin': '0011',
                    'balance': Decimal('17500.00')
                },
            ]
            
            # Create users
            self.stdout.write('Creating users...')
            created_users = []
            for user_data in users_data:
                user = User.objects.create_user(
                    phone_number=user_data['phone_number'],
                    full_name=user_data['full_name'],
                    pin=user_data['pin']
                )
                user.balance = user_data['balance']
                user.save()
                created_users.append(user)
                self.stdout.write(f'  ✓ Created user: {user.full_name} ({user.phone_number})')
            
            self.stdout.write(f'Successfully created {len(created_users)} users')
            
            # Create sample transactions
            self.stdout.write('\nCreating sample transactions...')
            
            transaction_descriptions = [
                'Groceries at Naivas',
                'Matatu fare',
                'Lunch at Java',
                'School fees payment',
                'Rent payment',
                'M-Pesa agent withdrawal',
                'Airtime purchase',
                'Electricity bill KPLC',
                'Water bill Nairobi Water',
                'Shopping at Tuskys',
                'Fuel at Kobil',
                'Salary advance',
                'Table banking contribution',
                'Chama contribution',
                'Medical bill',
                'Church offering',
                'Bodaboda fare',
                'Cyber cafe payment',
                'Internet bundle',
                'Movie tickets',
            ]
            
            transactions_created = 0
            
            # Create SEND transactions
            for _ in range(30):
                sender = random.choice(created_users)
                receiver = random.choice(created_users)
                
                # Don't send to self
                while receiver == sender:
                    receiver = random.choice(created_users)
                
                amount = Decimal(random.choice([50, 100, 200, 500, 1000, 1500, 2000, 3000, 5000]))
                
                # Only create transaction if sender has enough balance
                if sender.balance >= amount:
                    # Update balances
                    sender.balance -= amount
                    sender.save()
                    
                    receiver.balance += amount
                    receiver.save()
                    
                    # Create transaction
                    Transaction.objects.create(
                        sender=sender,
                        receiver=receiver,
                        amount=amount,
                        transaction_type='SEND',
                        status='COMPLETED',
                        description=random.choice(transaction_descriptions)
                    )
                    transactions_created += 1
            
            # Create DEPOSIT transactions
            for _ in range(15):
                user = random.choice(created_users)
                amount = Decimal(random.choice([1000, 2000, 5000, 10000, 15000, 20000]))
                
                user.balance += amount
                user.save()
                
                Transaction.objects.create(
                    receiver=user,
                    amount=amount,
                    transaction_type='DEPOSIT',
                    status='COMPLETED',
                    description='M-Pesa deposit from agent'
                )
                transactions_created += 1
            
            # Create WITHDRAW transactions
            for _ in range(15):
                user = random.choice(created_users)
                amount = Decimal(random.choice([500, 1000, 2000, 3000, 5000]))
                
                # Only withdraw if user has enough balance
                if user.balance >= amount:
                    user.balance -= amount
                    user.save()
                    
                    Transaction.objects.create(
                        sender=user,
                        amount=amount,
                        transaction_type='WITHDRAW',
                        status='COMPLETED',
                        description='ATM withdrawal'
                    )
                    transactions_created += 1
            
            self.stdout.write(f'Successfully created {transactions_created} transactions')
            
            # Create a test user for easy testing
            self.stdout.write('\nCreating test user...')
            test_user = User.objects.create_user(
                phone_number='+254700000000',
                full_name='Test User',
                pin='0000'
            )
            test_user.balance = Decimal('50000.00')
            test_user.save()
            
            self.stdout.write(self.style.SUCCESS('\n' + '='*60))
            self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
            self.stdout.write(self.style.SUCCESS('='*60))
            self.stdout.write(f'\nTotal Users Created: {User.objects.count()}')
            self.stdout.write(f'Total Transactions Created: {Transaction.objects.count()}')
            self.stdout.write('\n' + '-'*60)
            self.stdout.write('TEST USER CREDENTIALS:')
            self.stdout.write('-'*60)
            self.stdout.write(f'Phone: +254700000000')
            self.stdout.write(f'PIN: 0000')
            self.stdout.write(f'Balance: KES 50,000.00')
            self.stdout.write('-'*60)
            self.stdout.write('\nSample Users:')
            for user in created_users[:5]:
                self.stdout.write(f'  • {user.full_name}: {user.phone_number} (Balance: KES {user.balance:,.2f})')
            self.stdout.write('\nRun command: python manage.py seed_data')
            self.stdout.write(self.style.SUCCESS('\n✓ Ready to test your M-Pesa API!\n'))