from pets.models import Photo
from django.db.models import signals
from django.dispatch import receiver
from pets import settings
import os


@receiver(signals.post_delete, sender=Photo)
def delete_photo_file(sender, instance, using, **kwargs):
    os.remove(os.path.join(settings.MEDIA_ROOT, instance.file.name))
