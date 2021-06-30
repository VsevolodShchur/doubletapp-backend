from django.contrib import admin
from .models import Pet, Photo

# Register your models here.


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'type', )


@admin.register(Photo)
class PetAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'pet', )
