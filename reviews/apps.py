from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reviews'
    verbose_name = 'Reseñas y Calificaciones'
    
    def ready(self):
        import reviews.signals
