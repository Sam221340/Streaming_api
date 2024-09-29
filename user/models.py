from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


# from location_field.models.plain import PlainLocationField
class Roles(models.Model):
    roles = models.CharField(max_length=30)

    def __str__(self):
        return self.roles


class User(AbstractUser):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=10, blank=True, null=True)
    role = models.ForeignKey(Roles, on_delete=models.CASCADE, default=3)

    def __str__(self):
        return self.username


# class Blog(models.Model):
#     title = models.CharField(max_length=100)
#     author = models.ForeignKey(User, on_delete=models.CASCADE)
#     description = models.TextField(blank=True, null=True)
#
#     def __str__(self):
#         return self.title


class Team(models.Model):
    team_name = models.CharField(max_length=100)

    def __str__(self):
        return self.team_name


class Player(models.Model):
    player_name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, related_name='team_players', on_delete=models.CASCADE)

    def __str__(self):
        return self.player_name


class Match(models.Model):
    uploaded_by = models.ForeignKey(User, on_delete= models.CASCADE)
    team1 = models.ForeignKey(Team, related_name="team_1", on_delete=models.CASCADE)
    team2 = models.ForeignKey(Team, related_name="team_2", on_delete=models.CASCADE)
    match_date = models.DateField()
    location = models.CharField(max_length=100)
    team1_players = models.ManyToManyField(Player, related_name= 'team1_players')
    team2_players = models.ManyToManyField(Player, related_name= 'team2_players')
    show = models.BooleanField(default= False)

    @property
    def is_upcoming(self):
        return self.match_date > timezone.now().date()

    def __str__(self):
        return f'{self.team1} vs {self.team2}'


def highlight_file_path(instance, filename):
    """Generate file path for uploaded highlight files."""
    return f'match_highlights/{instance.match.id}/{filename}'


class MatchHighlight(models.Model):
    match = models.ForeignKey('Match', related_name='highlights', on_delete=models.CASCADE)
    highlight = models.FileField(upload_to=highlight_file_path)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(auto_now_add=True)
    # highlight_url = models.URLField(blank=True)  # URL field to store the highlight file URL
    active = models.BooleanField(default=False)
    liked_by_user = models.ManyToManyField(User, related_name='liked_highlights', blank=True)
    testing = models.CharField(max_length=100, null=True, blank=True)
    views = models.IntegerField(null= True, blank= True)

    class Meta:
        verbose_name = 'Match Highlight'
        verbose_name_plural = 'Match Highlights'

    # def save(self, *args, **kwargs):
    #     """Override the save method to set the highlight_url."""
    #     if self.highlight and not self.highlight_url:
    #         # Generate the URL based on the file path
    #         self.highlight_url = self.get_highlight_url()
    #     super().save(*args, **kwargs)

    # def get_highlight_url(self):
    #     """Generate and return the URL for the uploaded highlight file."""
    #     if self.highlight:
    #         # Construct the absolute URL using settings.MEDIA_URL
    #         return f'{settings.MEDIA_URL}{self.highlight.name}'
    #     return ''

    def __str__(self):
        return f"{self.match} - {self.upload_date}"
