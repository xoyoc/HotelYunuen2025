from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('', views.ReviewListView.as_view(), name='review_list'),
    path('create/', views.ReviewCreateView.as_view(), name='review_create'),
    path('<int:pk>/', views.ReviewDetailView.as_view(), name='review_detail'),
    path('<int:pk>/helpful/', views.MarkReviewHelpfulView.as_view(), name='mark_helpful'),
    path('hotel/<slug:hotel_slug>/', views.HotelReviewsView.as_view(), name='hotel_reviews'),
]