from django.core.management.base import BaseCommand
from voting.models import Position

class Command(BaseCommand):
    help = 'Creates initial positions for the election'

    def handle(self, *args, **kwargs):
        positions = [
            ('PRESIDENT', 'President'),
            ('GOVERNOR', 'Governor'),
            ('SENATOR', 'Senator'),
            ('WOMEN_REP', 'Women Representative'),
            ('MP', 'Member of Parliament'),
            ('MCA', 'Member of County Assembly')
        ]

        for code, name in positions:
            Position.objects.get_or_create(
                name=code,
                defaults={'name': code}
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created position "{name}"')
            ) 