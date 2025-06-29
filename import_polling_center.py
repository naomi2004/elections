import os
import django
import csv

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elections.settings')
django.setup()

from voting.models import PollingCenter, Ward

def import_polling_centers():
    csv_file_path = 'DATA/polling_centre_1.csv'
    seen_codes = set()
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            code = row['polling_centre_code']
            if code in seen_codes:
                continue  # Skip duplicate codes within the CSV
            seen_codes.add(code)
            try:
                ward = Ward.objects.get(code=row['caw_code'])
                polling_center, created = PollingCenter.objects.update_or_create(
                    code=code,
                    defaults={
                        'name': row['polling_centre_name'],
                        'ward': ward
                    }
                )
                if created:
                    print(f"Created polling center: {row['polling_centre_name']}")
                else:
                    print(f"Updated polling center: {row['polling_centre_name']}")
            except Ward.DoesNotExist:
                print(f"Ward with code {row['caw_code']} does not exist")
            except Exception as e:
                print(f"Error processing polling center {row.get('polling_centre_name', 'UNKNOWN')}: {str(e)}")

if __name__ == '__main__':
    import_polling_centers() 