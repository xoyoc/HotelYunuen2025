from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from bookings.models import Hotel
from rooms.models import RoomType, Amenity
from reviews.models import ReviewAndRating, HotelStatistics


class HomeView(TemplateView):
    """Vista principal del sitio web"""
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener el hotel principal (asumiendo que es el primero)
        hotel = Hotel.objects.filter(is_active=True).first()
        
        # Obtener habitaciones destacadas (las más baratas de cada categoría)
        featured_rooms = RoomType.objects.filter(is_active=True).order_by('category', 'price_per_night')[:6]
        
        # Obtener reseñas destacadas
        featured_reviews = ReviewAndRating.objects.filter(
            is_active=True, 
            rating__gte=4
        ).select_related('user', 'hotel')[:3]
        
        # Estadísticas del hotel
        if hotel:
            stats = HotelStatistics.objects.filter(hotel=hotel).first()
        else:
            stats = None
        
        context.update({
            'hotel': hotel,
            'featured_rooms': featured_rooms,
            'featured_reviews': featured_reviews,
            'stats': stats,
        })
        
        return context


class GalleryView(TemplateView):
    """Vista de galería de imágenes del hotel"""
    template_name = 'gallery.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener habitaciones con imágenes
        room_types = RoomType.objects.filter(
            is_active=True, 
            image__isnull=False
        ).exclude(image='')
        
        # Organizar por categorías
        gallery_items = []
        for room_type in room_types:
            gallery_items.append({
                'image': room_type.image,
                'title': room_type.name,
                'description': room_type.description,
                'category': room_type.get_category_display(),
                'price': room_type.price_per_night
            })
        
        context['gallery_items'] = gallery_items
        return context


class RatesView(TemplateView):
    """Vista de tarifas del hotel"""
    template_name = 'rates.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener todas las habitaciones activas organizadas por categoría
        room_types = RoomType.objects.filter(is_active=True).order_by('category', 'price_per_night')
        
        # Agrupar por categoría
        rooms_by_category = {}
        for room_type in room_types:
            category = room_type.get_category_display()
            if category not in rooms_by_category:
                rooms_by_category[category] = []
            rooms_by_category[category].append(room_type)
        
        context['rooms_by_category'] = rooms_by_category
        return context


class LocationView(TemplateView):
    """Vista de ubicación del hotel"""
    template_name = 'location.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener información del hotel
        hotel = Hotel.objects.filter(is_active=True).first()
        context['hotel'] = hotel
        
        # Información adicional sobre la ubicación
        context.update({
            'nearby_attractions': [
                {
                    'name': 'Playa Azul',
                    'distance': '15 km',
                    'description': 'Hermosa playa con arena dorada y aguas tranquilas'
                },
                {
                    'name': 'Puerto de Lázaro Cárdenas',
                    'distance': '2 km',
                    'description': 'Puerto comercial e industrial más importante del Pacífico'
                },
                {
                    'name': 'Zihuatanejo',
                    'distance': '45 km',
                    'description': 'Destino turístico con playas paradisíacas'
                },
                {
                    'name': 'Ixtapa',
                    'distance': '50 km',
                    'description': 'Centro turístico con hoteles de lujo y campos de golf'
                }
            ]
        })
        
        return context


class AboutView(TemplateView):
    """Vista acerca del hotel"""
    template_name = 'about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        hotel = Hotel.objects.filter(is_active=True).first()
        context['hotel'] = hotel
        
        # Información adicional del hotel
        context.update({
            'hotel_features': [
                {
                    'icon': 'fas fa-wifi',
                    'title': 'WiFi Gratuito',
                    'description': 'Internet de alta velocidad en todo el hotel'
                },
                {
                    'icon': 'fas fa-parking',
                    'title': 'Estacionamiento',
                    'description': 'Estacionamiento gratuito para huéspedes'
                },
                {
                    'icon': 'fas fa-concierge-bell',
                    'title': 'Servicio 24/7',
                    'description': 'Atención al cliente las 24 horas'
                },
                {
                    'icon': 'fas fa-utensils',
                    'title': 'Restaurante',
                    'description': 'Gastronomía local e internacional'
                },
                {
                    'icon': 'fas fa-cocktail',
                    'title': 'Video Bar',
                    'description': 'Bar con ambiente nocturno'
                },
                {
                    'icon': 'fas fa-briefcase',
                    'title': 'Centro de Negocios',
                    'description': 'Facilidades para viajeros de negocios'
                }
            ],
            'hotel_history': {
                'established': '1995',
                'mission': 'Brindar hospitalidad excepcional en el corazón de Lázaro Cárdenas, combinando confort, ubicación estratégica y el cálido servicio michoacano.',
                'vision': 'Ser el hotel de referencia en Lázaro Cárdenas para viajeros de negocios y turismo, reconocido por nuestra excelencia en servicio y ubicación privilegiada.'
            }
        })
        
        return context


class ContactView(TemplateView):
    """Vista de contacto con formulario"""
    template_name = 'contact.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        hotel = Hotel.objects.filter(is_active=True).first()
        context['hotel'] = hotel
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Procesar formulario de contacto"""
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if all([name, email, subject, message]):
            try:
                # Enviar email (configurar SMTP en settings)
                full_message = f"""
                Mensaje de contacto desde el sitio web:
                
                Nombre: {name}
                Email: {email}
                Asunto: {subject}
                
                Mensaje:
                {message}
                """
                
                send_mail(
                    f'[Hotel Yunuen] {subject}',
                    full_message,
                    email,
                    [settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False,
                )
                
                messages.success(request, '¡Mensaje enviado correctamente! Nos pondremos en contacto contigo pronto.')
            except Exception as e:
                messages.error(request, 'Error al enviar el mensaje. Por favor, intenta de nuevo.')
        else:
            messages.error(request, 'Por favor, completa todos los campos.')
        
        return self.get(request, *args, **kwargs)


def check_availability_ajax(request):
    """Vista AJAX para verificar disponibilidad"""
    if request.method == 'GET':
        check_in = request.GET.get('check_in')
        check_out = request.GET.get('check_out')
        guests = int(request.GET.get('guests', 1))
        
        if check_in and check_out:
            # Lógica para verificar disponibilidad
            available_rooms = RoomType.objects.filter(
                is_active=True,
                room_capacity__gte=guests
            )
            
            room_data = []
            for room_type in available_rooms:
                available_count = room_type.available_rooms_count()
                if available_count > 0:
                    room_data.append({
                        'id': room_type.id,
                        'name': room_type.name,
                        'price': str(room_type.price_per_night),
                        'capacity': room_type.room_capacity,
                        'available': available_count,
                        'image': room_type.image.url if room_type.image else None
                    })
            
            return JsonResponse({
                'status': 'success',
                'rooms': room_data
            })
    
    return JsonResponse({'status': 'error', 'message': 'Datos inválidos'})