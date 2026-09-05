from django import forms

from .models import Image, Tag


class ImageUploadForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    new_tags = forms.CharField(
        required=False,
        label="Nouveaux tags",
        help_text="Séparez les tags par des virgules.",
        widget=forms.TextInput(attrs={"placeholder": "Ex. voyage, été, famille"}),
    )

    class Meta:
        model = Image
        fields = ["file", "title", "tags", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_new_tags(self):
        names = []
        seen = set()
        for raw_name in self.cleaned_data.get("new_tags", "").split(","):
            name = " ".join(raw_name.split())
            if not name:
                continue
            if len(name) > 80:
                raise forms.ValidationError("Chaque tag doit contenir au maximum 80 caractères.")
            normalized_name = name.casefold()
            if normalized_name not in seen:
                names.append(name)
                seen.add(normalized_name)
        return names

    def save(self, commit=True):
        image = super().save(commit=commit)
        if commit:
            for name in self.cleaned_data.get("new_tags", []):
                tag = Tag.objects.filter(name__iexact=name).first()
                if tag is None:
                    tag = Tag.objects.create(name=name)
                image.tags.add(tag)
        return image


class ImageSearchForm(forms.Form):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    search = forms.CharField(
        required=False,
        label="Recherche",
        widget=forms.TextInput(attrs={"placeholder": "Titre ou description"}),
    )


class TagExportForm(forms.Form):
    tag = forms.ModelChoiceField(
        queryset=Tag.objects.all(),
        empty_label="Choisir un tag",
        label="Tag à exporter",
    )
