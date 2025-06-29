import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elections.settings')
django.setup()

import csv
from voting.models import Constituency, County

with open('DATA/constituency_1.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        county = County.objects.get(code=row['county_code'])
        Constituency.objects.create(name=row['constituency_name'], county=county, code=row['constituency_code']) 