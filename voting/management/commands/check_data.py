from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from voting.models import Party, Position, County, Constituency, Ward, Candidate

class Command(BaseCommand):
    help = 'Check if we have all the necessary data'

    def handle(self, *args, **kwargs):
        # Check Users
        users = User.objects.all()
        self.stdout.write(f"Users: {users.count()}")
        for user in users:
            self.stdout.write(f"- {user.username} ({user.get_full_name()})")

        # Check Parties
        parties = Party.objects.all()
        self.stdout.write(f"\nParties: {parties.count()}")
        for party in parties:
            self.stdout.write(f"- {party.name} ({party.abbreviation})")

        # Check Positions
        positions = Position.objects.all()
        self.stdout.write(f"\nPositions: {positions.count()}")
        for position in positions:
            self.stdout.write(f"- {position.get_name_display()}")

        # Check Counties
        counties = County.objects.all()
        self.stdout.write(f"\nCounties: {counties.count()}")
        for county in counties:
            self.stdout.write(f"- {county.name} ({county.code})")

        # Check Constituencies
        constituencies = Constituency.objects.all()
        self.stdout.write(f"\nConstituencies: {constituencies.count()}")
        for constituency in constituencies:
            self.stdout.write(f"- {constituency.name} ({constituency.code}) - County: {constituency.county.name}")

        # Check Wards
        wards = Ward.objects.all()
        self.stdout.write(f"\nWards: {wards.count()}")
        for ward in wards:
            self.stdout.write(f"- {ward.name} ({ward.code}) - Constituency: {ward.constituency.name}")

        # Check Candidates
        candidates = Candidate.objects.all()
        self.stdout.write(f"\nCandidates: {candidates.count()}")
        for candidate in candidates:
            self.stdout.write(f"- {candidate.user.get_full_name()} - {candidate.position.get_name_display()}") 