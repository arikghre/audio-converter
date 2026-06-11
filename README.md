# Media Converter

Application desktop Windows pour convertir des fichiers **audio, vidéo et image** entre de nombreux formats, en mode batch.

![Python](https://img.shields.io/badge/Python-3.12-blue) ![License](https://img.shields.io/badge/license-MIT-green)

## Formats supportés

| Catégorie | Formats |
|-----------|---------|
| Audio | MP3, WAV, FLAC |
| Vidéo | MP4, AVI, MOV |
| Image | HEIC, JPG, PNG |

Toutes les conversions sont bidirectionnelles entre les formats d'une même catégorie.

## Fonctionnalités

- Sélection du format source et du format cible via menus déroulants
- Mode **batch** : ajout de plusieurs fichiers ou d'un dossier entier
- Interface graphique (Tkinter) — **réactive pendant la conversion** (thread séparé)
- Statut par fichier : En attente / En cours / Terminé ✓ / Erreur ✗ (avec couleurs)
- Barre de progression globale
- Choix du dossier de sortie (par défaut : même dossier que la source)

## Prérequis

- Python 3.10+
- [ffmpeg](https://ffmpeg.org/download.html) installé et dans le PATH

### Installer ffmpeg sur Windows

```powershell
winget install --id Gyan.FFmpeg --source winget
```

Redémarre ton terminal après l'installation.

## Installation

```powershell
pip install -r requirements.txt
```

## Lancement

```powershell
python converter.py
```

## Tests

```powershell
python -m pytest tests/ -v
```

## Structure

```
audio_converter/
├── converter.py       # Application complète (ConversionEngine + AppUI)
├── requirements.txt   # pydub, Pillow, pillow-heif
└── tests/
    └── test_engine.py # Tests unitaires du moteur de conversion
```
