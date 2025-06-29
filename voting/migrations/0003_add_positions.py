from django.db import migrations

def add_positions(apps, schema_editor):
    Position = apps.get_model('voting', 'Position')
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

def remove_positions(apps, schema_editor):
    Position = apps.get_model('voting', 'Position')
    Position.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('voting', '0002_remove_voter_is_verified_voter_photo_and_more'),
    ]

    operations = [
        migrations.RunPython(add_positions, remove_positions),
    ] 