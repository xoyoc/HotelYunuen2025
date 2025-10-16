# bookings/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Hotel, Coupon, Booking


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'state', 'phone', 'is_active']
    list_filter = ['is_active', 'city', 'state']
    search_fields = ['name', 'city', 'address']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Ubicación', {
            'fields': ('address', 'city', 'state', 'postal_code')
        }),
        ('Contacto', {
            'fields': ('phone', 'email')
        }),
        ('Horarios', {
            'fields': ('check_in_time', 'check_out_time')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_display', 'valid_from', 'valid_until', 
                    'usage_display', 'is_valid_now', 'is_active']
    list_filter = ['discount_type', 'is_active', 'valid_from', 'valid_until']
    search_fields = ['code']
    readonly_fields = ['times_used']
    
    fieldsets = (
        ('Información del Cupón', {
            'fields': ('code', 'discount_type', 'discount_value')
        }),
        ('Restricciones', {
            'fields': ('min_amount', 'max_discount', 'max_uses', 'times_used')
        }),
        ('Validez', {
            'fields': ('valid_from', 'valid_until', 'is_active')
        }),
    )
    
    def discount_display(self, obj):
        if obj.discount_type == 'PERCENTAGE':
            return f"{obj.discount_value}%"
        return f"${obj.discount_value}"
    discount_display.short_description = 'Descuento'
    
    def usage_display(self, obj):
        if obj.max_uses:
            percentage = (obj.times_used / obj.max_uses) * 100
            color = 'red' if percentage >= 90 else 'orange' if percentage >= 70 else 'green'
            return format_html(
                '<span style="color: {};">{}/{}</span>',
                color, obj.times_used, obj.max_uses
            )
        return f"{obj.times_used}/∞"
    usage_display.short_description = 'Usos'
    
    def is_valid_now(self, obj):
        is_valid = obj.is_valid()
        color = 'green' if is_valid else 'red'
        text = '✓ Válido' if is_valid else '✗ No válido'
        return format_html('<span style="color: {};">{}</span>', color, text)
    is_valid_now.short_description = 'Estado'


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['invoice_id', 'user_name', 'hotel', 'room_number', 
                    'check_in_date', 'check_out_date', 'total_price', 
                    'payment_status', 'booking_date']
    list_filter = ['payment_status', 'hotel', 'check_in_date', 'booking_date']
    search_fields = ['invoice_id', 'booking_id', 'user__username', 
                     'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['booking_id', 'invoice_id', 'booking_date', 
                       'total_days', 'created_at', 'updated_at']
    date_hierarchy = 'check_in_date'
    
    fieldsets = (
        ('Identificación', {
            'fields': ('booking_id', 'invoice_id', 'booking_date')
        }),
        ('Cliente y Hotel', {
            'fields': ('user', 'hotel', 'room')
        }),
        ('Fechas y Huéspedes', {
            'fields': ('check_in_date', 'check_out_date', 'adults', 'children')
        }),
        ('Precios', {
            'fields': ('subtotal', 'discount_amount', 'tax_amount', 'total_price', 'coupon')
        }),
        ('Estado', {
            'fields': ('payment_status', 'special_requests')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_paid', 'mark_as_confirmed', 'cancel_bookings']
    
    def user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_name.short_description = 'Cliente'
    
    def room_number(self, obj):
        return obj.room.room_number
    room_number.short_description = 'Habitación'
    
    def total_days(self, obj):
        return obj.total_days
    total_days.short_description = 'Días'
    
    @admin.action(description='Marcar como pagado')
    def mark_as_paid(self, request, queryset):
        updated = queryset.update(payment_status='PAID')
        self.message_user(request, f'{updated} reservaciones marcadas como pagadas.')
    
    @admin.action(description='Marcar como confirmado')
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(payment_status='CONFIRMED')
        self.message_user(request, f'{updated} reservaciones confirmadas.')
    
    @admin.action(description='Cancelar reservaciones')
    def cancel_bookings(self, request, queryset):
        updated = queryset.update(payment_status='CANCELLED')
        self.message_user(request, f'{updated} reservaciones canceladas.')
