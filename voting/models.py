from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import FileExtensionValidator

class Party(models.Model):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=10)
    color = models.CharField(max_length=7, default="#000000")  # Hex color code
    logo = models.FileField(
        upload_to='party_logos/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.abbreviation})"

    class Meta:
        verbose_name_plural = "Parties"

class County(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Counties"

class Constituency(models.Model):
    name = models.CharField(max_length=100)
    county = models.ForeignKey(County, on_delete=models.CASCADE)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.name} ({self.county.name})"

    class Meta:
        verbose_name_plural = "Constituencies"

class Ward(models.Model):
    name = models.CharField(max_length=100)
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.name} ({self.constituency.name})"

class PollingCenter(models.Model):
    name = models.CharField(max_length=100)
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.name} ({self.ward.name})"

class PollingStation(models.Model):
    name = models.CharField(max_length=100)
    center = models.ForeignKey(PollingCenter, on_delete=models.CASCADE)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.name} ({self.center.name})"

class Position(models.Model):
    POSITION_CHOICES = [
        ('PRESIDENT', 'President'),
        ('GOVERNOR', 'Governor'),
        ('SENATOR', 'Senator'),
        ('WOMEN_REP', 'Women Representative'),
        ('MP', 'Member of Parliament'),
        ('MCA', 'Member of County Assembly'),
    ]
    
    name = models.CharField(max_length=20, choices=POSITION_CHOICES, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.get_name_display()

class Candidate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    county = models.ForeignKey(County, on_delete=models.CASCADE)
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE, null=True, blank=True)
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, null=True, blank=True)
    bio = models.TextField(blank=True)
    manifesto = models.TextField(blank=True)
    photo = models.FileField(
        upload_to='candidate_photos/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    votes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.position.get_name_display()}"

class Voter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_number = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=15)
    photo = models.CharField(max_length=255, blank=True, null=True)
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, blank=True)
    constituency = models.ForeignKey(Constituency, on_delete=models.SET_NULL, null=True, blank=True)
    ward = models.ForeignKey(Ward, on_delete=models.SET_NULL, null=True, blank=True)
    polling_center = models.ForeignKey(PollingCenter, on_delete=models.SET_NULL, null=True, blank=True)
    polling_station = models.ForeignKey(PollingStation, on_delete=models.SET_NULL, null=True, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.id_number}"

class Vote(models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('voter', 'position')

    def __str__(self):
        return f"{self.voter.user.get_full_name()} voted for {self.candidate.user.get_full_name()} as {self.position.get_name_display()}"
