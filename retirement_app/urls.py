from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("over/", views.over, name="over"),
    path("reset/", views.reset, name="reset"),
]
