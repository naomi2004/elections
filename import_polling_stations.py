import os
import django
import csv

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elections.settings')
django.setup()

from voting.models import PollingCenter, PollingStation

def import_polling_stations():
    csv_file_path = 'DATA/polling_station_1.csv'
    seen_codes = set()

    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            code = row.get('polling_station_code')
            name = row.get('polling_station_name')
            center_code = row.get('polling_centre_code')  # ✅ Correct column

            if not all([code, name, center_code]):
                print(f"Skipping row due to missing data: {row}")
                continue

            if code in seen_codes:
                continue
            seen_codes.add(code)

            try:
                polling_center = PollingCenter.objects.get(code=center_code)

                polling_station, created = PollingStation.objects.update_or_create(
                    code=code,
                    defaults={
                        'name': name,
                        'center': polling_center,  # ✅ per model field
                    }
                )

                action = "Created" if created else "Updated"
                print(f"{action} polling station: {name}")

            except PollingCenter.DoesNotExist:
                print(f"PollingCenter with code {center_code} does not exist for station {name}")
            except Exception as e:
                print(f"Error processing polling station {name or 'UNKNOWN'}: {str(e)}")

if __name__ == '__main__':
    import_polling_stations()
