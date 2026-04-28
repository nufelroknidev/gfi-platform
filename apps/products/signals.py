from django.contrib.postgres.search import SearchVector
from django.db import connection
from django.db.models.signals import post_save
from django.dispatch import receiver


def _build_vector():
    return (
        SearchVector('name',              weight='A') +
        SearchVector('cas_number',        weight='B') +
        SearchVector('e_number',          weight='B') +
        SearchVector('alternative_names', weight='B') +
        SearchVector('description',       weight='C') +
        SearchVector('available_forms',   weight='D') +
        SearchVector('specifications',    weight='D')
    )


@receiver(post_save, sender='products.Product')
def update_search_vector(sender, instance, **kwargs):
    if connection.vendor != 'postgresql':
        return
    sender.objects.filter(pk=instance.pk).update(search_vector=_build_vector())
