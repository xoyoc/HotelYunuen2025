from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.BookingListView.as_view(), name='booking_list'),
    path('create/', views.BookingCreateView.as_view(), name='booking_create'),
    path('<uuid:booking_id>/', views.BookingDetailView.as_view(), name='booking_detail'),
    path('<uuid:booking_id>/cancel/', views.BookingCancelView.as_view(), name='booking_cancel'),
    path('<uuid:booking_id>/invoice/', views.BookingInvoiceView.as_view(), name='booking_invoice'),
]