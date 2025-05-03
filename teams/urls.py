from django.urls import path
from . import views

urlpatterns = [
    # Home (with built-in lock‐screen in team_list)
    path('', views.team_list, name='team_list'),

    # Core pages
    path('team/<int:team_id>/', views.team_detail, name='team_detail'),
    path('player/<int:player_id>/<int:team_id>/', views.player_detail, name='player_detail'),
    path('compare/', views.compare_teams, name='compare_teams'),
    path('league/<int:league_id>/standings/', views.league_standings, name='league_standings'),
    path('league/ai/', views.league_ai, name='league_ai'),

    # AI Endpoints
    path('ask/', views.ask_ai, name='ask_ai'),
    path('ask/player/', views.ask_player_ai, name='ask_player_ai'),
    path('ask/compare/', views.ask_compare_ai, name='ask_compare_ai'),
    path('ask/league/', views.ask_league_ai, name='ask_league_ai'),

    # Trivia Game
    path('trivia/', views.trivia_quiz, name='trivia_quiz'),
    path('trivia/submit/', views.submit_trivia, name='submit_trivia'),
]