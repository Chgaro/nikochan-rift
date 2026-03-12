"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from pathlib import Path

from django.conf import settings
from django.contrib import admin
from django.http import FileResponse, Http404
from django.urls import include, path, re_path


def media_file(request, path):
    file_path = Path(settings.MEDIA_ROOT) / path
    if file_path.is_file():
        return FileResponse(open(file_path, "rb"))
    raise Http404("Media file not found")


urlpatterns = [
    path("admin/", admin.site.urls),
    re_path(r"^media/(?P<path>.*)$", media_file),
    path("", include("league.urls")),
]