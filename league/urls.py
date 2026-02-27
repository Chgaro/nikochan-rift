from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("season/<int:season_id>/", views.season_standings, name="season_standings"),
    path("season/<int:season_id>/matchdays/", views.matchday_list, name="matchday_list"),
    path("season/<int:season_id>/matchdays/<int:matchday_id>/", views.matchday_detail, name="matchday_detail"),
]