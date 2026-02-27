from django.db import models
from django.db.models import Sum


class Season(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    # Reglas parametrizables
    points_win = models.IntegerField(default=2)
    points_draw = models.IntegerField(default=1)
    points_loss = models.IntegerField(default=0)
    bonus_undefeated = models.IntegerField(default=1)

    top_matchdays_limit = models.IntegerField(default=8)

    def __str__(self):
        return self.name


class Player(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="players")
    display_name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.display_name


class Matchday(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="matchdays")
    number = models.IntegerField()
    date = models.DateField()
    is_closed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("season", "number")
        ordering = ["number"]

    def __str__(self):
        return f"{self.season.name} - Jornada {self.number}"


class Match(models.Model):
    RESULT_CHOICES = [
        ("A_WIN", "Jugador A gana"),
        ("DRAW", "Empate"),
        ("B_WIN", "Jugador B gana"),
    ]

    matchday = models.ForeignKey(Matchday, on_delete=models.CASCADE, related_name="matches")
    player_a = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="matches_as_a")
    player_b = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="matches_as_b")
    result = models.CharField(max_length=10, choices=RESULT_CHOICES)

    def __str__(self):
        return f"{self.player_a} vs {self.player_b}"


class MatchdayScore(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    matchday = models.ForeignKey(Matchday, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

    wins = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)

    points_base = models.IntegerField(default=0)
    bonus = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)

    class Meta:
        unique_together = ("matchday", "player")

    def __str__(self):
        return f"{self.player} - Jornada {self.matchday.number}"


class Standing(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

    total_points = models.IntegerField(default=0)

    class Meta:
        unique_together = ("season", "player")
        ordering = ["-total_points"]

    def __str__(self):
        return f"{self.player} - {self.total_points} pts"