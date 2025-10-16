# reviews/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ReviewAndRating, ReviewHelpful, HotelStatistics


@receiver(post_save, sender=ReviewAndRating)
def update_review_statistics(sender, instance, created, **kwargs):
    """Actualiza las estadísticas del hotel cuando se crea o modifica una reseña"""
    # Crear estadísticas si no existen
    stats, created_stats = HotelStatistics.objects.get_or_create(
        hotel=instance.hotel
    )
    stats.update_statistics()


@receiver(post_delete, sender=ReviewAndRating)
def update_statistics_on_delete(sender, instance, **kwargs):
    """Actualiza las estadísticas cuando se elimina una reseña"""
    if hasattr(instance.hotel, 'statistics'):
        instance.hotel.statistics.update_statistics()


@receiver(post_save, sender=ReviewHelpful)
def update_helpful_count(sender, instance, created, **kwargs):
    """Actualiza el contador de votos útiles en la reseña"""
    if created:
        review = instance.review
        review.helpful_count = review.helpful_votes.count()
        review.save(update_fields=['helpful_count'])


@receiver(post_delete, sender=ReviewHelpful)
def decrease_helpful_count(sender, instance, **kwargs):
    """Disminuye el contador de votos útiles cuando se elimina un voto"""
    review = instance.review
    review.helpful_count = review.helpful_votes.count()
    review.save(update_fields=['helpful_count'])