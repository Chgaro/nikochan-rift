from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.db.models import Count, Q
from .models import Season, Standing, Matchday, MatchdayScore, Sponsor

def home(request):
    seasons = Season.objects.order_by("-start_date")
    active_season = seasons.filter(is_active=True).first() or seasons.first()
    sponsors = Sponsor.objects.filter(is_active=True)

    stats = None
    if active_season:
        players_count = (
            MatchdayScore.objects
            .filter(season=active_season)
            .values("player_id")
            .distinct()
            .count()
        )

        matchdays_total = Matchday.objects.filter(season=active_season).count()
        matchdays_closed = Matchday.objects.filter(season=active_season, is_closed=True).count()

        leader = (
            Standing.objects
            .filter(season=active_season)
            .select_related("player")
            .order_by("-total_points", "player__display_name")
            .first()
        )

        stats = {
            "season_name": active_season.name,
            "players_count": players_count,
            "matchdays_closed": matchdays_closed,
            "matchdays_total": matchdays_total,
            "leader_name": leader.player.display_name if leader else None,
            "leader_points": leader.total_points if leader else None,
        }

    return render(request, "league/home.html", {
        "seasons": seasons,
        "active_season": active_season,
        "stats": stats,
        "twitch_channel": settings.TWITCH_CHANNEL,
        "twitch_parent": settings.TWITCH_PARENT,
        "sponsors": sponsors,
    })

def season_standings(request, season_id):
    season = get_object_or_404(Season, id=season_id)

    standings = (
        Standing.objects
        .filter(season=season)
        .select_related("player")
        .annotate(
            played=Count(
                "player__matchdayscore",
                filter=Q(player__matchdayscore__season=season),
                distinct=True,
            )
        )
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
    
def normativa(request):
    season = Season.objects.order_by("-id").first()
    return render(request, "league/normativa.html", {
        "season": season,
    })