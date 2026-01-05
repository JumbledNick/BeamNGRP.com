from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import Business

@receiver(pre_delete, sender=Business)
def revert_business_owner(sender, instance, **kwargs):
    user = instance.owner

    if not hasattr (user, 'business'):
        user.role = 'user'
        user.save()