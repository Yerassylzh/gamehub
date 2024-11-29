from django.urls import path, include

from authpage import views

app_name = "authpage"

urlpatterns = [
    path("", views.auth, name="authpage"),
]
