# Galerie d'images par tags

Application Django indépendante permettant de créer une galerie d'images et
de les retrouver grâce à des tags.

## Fonctionnalités

- ajout d'une image avec titre, tags et notes ;
- affichage sous forme de galerie responsive ;
- recherche dans les titres et les notes ;
- filtrage par plusieurs tags ;
- logique **ET** : une image doit posséder tous les tags sélectionnés ;
- export CSV et JSON du résultat filtré ;
- critères de recherche inclus dans les exports ;
- gestion des images et des tags depuis l'administration Django.

## Installation

Depuis ce dossier :

```bash
python -m venv .venv
source .venv/bin/activate       # Windows : .venv\\Scripts\\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Pages disponibles :

- `http://127.0.0.1:8000/` — galerie et recherche ;
- `http://127.0.0.1:8000/upload/` — ajouter une image ;
- `http://127.0.0.1:8000/admin/` — administrer les tags et les images.

## Utilisation

1. Créer quelques tags depuis `/admin/`.
2. Ajouter une image depuis `/upload/`.
3. Sélectionner un ou plusieurs tags sur la page principale.
4. Cliquer sur **Rechercher**.
5. Exporter le résultat en CSV ou en JSON si nécessaire.

Les filtres actifs sont conservés dans l'URL et réutilisés par les boutons
d'export. Les exports contiennent également la date et les critères appliqués.

## Structure

```text
generic_image_gallery/
├── gallery/
│   ├── migrations/
│   ├── static/gallery/css/style.css
│   ├── templates/gallery/
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── imagegallery_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
└── requirements.txt
```
