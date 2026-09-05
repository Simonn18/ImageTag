from django.urls import path

from . import views

app_name = "gallery"

urlpatterns = [
    path("", views.image_list, name="list"),
    path("upload/", views.upload_image, name="upload"),
    path("export/tag/", views.export_by_tag, name="export_by_tag"),
    path("export/<str:format_name>/", views.export_images, name="export"),
]
