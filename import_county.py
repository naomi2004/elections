import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elections.settings')
django.setup()

import csv
from voting.models import County

with open('DATA/county_1.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        County.objects.create(name=row['county_name'], code=row['county_code']) 