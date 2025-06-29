from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from voting.models import Party, Position, County, Constituency, Ward

class Command(BaseCommand):
    help = 'Initialize the database with required data'

    def handle(self, *args, **kwargs):
        # Create a test party
        party, created = Party.objects.get_or_create(
            name="Test Party",
            defaults={
                'abbreviation': 'TP',
                'color': '#FF0000',
                'description': 'A test party'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created test party'))
        else:
            self.stdout.write(self.style.SUCCESS('Test party already exists'))

        # Create a test position
        position, created = Position.objects.get_or_create(
            name="Test Position",
            defaults={
                'description': 'A test position'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created test position'))
        else:
            self.stdout.write(self.style.SUCCESS('Test position already exists'))

        # Create a test county
        county, created = County.objects.get_or_create(
            name="Test County",
            defaults={
                'code': 'TC'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created test county'))
        else:
            self.stdout.write(self.style.SUCCESS('Test county already exists'))

        # Create a test constituency
        constituency, created = Constituency.objects.get_or_create(
            code='TC1',  # Use code as the unique identifier
            defaults={
                'name': 'Test Constituency',
                'county': county
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created test constituency'))
        else:
            self.stdout.write(self.style.SUCCESS('Test constituency already exists'))

        # Create a test ward
        ward, created = Ward.objects.get_or_create(
            code='TW1',  # Use code as the unique identifier
            defaults={
                'name': 'Test Ward',
                'constituency': constituency
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created test ward'))
        else:
            self.stdout.write(self.style.SUCCESS('Test ward already exists')) 