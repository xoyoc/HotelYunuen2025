from django.urls import path
from . import views

app_name = 'rooms'

urlpatterns = [
    path('', views.RoomTypeListView.as_view(), name='room_type_list'),
    path('<int:pk>/', views.RoomTypeDetailView.as_view(), name='room_type_detail'),
    path('check-availability/', views.CheckAvailabilityView.as_view(), name='check_availability'),
]