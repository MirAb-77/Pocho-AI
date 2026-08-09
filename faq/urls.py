from django.urls import path

from . import views

app_name = "faq"

urlpatterns = [
    path("", views.home, name="home"),
    path("chat/", views.index, name="chat"),
    path("ask/", views.ask, name="ask"),
]
