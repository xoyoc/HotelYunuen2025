"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # Páginas principales
    path('', views.HomeView.as_view(), name='home'),
    path('galeria/', views.GalleryView.as_view(), name='gallery'),
    path('tarifas/', views.RatesView.as_view(), name='rates'),
    path('ubicacion/', views.LocationView.as_view(), name='location'),
    path('acerca-de/', views.AboutView.as_view(), name='about'),
    path('contacto/', views.ContactView.as_view(), name='contact'),
    
    # AJAX endpoints
    path('ajax/check-availability/', views.check_availability_ajax, name='check_availability_ajax'),
    
    # Apps
    path('habitaciones/', include('rooms.urls')),
    path('reservaciones/', include('bookings.urls')),
    path('resenas/', include('reviews.urls')),
    
    # Admin
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Personalización del admin
admin.site.site_header = "Hotel Yunuen - Administración"
admin.site.site_title = "Hotel Yunuen Admin"
admin.site.index_title = "Panel de Administración"