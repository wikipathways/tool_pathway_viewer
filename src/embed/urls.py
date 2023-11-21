from django.urls import path

from . import views

urlpatterns = [
    path("<str:wpid>", views.embed, name="embed"),
    path("", views.help, name="help"),
]
