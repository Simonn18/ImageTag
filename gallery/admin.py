from django.contrib import admin

from .models import Image, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("title", "uploaded_at")
    list_filter = ("tags", "uploaded_at")
    search_fields = ("title", "notes")
    filter_horizontal = ("tags",)
