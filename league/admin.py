from django.contrib import admin
from django.db import transaction

from .models import Season, Player, Matchday, Match, MatchdayScore, Standing
from .services.standings import recalc_matchday_scores, rebuild_season_standings


# ---------- Inlines ----------

class MatchdayScoreInline(admin.TabularInline):
    """
    Entrada manual por jugador y jornada:
    wins/draws/losses se editan; points_base/bonus/total_points son de solo lectura.
    """
    model = MatchdayScore
    extra = 0
    autocomplete_fields = ("player",)
    fields = ("player", "wins", "losses", "draws", "points_base", "bonus", "total_points")
    readonly_fields = ("points_base", "bonus", "total_points")

    def has_add_permission(self, request, obj=None):
        # obj es el Matchday
        if obj and obj.is_closed:
            return False
        return super().has_add_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if obj and obj.is_closed:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_closed:
            return False
        return super().has_delete_permission(request, obj)


# ---------- Admins ----------

@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "start_date",
        "end_date",
        "is_active",
        "points_win",
        "points_draw",
        "points_loss",
        "bonus_undefeated",
        "top_matchdays_limit",
    )
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("display_name", "season", "active")
    list_filter = ("season", "active")
    search_fields = ("display_name",)
    autocomplete_fields = ("season",)


@admin.register(Matchday)
class MatchdayAdmin(admin.ModelAdmin):
    list_display = ("season", "number", "date", "is_closed")
    list_filter = ("season", "is_closed")
    search_fields = ("season__name",)
    autocomplete_fields = ("season",)
    inlines = [MatchdayScoreInline]
    actions = ("close_matchdays_and_rebuild", "reopen_matchdays", "rebuild_selected_matchdays")
    
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for obj in instances:
            if isinstance(obj, MatchdayScore):
                obj.matchday = form.instance
                obj.season = form.instance.season
            obj.save()

        # Borra los que se hayan marcado para borrar
        for obj in formset.deleted_objects:
            obj.delete()

        formset.save_m2m()

    @admin.action(description="Cerrar jornada(s) seleccionadas y recalcular puntos/standings")
    def close_matchdays_and_rebuild(self, request, queryset):
        with transaction.atomic():
            seasons_to_rebuild = set()

            for md in queryset.select_related("season"):
                md.is_closed = True
                md.save(update_fields=["is_closed"])

                # recalcula puntos de esa jornada a partir de W/D/L (input manual)
                recalc_matchday_scores(md)

                seasons_to_rebuild.add(md.season_id)

            # rebuild standings (top N) por season
            for season_id in seasons_to_rebuild:
                season = Season.objects.get(id=season_id)
                rebuild_season_standings(season)

        self.message_user(request, "Jornadas cerradas y standings recalculados.")

    @admin.action(description="Reabrir jornada(s) seleccionadas (permitir editar)")
    def reopen_matchdays(self, request, queryset):
        queryset.update(is_closed=False)
        self.message_user(request, "Jornadas reabiertas.")

    @admin.action(description="Recalcular puntos/standings de jornada(s) seleccionadas")
    def rebuild_selected_matchdays(self, request, queryset):
        with transaction.atomic():
            seasons_to_rebuild = set()

            for md in queryset.select_related("season"):
                recalc_matchday_scores(md)
                seasons_to_rebuild.add(md.season_id)

            for season_id in seasons_to_rebuild:
                season = Season.objects.get(id=season_id)
                rebuild_season_standings(season)

        self.message_user(request, "Recalculo completado.")


@admin.register(MatchdayScore)
class MatchdayScoreAdmin(admin.ModelAdmin):
    list_display = (
        "season",
        "matchday",
        "player",
        "wins",
        "draws",
        "losses",
        "points_base",
        "bonus",
        "total_points",
    )
    list_filter = ("season", "matchday")
    search_fields = ("player__display_name", "season__name")
    autocomplete_fields = ("season", "matchday", "player")


@admin.register(Standing)
class StandingAdmin(admin.ModelAdmin):
    list_display = ("season", "player", "total_points")
    list_filter = ("season",)
    search_fields = ("player__display_name", "season__name")
    autocomplete_fields = ("season", "player")


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    """
    Se mantiene por si en el futuro quieres registrar emparejamientos reales.
    En v1 no lo usamos para calcular nada.
    """
    list_display = ("matchday", "player_a", "player_b", "result")
    list_filter = ("matchday__season", "matchday")
    search_fields = ("player_a__display_name", "player_b__display_name")
    autocomplete_fields = ("matchday", "player_a", "player_b")