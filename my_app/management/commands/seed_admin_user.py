# my_app/management/commands/seed_admin_user.py

from django.core.management.base import BaseCommand
from django.db import IntegrityError
from my_app.models import User


class Command(BaseCommand):
    help = "Seed an admin (superuser) account"

    def handle(self, *args, **options):
        phone_number = "+254757790687"
        pin = "1209"
        full_name = "System Administrator"

        try:
            if User.objects.filter(phone_number=phone_number).exists():
                self.stdout.write(
                    self.style.WARNING(
                        f"Admin user with phone {phone_number} already exists."
                    )
                )
                return

            user = User.objects.create_superuser(
                phone_number=phone_number,
                pin=pin,
                full_name=full_name,
            )

            self.stdout.write(
                self.style.SUCCESS(
                    "✅ Admin user created successfully!"
                )
            )
            self.stdout.write(f"📱 Phone: {phone_number}")
            self.stdout.write(f"🔐 PIN: {pin}")
            self.stdout.write("⚠️  Please change the PIN after first login.")

        except IntegrityError as e:
            self.stderr.write(
                self.style.ERROR(f"❌ Database error: {str(e)}")
            )
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"❌ Unexpected error: {str(e)}")
            )
