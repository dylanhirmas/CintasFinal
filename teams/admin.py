from django.contrib import admin
from .models import Team, Player

class TeamAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'country', 'founded_year', 'stadium_name',
        'api_football_id', 'api_league_id',
        'football_data_team_id', 'football_data_league_code'
    )
    search_fields = ('name', 'country', 'football_data_team_id', 'football_data_league_code')
    list_filter = ('country',)
    fields = (
        'name', 'country', 'founded_year', 'stadium_name', 'description',
        'logo', 'website', 'background_image_url',
        'api_football_id', 'api_league_id',
        'football_data_team_id', 'football_data_league_code'
    )

class PlayerAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'position', 'team', 'goals', 'assists',
        'yellow_cards', 'red_cards'
    )
    search_fields = ('name', 'position', 'team__name')
    list_filter = ('team', 'position', 'nationality')

admin.site.register(Team, TeamAdmin)
admin.site.register(Player, PlayerAdmin)
