import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elections.settings')
django.setup()

import csv
from voting.models import Ward, Constituency

with open('DATA/caw_1.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        constituency = Constituency.objects.get(code=row['constituency_code'])
        Ward.objects.create(name=row['caw_name'], constituency=constituency, code=row['caw_code']) 