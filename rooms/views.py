# rooms/views.py
from django.views.generic import ListView, DetailView, View
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from datetime import datetime
from .models import RoomType, Room


class RoomTypeListView(ListView):
    """Lista todos los tipos de habitaciones disponibles"""
    model = RoomType
    template_name = 'rooms/room_type_list.html'
    context_object_name = 'room_types'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = RoomType.objects.filter(is_active=True).prefetch_related('amenities')
        
        # Filtrar por categoría
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Filtrar por precio
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price_per_night__gte=min_price)
        if max_price:
            queryset = queryset.filter(price_per_night__lte=max_price)
        
        # Filtrar por capacidad
        capacity = self.request.GET.get('capacity')
        if capacity:
            queryset = queryset.filter(room_capacity__gte=capacity)
        
        # Ordenar
        ordering = self.request.GET.get('ordering', 'price_per_night')
        queryset = queryset.order_by(ordering)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = RoomType.RoomCategory.choices
        return context


class RoomTypeDetailView(DetailView):
    """Detalle de un tipo de habitación"""
    model = RoomType
    template_name = 'rooms/room_type_detail.html'
    context_object_name = 'room_type'
    
    def get_queryset(self):
        return RoomType.objects.filter(is_active=True).prefetch_related(
            'amenities', 'rooms'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener fechas de búsqueda si existen
        check_in_str = self.request.GET.get('check_in')
        check_out_str = self.request.GET.get('check_out')
        
        if check_in_str and check_out_str:
            check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
            check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
            
            # Contar habitaciones disponibles
            available_rooms = [
                room for room in self.object.rooms.all()
                if room.is_available_for_dates(check_in, check_out)
            ]
            context['available_rooms_count'] = len(available_rooms)
            context['check_in'] = check_in
            context['check_out'] = check_out
        else:
            context['available_rooms_count'] = self.object.available_rooms_count()
        
        return context


class CheckAvailabilityView(View):
    """Vista AJAX para verificar disponibilidad"""
    
    def get(self, request):
        room_type_id = request.GET.get('room_type_id')
        check_in_str = request.GET.get('check_in')
        check_out_str = request.GET.get('check_out')
        
        if not all([room_type_id, check_in_str, check_out_str]):
            return JsonResponse({
                'error': 'Parámetros incompletos'
            }, status=400)
        
        try:
            check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
            check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
            room_type = RoomType.objects.get(id=room_type_id, is_active=True)
            
            # Buscar habitaciones disponibles
            available_rooms = [
                room for room in room_type.rooms.all()
                if room.is_available_for_dates(check_in, check_out)
            ]
            
            nights = (check_out - check_in).days
            total_price = room_type.price_per_night * nights
            
            return JsonResponse({
                'available': len(available_rooms) > 0,
                'available_count': len(available_rooms),
                'nights': nights,
                'price_per_night': float(room_type.price_per_night),
                'total_price': float(total_price),
            })
            
        except (ValueError, RoomType.DoesNotExist) as e:
            return JsonResponse({
                'error': str(e)
            }, status=400)
