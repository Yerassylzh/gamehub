from django.urls import path, include

from club import views

app_name = "club"

urlpatterns = [
    path("", views.home, name="homepage"),
    path("my_bookings/", views.bookings, name="my_bookings"),
    path("club_details/<int:pk>/", views.club_details, name="club_details"),
]
