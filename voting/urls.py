from django.urls import path
from . import views

app_name = 'voting'

urlpatterns = [
    # Authentication URLs
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Voter Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    
    # Voting URLs
    path('vote/<str:position>/', views.vote, name='vote'),
    path('confirm-vote/<int:candidate_id>/<str:position>/', views.confirm_vote, name='confirm_vote'),
    path('vote-success/', views.vote_success, name='vote_success'),
    
    # Ajax endpoints for dependent dropdowns
    path('load-constituencies/', views.load_constituencies, name='load_constituencies'),
    path('load-wards/', views.load_wards, name='load_wards'),
    path('load-polling-centers/', views.load_polling_centers, name='load_polling_centers'),
    path('load-polling-stations/', views.load_polling_stations, name='load_polling_stations'),
    
    # Admin Dashboard URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('election-statistics/', views.election_statistics, name='election_statistics'),
    path('add-candidate/', views.add_candidate, name='add_candidate'),
    path('admin/add-party/', views.add_party, name='add_party'),
] 