from django.urls import path
from . import views

app_name = 'location_tracking'

urlpatterns = [
    path('map/', views.map_view, name='map_view'),
    path('update/', views.update_location, name='update'),
]
