import os
import django
import csv
from django.db import transaction

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elections.settings')
django.setup()

from voting.models import Ward, Constituency

def import_wards():
    """Import wards from CSV file with error handling"""
    csv_file = 'DATA/caw_1.csv'
    
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found!")
        return
    
    created_count = 0
    error_count = 0
    duplicate_count = 0
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            with transaction.atomic():  # Use transaction for data integrity
                for row_num, row in enumerate(reader, start=2):  # Start from 2 (header is row 1)
                    try:
                        constituency_code = str(row['constituency_code']).strip()
                        ward_code = str(row['caw_code']).strip()
                        ward_name = row['caw_name'].strip()
                        
                        # Check if constituency exists
                        try:
                            constituency = Constituency.objects.get(code=constituency_code)
                        except Constituency.DoesNotExist:
                            print(f"Row {row_num}: Constituency with code '{constituency_code}' not found for ward '{ward_name}'")
                            error_count += 1
                            continue
                        
                        # Check if ward already exists
                        if Ward.objects.filter(code=ward_code).exists():
                            print(f"Row {row_num}: Ward with code '{ward_code}' already exists - skipping")
                            duplicate_count += 1
                            continue
                        
                        # Create the ward
                        Ward.objects.create(
                            name=ward_name,
                            constituency=constituency,
                            code=ward_code
                        )
                        
                        created_count += 1
                        print(f"✓ Created: {ward_name} ({ward_code}) in {constituency.name}")
                        
                    except Exception as e:
                        error_count += 1
                        print(f"Row {row_num}: Error processing ward - {str(e)}")
                        print(f"  Row data: {row}")
                        
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
        return
    
    # Print summary
    print(f"\n=== Import Summary ===")
    print(f"✓ Created: {created_count} wards")
    print(f"⚠ Duplicates skipped: {duplicate_count} wards")
    print(f"✗ Errors: {error_count} rows")
    print(f"Total rows processed: {created_count + duplicate_count + error_count}")

if __name__ == "__main__":
    print("Starting ward import...")
    import_wards()
    print("Import completed!")