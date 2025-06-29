from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import (
    County, Constituency, Ward, PollingCenter, PollingStation,
    Party, Position, Voter, Candidate, Vote
)
from django.core.exceptions import ValidationError
import logging
import traceback

logger = logging.getLogger(__name__)

@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(Constituency)
class ConstituencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'county', 'code')
    list_filter = ('county',)
    search_fields = ('name', 'code')

@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ('name', 'constituency', 'code')
    list_filter = ('constituency__county', 'constituency')
    search_fields = ('name', 'code')

@admin.register(PollingCenter)
class PollingCenterAdmin(admin.ModelAdmin):
    list_display = ('name', 'ward', 'code')
    list_filter = ('ward__constituency__county', 'ward__constituency', 'ward')
    search_fields = ('name', 'code')

@admin.register(PollingStation)
class PollingStationAdmin(admin.ModelAdmin):
    list_display = ('name', 'center', 'code')
    list_filter = ('center__ward__constituency__county', 'center__ward__constituency', 'center__ward', 'center')
    search_fields = ('name', 'code')

class PartyAdminForm(forms.ModelForm):
    class Meta:
        model = Party
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'abbreviation': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    class Media:
        css = {
            'all': ('admin/css/widgets.css',)
        }
        js = (
            'admin/js/core.js',
            'admin/js/vendor/jquery/jquery.js',
            'admin/js/jquery.init.js',
        )

@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    form = PartyAdminForm
    list_display = ('name', 'abbreviation', 'color', 'description')
    search_fields = ('name', 'abbreviation')
    list_filter = ('name',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'abbreviation', 'color')
        }),
        ('Additional Information', {
            'fields': ('logo', 'description'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('get_name_display', 'description')
    search_fields = ('name',)
    list_filter = ('name',)
    fieldsets = (
        ('Position Details', {
            'fields': ('name', 'description')
        }),
    )

@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):
    list_display = ('user', 'id_number', 'phone_number', 'registration_date')
    list_filter = ('registration_date', 'county', 'constituency', 'ward')
    search_fields = ('user__username', 'id_number', 'phone_number')
    readonly_fields = ('registration_date',)
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'id_number', 'phone_number', 'photo')
        }),
        ('Location Information', {
            'fields': ('county', 'constituency', 'ward', 'polling_center', 'polling_station')
        }),
        ('Registration Information', {
            'fields': ('registration_date',),
            'classes': ('collapse',)
        }),
    )

class CandidateAdminForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = '__all__'
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-control'}),
            'party': forms.Select(attrs={'class': 'form-control'}),
            'county': forms.Select(attrs={'class': 'form-control'}),
            'constituency': forms.Select(attrs={'class': 'form-control'}),
            'ward': forms.Select(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'manifesto': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }

    class Media:
        css = {
            'all': ('admin/css/widgets.css',)
        }
        js = (
            'admin/js/core.js',
            'admin/js/vendor/jquery/jquery.js',
            'admin/js/jquery.init.js',
            'admin/js/SelectBox.js',
            'admin/js/SelectFilter2.js',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            if self.instance and self.instance.pk:
                # Editing an existing candidate - filter based on saved data
                self.fields['constituency'].queryset = Constituency.objects.filter(county=self.instance.county)
                self.fields['ward'].queryset = Ward.objects.filter(constituency=self.instance.constituency)
            elif 'county' in self.data:
                # Adding a new candidate with form data - filter based on submitted data
                try:
                    county_id = int(self.data.get('county'))
                    self.fields['constituency'].queryset = Constituency.objects.filter(county_id=county_id)
                except (ValueError, TypeError):
                    self.fields['constituency'].queryset = Constituency.objects.none()

                try:
                    constituency_id = int(self.data.get('constituency'))
                    self.fields['ward'].queryset = Ward.objects.filter(constituency_id=constituency_id)
                except (ValueError, TypeError):
                    self.fields['ward'].queryset = Ward.objects.none()
            else:
                # No data available - show empty dropdowns
                self.fields['constituency'].queryset = Constituency.objects.none()
                self.fields['ward'].queryset = Ward.objects.none()
        except Exception as e:
            logger.error(f"Error in CandidateAdminForm.__init__: {str(e)}")
            logger.error(traceback.format_exc())

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    form = CandidateAdminForm
    list_display = ('user', 'position', 'party', 'county', 'constituency', 'ward')
    list_filter = ('position', 'party', 'county', 'constituency', 'ward')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')

    class Media:
        js = (
            'admin/js/vendor/jquery/jquery.js',
            'admin/js/jquery.init.js',
            'js/candidate_admin_v2.js',
        )

    def get_form(self, request, obj=None, **kwargs):
        try:
            return super().get_form(request, obj, **kwargs)
        except Exception as e:
            logger.error(f"Error in CandidateAdmin.get_form: {str(e)}\n{traceback.format_exc()}")
            raise

    def save_model(self, request, obj, form, change):
        try:
            super().save_model(request, obj, form, change)
        except Exception as e:
            logger.error(f"Error in CandidateAdmin.save_model: {str(e)}\n{traceback.format_exc()}")
            raise

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('voter', 'position', 'candidate', 'timestamp')
    list_filter = ('position', 'timestamp')
    search_fields = ('voter__user__username', 'position__name', 'candidate__user__username')
    readonly_fields = ('timestamp',)
    fieldsets = (
        ('Vote Information', {
            'fields': ('voter', 'position', 'candidate')
        }),
        ('Timestamp', {
            'fields': ('timestamp',),
            'classes': ('collapse',)
        }),
    ) 