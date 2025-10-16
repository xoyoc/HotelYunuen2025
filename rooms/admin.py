# rooms/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Amenity, RoomType, Room


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    list_editable = ['is_active']


class RoomInline(admin.TabularInline):
    model = Room
    extra = 0
    fields = ['room_number', 'floor', 'status', 'is_available']


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price_per_night', 'room_capacity', 
                    'total_rooms', 'available_count', 'is_active']
    list_filter = ['category', 'is_active', 'number_of_beds']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    filter_horizontal = ['amenities']
    inlines = [RoomInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'category', 'description')
        }),
        ('Capacidad', {
            'fields': ('number_of_beds', 'room_capacity', 'size_sqm', 'total_rooms')
        }),
        ('Precio', {
            'fields': ('price_per_night',)
        }),
        ('Comodidades', {
            'fields': ('amenities', 'image')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
    )
    
    def available_count(self, obj):
        count = obj.available_rooms_count()
        color = 'green' if count > 0 else 'red'
        return format_html(
            '<span style="color: {};">{}/{}</span>',
            color, count, obj.total_rooms
        )
    available_count.short_description = 'Disponibles'


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'room_type', 'floor', 'status', 
                    'is_available', 'updated_at']
    list_filter = ['status', 'is_available', 'floor', 'room_type']
    search_fields = ['room_number', 'notes']
    list_editable = ['status', 'is_available']
    
    fieldsets = (
        ('Información de la Habitación', {
            'fields': ('room_type', 'room_number', 'floor')
        }),
        ('Estado', {
            'fields': ('status', 'is_available', 'notes')
        }),
    )
