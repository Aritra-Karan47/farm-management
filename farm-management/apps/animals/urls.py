from django.urls import path
from apps.animals import views

app_name = "animals"

urlpatterns = [
    path("", views.animal_list, name="list"),
    path("<int:pk>/", views.animal_profile, name="profile"),
]
