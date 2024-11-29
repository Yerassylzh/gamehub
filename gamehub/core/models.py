from django.db import models
from django.utils.safestring import mark_safe

from sorl.thumbnail import get_thumbnail


class AbstractImage(models.Model):
    image = models.ImageField(
        name="image",
        verbose_name="изображение",
        upload_to="uploads/",
    )

    def get_image_300x300(self):
        return get_thumbnail(
            self.main_image.image,
            "300x300",
            crop="center",
            quality=51,
        )

    def get_image_50x50(self):
        return get_thumbnail(
            self.image,
            "50x50",
            crop="center",
            quality=51,
        )

    def image_tmb(self):
        image = self.get_image_50x50()
        if image:
            return mark_safe(
                f'<img src="{image.url}" class="img-fuild">',
            )
        return "No image"

    image_tmb.short_description = "превью"
    image_tmb.allow_tags = True

    class Meta:
        abstract = True

    def __str__(self):
        return f"Image at '...{self.image.path[:15]}'"
