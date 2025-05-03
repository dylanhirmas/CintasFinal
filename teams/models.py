from django.db import models

class Team(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    founded_year = models.IntegerField()
    stadium_name = models.CharField(max_length=100)
    description = models.TextField()
    logo = models.ImageField(upload_to='team_logos/', null=True, blank=True)
    website = models.URLField(blank=True, null=True)
    api_football_id = models.IntegerField(null=True, blank=True)
    api_league_id = models.IntegerField(blank=True, null=True)
    background_image_url = models.URLField(blank=True, null=True)

    # ✅ Correct fields for Football-Data.org integration
    football_data_team_id = models.IntegerField(null=True, blank=True)
    football_data_league_code = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.name


class Player(models.Model):
    name = models.CharField(max_length=255)
    position = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players')
    goals = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    yellow_cards = models.IntegerField(default=0)
    red_cards = models.IntegerField(default=0)
    date_of_birth = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name


class TriviaQuestion(models.Model):
    question_text = models.TextField()
    choice_a      = models.CharField(max_length=255)
    choice_b      = models.CharField(max_length=255)
    choice_c      = models.CharField(max_length=255)
    choice_d      = models.CharField(max_length=255)

    CORRECT_CHOICES = [
        ('A', 'Choice A'),
        ('B', 'Choice B'),
        ('C', 'Choice C'),
        ('D', 'Choice D'),
    ]
    correct_choice = models.CharField(
        max_length=1,
        choices=CORRECT_CHOICES,
        help_text="Select the letter of the correct answer."
    )

    def __str__(self):
        # Truncate to first 50 chars for readability
        return self.question_text if len(self.question_text) <= 50 else self.question_text[:47] + '...'
