from django.db import transaction

from league.models import MatchdayScore, Standing


def recalc_matchday_scores(matchday):
    """
    Recalcula points_base/bonus/total_points de los MatchdayScore existentes
    para esa jornada (input manual W/D/L).
    """
    season = matchday.season
    W = season.points_win
    D = season.points_draw
    L = season.points_loss
    BONUS = season.bonus_undefeated

    qs = MatchdayScore.objects.filter(matchday=matchday).select_related("season")

    with transaction.atomic():
        for sc in qs:
            played = sc.wins + sc.draws + sc.losses
            points_base = (sc.wins * W) + (sc.draws * D) + (sc.losses * L)
            bonus = BONUS if (played > 0 and sc.losses == 0) else 0
            total = points_base + bonus

            MatchdayScore.objects.filter(pk=sc.pk).update(
                points_base=points_base,
                bonus=bonus,
                total_points=total,
                season=season,  # por seguridad, lo alineamos
            )


def rebuild_season_standings(season):
    """
    Standing.total_points = SUMA de las mejores N jornadas (top_matchdays_limit) por jugador.
    """
    limit = season.top_matchdays_limit

    scores = (
        MatchdayScore.objects
        .filter(season=season)
        .order_by("player_id", "-total_points", "matchday_id")
        .values_list("player_id", "total_points")
    )

    totals = {}
    counts = {}

    for player_id, pts in scores:
        if player_id not in totals:
            totals[player_id] = 0
            counts[player_id] = 0
        if counts[player_id] < limit:
            totals[player_id] += pts
            counts[player_id] += 1

    with transaction.atomic():
        Standing.objects.filter(season=season).delete()
        Standing.objects.bulk_create(
            [Standing(season=season, player_id=pid, total_points=total) for pid, total in totals.items()]
        )