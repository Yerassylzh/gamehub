from django.urls import path

from authpage import views

app_name = "authpage"

urlpatterns = [
    path("", views.AuthpageView.as_view(), name="authpage"),
]
