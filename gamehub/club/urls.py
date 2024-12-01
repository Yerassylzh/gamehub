from django.urls import path, include

from club import views

app_name = "club"

urlpatterns = [
    path("", views.HomepageView.as_view(), name="homepage"),
    path("my_bookings/", views.BookingsView.as_view(), name="my_bookings"),
    path("club_details/<int:pk>/", views.ClubDetailsView.as_view(), name="club_details"),
]
