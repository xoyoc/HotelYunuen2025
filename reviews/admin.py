# reviews/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import ReviewAndRating, ReviewHelpful, HotelStatistics


@admin.register(ReviewAndRating)
class ReviewAndRatingAdmin(admin.ModelAdmin):
    list_display = ['user_name', 'hotel', 'rating_display', 'review_date', 
                    'is_verified', 'is_active', 'helpful_count']
    list_filter = ['rating', 'is_active', 'is_verified', 'would_recommend', 
                   'review_date', 'hotel']
    search_fields = ['user__username', 'user__email', 'title', 'review_text']
    readonly_fields = ['review_date', 'updated_at', 'helpful_count', 'is_verified']
    date_hierarchy = 'review_date'
    
    fieldsets = (
        ('Usuario y Reservación', {
            'fields': ('user', 'hotel', 'booking')
        }),
        ('Calificaciones', {
            'fields': ('rating', 'cleanliness_rating', 'service_rating', 
                      'location_rating', 'value_rating', 'would_recommend')
        }),
        ('Reseña', {
            'fields': ('title', 'review_text')
        }),
        ('Respuesta del Hotel', {
            'fields': ('hotel_response', 'hotel_response_date'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('is_active', 'is_verified', 'helpful_count', 
                      'review_date', 'updated_at')
        }),
    )
    
    actions = ['activate_reviews', 'deactivate_reviews', 'update_hotel_stats']
    
    def user_name(self, obj):
        name = obj.user.get_full_name() or obj.user.username
        if obj.is_verified:
            return format_html('{} <span style="color: green;">✓</span>', name)
        return name
    user_name.short_description = 'Usuario'
    
    def rating_display(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color: gold;">{}</span>', stars)
    rating_display.short_description = 'Calificación'
    
    @admin.action(description='Activar reseñas seleccionadas')
    def activate_reviews(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} reseñas activadas.')
        # Actualizar estadísticas
        for review in queryset:
            if hasattr(review.hotel, 'statistics'):
                review.hotel.statistics.update_statistics()
    
    @admin.action(description='Desactivar reseñas seleccionadas')
    def deactivate_reviews(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} reseñas desactivadas.')
        # Actualizar estadísticas
        for review in queryset:
            if hasattr(review.hotel, 'statistics'):
                review.hotel.statistics.update_statistics()
    
    @admin.action(description='Actualizar estadísticas del hotel')
    def update_hotel_stats(self, request, queryset):
        hotels = set(review.hotel for review in queryset)
        for hotel in hotels:
            if hasattr(hotel, 'statistics'):
                hotel.statistics.update_statistics()
        self.message_user(request, f'Estadísticas actualizadas para {len(hotels)} hoteles.')


@admin.register(ReviewHelpful)
class ReviewHelpfulAdmin(admin.ModelAdmin):
    list_display = ['review', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'review__title']
    date_hierarchy = 'created_at'


@admin.register(HotelStatistics)
class HotelStatisticsAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'average_rating', 'total_reviews', 
                    'recommendation_percentage', 'total_bookings', 'last_updated']
    list_filter = ['last_updated']
    search_fields = ['hotel__name']
    readonly_fields = ['hotel', 'average_rating', 'total_reviews', 
                       'avg_cleanliness', 'avg_service', 'avg_location', 
                       'avg_value', 'recommendation_percentage', 
                       'total_bookings', 'completed_bookings', 
                       'cancelled_bookings', 'last_updated']
    
    actions = ['refresh_statistics']
    
    @admin.action(description='Actualizar estadísticas')
    def refresh_statistics(self, request, queryset):
        for stats in queryset:
            stats.update_statistics()
        self.message_user(request, f'{queryset.count()} estadísticas actualizadas.')
