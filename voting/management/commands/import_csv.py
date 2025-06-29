import csv
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from voting.models import (
    County, Constituency, Ward, PollingCenter, PollingStation,
    Party, Position, Candidate, Voter
)

class Command(BaseCommand):
    help = 'Import data from CSV files'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')
        parser.add_argument('model', type=str, help='Model to import data into')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        model_name = options['model'].lower()

        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                if model_name == 'county':
                    self.import_counties(reader)
                elif model_name == 'constituency':
                    self.import_constituencies(reader)
                elif model_name == 'ward':
                    self.import_wards(reader)
                elif model_name == 'pollingcenter':
                    self.import_polling_centers(reader)
                elif model_name == 'pollingstation':
                    self.import_polling_stations(reader)
                elif model_name == 'party':
                    self.import_parties(reader)
                elif model_name == 'position':
                    self.import_positions(reader)
                elif model_name == 'candidate':
                    self.import_candidates(reader)
                elif model_name == 'voter':
                    self.import_voters(reader)
                else:
                    self.stdout.write(self.style.ERROR(f'Unknown model: {model_name}'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {csv_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))

    def import_counties(self, reader):
        for row in reader:
            County.objects.get_or_create(
                name=row['county_name'],
                code=row['county_code']
            )
        self.stdout.write(self.style.SUCCESS('Successfully imported counties'))

    def import_constituencies(self, reader):
        for row in reader:
            county = County.objects.get(code=row['county_code'])
            Constituency.objects.get_or_create(
                name=row['constituency_name'],
                county=county,
                code=row['constituency_code']
            )
        self.stdout.write(self.style.SUCCESS('Successfully imported constituencies'))

    def import_wards(self, reader):
        for row in reader:
            constituency = Constituency.objects.get(code=row['constituency_code'])
            Ward.objects.get_or_create(
                name=row['ward_name'],
                constituency=constituency,
                code=row['ward_code']
            )
        self.stdout.write(self.style.SUCCESS('Successfully imported wards'))

    def import_polling_centers(self, reader):
        for row in reader:
            ward = Ward.objects.get(code=row['caw_code'])
            PollingCenter.objects.get_or_create(
                name=row['polling_centre_name'],
                ward=ward,
                code=row['polling_centre_code']
            )
        self.stdout.write(self.style.SUCCESS('Successfully imported polling centers'))

    def import_polling_stations(self, reader):
        for row in reader:
            center = PollingCenter.objects.get(code=row['polling_centre_code'])
            PollingStation.objects.get_or_create(
                name=f"{row['polling_station_name']} - Stream {row['stream']}",
                center=center,
                code=row['polling_station_code']
            )
        self.stdout.write(self.style.SUCCESS('Successfully imported polling stations'))

    def import_parties(self, reader):
        for row in reader:
            Party.objects.get_or_create(
                name=row['name'],
                abbreviation=row['abbreviation'],
                color=row.get('color', '#000000'),
                logo=row.get('logo', ''),
                description=row.get('description', '')
            )
        self.stdout.write(self.style.SUCCESS('Successfully imported parties'))

    def import_positions(self, reader):
        for row in reader:
            Position.objects.get_or_create(
                name=row['name'],
                description=row.get('description', '')
            )
        self.stdout.write(self.style.SUCCESS('Successfully imported positions'))

    def import_candidates(self, reader):
        for row in reader:
            # Create user if not exists
            user, _ = User.objects.get_or_create(
                username=row['username'],
                defaults={
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'email': row['email']
                }
            )
            user.set_password(row['password'])
            user.save()

            # Get related objects
            position = Position.objects.get(name=row['position'])
            party = Party.objects.get(abbreviation=row['party'])
            county = County.objects.get(code=row['county_code']) if row.get('county_code') else None
            constituency = Constituency.objects.get(code=row['constituency_code']) if row.get('constituency_code') else None
            ward = Ward.objects.get(code=row['ward_code']) if row.get('ward_code') else None

            # Create candidate
            Candidate.objects.get_or_create(
                user=user,
                position=position,
                party=party,
                county=county,
                constituency=constituency,
                ward=ward,
                photo=row.get('photo', ''),
                bio=row.get('bio', ''),
                manifesto=row.get('manifesto', '')
            )
        self.stdout.write(self.style.SUCCESS('Successfully imported candidates'))

    def import_voters(self, reader):
        for row in reader:
            # Create user if not exists
            user, _ = User.objects.get_or_create(
                username=row['username'],
                defaults={
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'email': row['email']
                }
            )
            user.set_password(row['password'])
            user.save()

            # Get related objects
            county = County.objects.get(code=row['county_code']) if row.get('county_code') else None
            constituency = Constituency.objects.get(code=row['constituency_code']) if row.get('constituency_code') else None
            ward = Ward.objects.get(code=row['ward_code']) if row.get('ward_code') else None
            polling_center = PollingCenter.objects.get(code=row['center_code']) if row.get('center_code') else None
            polling_station = PollingStation.objects.get(code=row['station_code']) if row.get('station_code') else None

            # Create voter
            Voter.objects.get_or_create(
                user=user,
                id_number=row['id_number'],
                phone_number=row['phone_number'],
                photo=row.get('photo', ''),
                county=county,
                constituency=constituency,
                ward=ward,
                polling_center=polling_center,
                polling_station=polling_station
            )
        self.stdout.write(self.style.SUCCESS('Successfully imported voters')) 