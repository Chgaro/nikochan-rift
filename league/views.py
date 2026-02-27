from django.conf import settings
from django.shortcuts import get_object_or_404, render
from .models import Season, Standing, Matchday, MatchdayScore

def home(request):
    seasons = Season.objects.order_by("-start_date")
    active_season = seasons.filter(is_active=True).first()
    return render(request, "league/home.html", {
        "seasons": seasons,
        "active_season": active_season,
        "twitch_channel": settings.TWITCH_CHANNEL,
        "twitch_parent": settings.TWITCH_PARENT,
    })

def season_standings(request, season_id):
    season = get_object_or_404(Season, id=season_id)
    standings = (
        Standing.objects
        .filter(season=season)
        .select_related("player")
        .order_by("-total_points", "player__display_name")
    )
    return render(request, "league/season_standings.html", {"season": season, "standings": standings})


def matchday_list(request, season_id):
    season = get_object_or_404(Season, id=season_id)
    matchdays = (
        Matchday.objects
        .filter(season=season)
        .order_by("number")
    )
    return render(request, "league/matchday_list.html", {"season": season, "matchdays": matchdays})


def matchday_detail(request, season_id, matchday_id):
    season = get_object_or_404(Season, id=season_id)
    matchday = get_object_or_404(Matchday, id=matchday_id, season=season)

    scores = (
        MatchdayScore.objects
        .filter(matchday=matchday)
        .select_related("player")
        .order_by("-total_points", "player__display_name")
    )

    return render(
        request,
        "league/matchday_detail.html",
        {"season": season, "matchday": matchday, "scores": scores},
    )