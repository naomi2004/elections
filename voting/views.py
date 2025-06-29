from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count
from .models import (
    County, Constituency, Ward, PollingCenter, PollingStation,
    Position, Candidate, Voter, Vote, Party
)
from django.db.models.functions import TruncDate
from django.utils import timezone

def is_admin_user(user):
    return user.is_staff

def home(request):
    return render(request, 'voting/home.html')

def register(request):
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        id_number = request.POST.get('id_number')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Optional location fields
        county_id = request.POST.get('county')
        constituency_id = request.POST.get('constituency')
        ward_id = request.POST.get('ward')
        polling_center_id = request.POST.get('polling_center')
        polling_station_id = request.POST.get('polling_station')
        
        # Check if ID number already exists
        if Voter.objects.filter(id_number=id_number).exists():
            messages.error(request, 'A voter with this ID number is already registered.')
            return redirect('voting:register')
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'This username is already taken.')
            return redirect('voting:register')
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Create voter profile with optional location fields
            voter = Voter.objects.create(
                user=user,
                id_number=id_number,
                phone_number=phone_number,
                county_id=county_id if county_id else None,
                constituency_id=constituency_id if constituency_id else None,
                ward_id=ward_id if ward_id else None,
                polling_center_id=polling_center_id if polling_center_id else None,
                polling_station_id=polling_station_id if polling_station_id else None
            )
            
            messages.success(request, 'Registration successful. Please login.')
            return redirect('voting:login')
            
        except Exception as e:
            # If user was created but voter creation failed, delete the user
            if 'user' in locals():
                user.delete()
            messages.error(request, f'Registration failed: {str(e)}')
            return redirect('voting:register')
    
    counties = County.objects.all()
    return render(request, 'voting/register.html', {'counties': counties})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('voting:admin_dashboard')
            return redirect('voting:dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'voting/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('voting:home')

@login_required
def dashboard(request):
    if not hasattr(request.user, 'voter'):
        messages.error(request, 'You are not registered as a voter')
        return redirect('voting:home')
    
    voter = request.user.voter
    positions = Position.objects.all()
    votes = Vote.objects.filter(voter=voter)
    voted_positions = [vote.position for vote in votes]
    
    context = {
        'voter': voter,
        'positions': positions,
        'voted_positions': voted_positions
    }
    return render(request, 'voting/dashboard.html', context)

@login_required
def profile(request):
    if not hasattr(request.user, 'voter'):
        messages.error(request, 'You are not registered as a voter')
        return redirect('voting:home')
    
    voter = request.user.voter
    return render(request, 'voting/profile.html', {'voter': voter})

@login_required
def vote(request, position):
    if not hasattr(request.user, 'voter'):
        messages.error(request, 'You are not registered as a voter')
        return redirect('voting:home')
    
    voter = request.user.voter
    position_obj = get_object_or_404(Position, name=position)
    
    # Check if already voted for this position
    if Vote.objects.filter(voter=voter, position=position_obj).exists():
        messages.error(request, f'You have already voted for {position_obj.get_name_display()}')
        return redirect('voting:dashboard')
    
    # Get candidates based on position and voter's location
    candidates = Candidate.objects.filter(position=position_obj)
    if position == 'PRESIDENT':
        pass  # All voters can vote for president
    elif position in ['GOVERNOR', 'SENATOR', 'WOMEN_REP']:
        candidates = candidates.filter(county=voter.county)
    elif position == 'MP':
        candidates = candidates.filter(constituency=voter.constituency)
    else:  # MCA
        candidates = candidates.filter(ward=voter.ward)
    
    context = {
        'position': position_obj,
        'candidates': candidates
    }
    return render(request, 'voting/vote.html', context)

@login_required
def confirm_vote(request, candidate_id, position):
    if request.method == 'POST':
        voter = request.user.voter
        candidate = get_object_or_404(Candidate, id=candidate_id)
        position_obj = get_object_or_404(Position, name=position)
        
        # Final check if already voted
        if Vote.objects.filter(voter=voter, position=position_obj).exists():
            messages.error(request, f'You have already voted for {position_obj.get_name_display()}')
            return redirect('voting:dashboard')
        
        # Create vote
        Vote.objects.create(
            voter=voter,
            position=position_obj,
            candidate=candidate
        )
        
        messages.success(request, f'Your vote for {position_obj.get_name_display()} has been recorded')
        return redirect('voting:vote_success')
    
    candidate = get_object_or_404(Candidate, id=candidate_id)
    return render(request, 'voting/confirm_vote.html', {'candidate': candidate})

@login_required
def vote_success(request):
    return render(request, 'voting/vote_success.html')

# Ajax views for dependent dropdowns
def load_constituencies(request):
    county_id = request.GET.get('county')
    constituencies = Constituency.objects.filter(county_id=county_id).values('id', 'name')
    return JsonResponse(list(constituencies), safe=False)

def load_wards(request):
    constituency_id = request.GET.get('constituency')
    wards = Ward.objects.filter(constituency_id=constituency_id).values('id', 'name')
    return JsonResponse(list(wards), safe=False)

def load_polling_centers(request):
    ward_id = request.GET.get('ward')
    centers = PollingCenter.objects.filter(ward_id=ward_id).values('id', 'name')
    return JsonResponse(list(centers), safe=False)

def load_polling_stations(request):
    center_id = request.GET.get('center')
    stations = PollingStation.objects.filter(center_id=center_id).values('id', 'name')
    return JsonResponse(list(stations), safe=False)

# Admin views
@user_passes_test(is_admin_user)
def admin_dashboard(request):
    total_voters = Voter.objects.count()
    total_votes = Vote.objects.values('voter').distinct().count()
    total_candidates = Candidate.objects.count()
    
    # Votes by position
    position_stats = Position.objects.annotate(
        total_votes=Count('vote'),
        total_candidates=Count('candidate')
    )
    
    # Recent votes
    recent_votes = Vote.objects.select_related(
        'voter__user', 'position', 'candidate'
    ).order_by('-timestamp')[:10]
    
    # Registration trend
    registration_trend = Voter.objects.annotate(
        date=TruncDate('registration_date')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    context = {
        'total_voters': total_voters,
        'total_votes': total_votes,
        'total_candidates': total_candidates,
        'position_stats': position_stats,
        'recent_votes': recent_votes,
        'registration_trend': registration_trend
    }
    return render(request, 'voting/admin_dashboard.html', context)

def election_statistics(request):
    positions = Position.objects.all()
    stats = []
    
    for position in positions:
        position_stats = {
            'position': position,
            'total_votes': Vote.objects.filter(position=position).count(),
            'candidates': []
        }
        
        candidates = Candidate.objects.filter(position=position)
        for candidate in candidates:
            votes = Vote.objects.filter(position=position, candidate=candidate).count()
            position_stats['candidates'].append({
                'candidate': candidate,
                'votes': votes,
                'percentage': (votes / position_stats['total_votes'] * 100) if position_stats['total_votes'] > 0 else 0
            })
        
        # Sort candidates by votes
        position_stats['candidates'].sort(key=lambda x: x['votes'], reverse=True)
        stats.append(position_stats)
    
    context = {
        'stats': stats,
        'last_updated': timezone.now()
    }
    return render(request, 'voting/election_statistics.html', context)

@user_passes_test(is_admin_user)
def add_candidate(request):
    if request.method == 'POST':
        user = User.objects.create_user(
            username=request.POST['username'],
            email=request.POST['email'],
            password=request.POST['password'],
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name']
        )
        position = Position.objects.get(id=request.POST['position'])
        party = Party.objects.get(id=request.POST['party'])
        county = County.objects.get(id=request.POST['county']) if request.POST.get('county') else None
        constituency = Constituency.objects.get(id=request.POST['constituency']) if request.POST.get('constituency') else None
        ward = Ward.objects.get(id=request.POST['ward']) if request.POST.get('ward') else None
        
        # Handle photo upload
        photo = request.FILES.get('photo')
        
        Candidate.objects.create(
            user=user,
            position=position,
            party=party,
            county=county,
            constituency=constituency,
            ward=ward,
            photo=photo,
            bio=request.POST.get('bio', ''),
            manifesto=request.POST.get('manifesto', '')
        )
        messages.success(request, 'Candidate added successfully.')
        return redirect('voting:admin_dashboard')
    
    positions = Position.objects.all()
    parties = Party.objects.all()
    counties = County.objects.all()
    constituencies = Constituency.objects.all()
    wards = Ward.objects.all()
    return render(request, 'voting/add_candidate.html', {
        'positions': positions,
        'parties': parties,
        'counties': counties,
        'constituencies': constituencies,
        'wards': wards
    })

@user_passes_test(is_admin_user)
def add_party(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        abbreviation = request.POST.get('abbreviation')
        color = request.POST.get('color')
        description = request.POST.get('description')
        logo = request.FILES.get('logo')  # Get logo file from form

        Party.objects.create(
            name=name,
            abbreviation=abbreviation,
            color=color,
            description=description,
            logo=logo  # Save the logo file
        )
        messages.success(request, 'Party added successfully!')
        return redirect('voting:admin_dashboard')
    
    return render(request, 'voting/add_party.html')

def get_constituencies(request):
    county_id = request.GET.get('county_id')
    if county_id:
        constituencies = Constituency.objects.filter(county_id=county_id).values('id', 'name')
        return JsonResponse(list(constituencies), safe=False)
    return JsonResponse([], safe=False)

def get_wards(request):
    constituency_id = request.GET.get('constituency_id')
    if constituency_id:
        wards = Ward.objects.filter(constituency_id=constituency_id).values('id', 'name')
        return JsonResponse(list(wards), safe=False)
    return JsonResponse([], safe=False)
