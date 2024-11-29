from django.contrib import admin

from club.models import Club, MainImage, GalleryImage, Contact


class MainImageInline(admin.TabularInline):
    model = MainImage


class GalleryImageInline(admin.TabularInline):
    model = GalleryImage


class ContactInline(admin.TabularInline):
    model = Contact


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    inlines = [
        MainImageInline,
        GalleryImageInline,
        ContactInline,
    ]

    def image_tmb(self):
        return self.main_image.image_tmb()
    
    list_display = (
        Club.name.field.name,
        Club.description.field.name,
        image_tmb,
        Club.price.field.name,
        Club.number_of_computers.field.name,
    )
