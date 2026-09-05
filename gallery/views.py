import csv
import io
import json
import zipfile
from datetime import date
from pathlib import Path

from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.text import slugify

from .forms import ImageSearchForm, ImageUploadForm, TagExportForm
from .models import Image


def _filtered_images(request):
    form = ImageSearchForm(request.GET or None)
    images = Image.objects.all().prefetch_related("tags")

    if form.is_valid():
        search = form.cleaned_data.get("search")
        selected_tags = form.cleaned_data.get("tags")

        if search:
            images = images.filter(Q(title__icontains=search) | Q(notes__icontains=search))
        if selected_tags:
            for tag in selected_tags:
                images = images.filter(tags=tag)

    return form, images.distinct()


def _criteria(form):
    if not form.is_valid():
        return {key: value for key, value in form.data.items()}
    return {
        "search": form.cleaned_data.get("search") or None,
        "tags": [tag.name for tag in form.cleaned_data.get("tags") or []],
        "tag_logic": "AND",
    }


def _record(image):
    return {
        "id": image.id,
        "title": image.title,
        "file": image.file.name,
        "tags": [tag.name for tag in image.tags.all()],
        "notes": image.notes,
        "uploaded_at": image.uploaded_at.isoformat() if image.uploaded_at else None,
    }


def upload_image(request):
    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Image ajoutée à la galerie.")
            return redirect("gallery:upload")
    else:
        form = ImageUploadForm()
    return render(request, "gallery/upload.html", {"form": form})


def image_list(request):
    form, images = _filtered_images(request)
    return render(
        request,
        "gallery/list.html",
        {"form": form, "images": images, "count": images.count(), "criteria": _criteria(form)},
    )


def export_by_tag(request):
    form = TagExportForm(request.POST or None)
    if request.method == "GET":
        return render(request, "gallery/export_by_tag.html", {"form": form})

    if not form.is_valid():
        return render(request, "gallery/export_by_tag.html", {"form": form})

    tag = form.cleaned_data["tag"]
    images = Image.objects.filter(tags=tag).distinct()
    archive = io.BytesIO()

    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
        used_names = set()
        for image in images:
            if not image.file:
                continue
            source_path = Path(image.file.path)
            if not source_path.is_file():
                continue

            filename = source_path.name
            if filename in used_names:
                filename = f"{image.pk}_{filename}"
            used_names.add(filename)
            zip_file.write(source_path, arcname=filename)

    response = HttpResponse(archive.getvalue(), content_type="application/zip")
    safe_tag_name = slugify(tag.name) or f"{tag.pk}"
    response["Content-Disposition"] = f'attachment; filename="galerie-tag-{safe_tag_name}.zip"'
    return response


def export_images(request, format_name):
    if format_name not in {"csv", "json"}:
        return HttpResponse("Format d'export non supporté.", status=400)

    form, images = _filtered_images(request)
    records = [_record(image) for image in images]
    criteria = _criteria(form)

    if format_name == "json":
        response = HttpResponse(
            json.dumps(
                {
                    "exported_at": date.today().isoformat(),
                    "criteria": criteria,
                    "count": len(records),
                    "images": records,
                },
                ensure_ascii=False,
                indent=2,
            ),
            content_type="application/json; charset=utf-8",
        )
    else:
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response.write("# critères=" + json.dumps(criteria, ensure_ascii=False) + "\n")
        fieldnames = ["id", "title", "file", "tags", "notes", "uploaded_at"]
        writer = csv.DictWriter(response, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            row = record.copy()
            row["tags"] = " | ".join(row["tags"])
            writer.writerow(row)

    response["Content-Disposition"] = f'attachment; filename="galerie.{format_name}"'
    return response
