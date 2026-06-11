# Audio Converter — MP3 ↔ WAV

Application desktop Windows pour convertir des fichiers audio entre **MP3** et **WAV** dans les deux sens, en mode batch.

![Python](https://img.shields.io/badge/Python-3.12-blue) ![License](https://img.shields.io/badge/license-MIT-green)

## Fonctionnalités

- Conversion **MP3 → WAV** et **WAV → MP3**
- Mode **batch** : ajout de plusieurs fichiers ou d'un dossier entier
- Interface graphique (Tkinter) — **réactive pendant la conversion** (thread séparé)
- Statut par fichier : En attente / En cours / Terminé ✓ / Erreur ✗
- Barre de progression globale
- Choix du dossier de sortie (par défaut : même dossier que la source)

## Prérequis

- Python 3.10+
- [ffmpeg](https://ffmpeg.org/download.html) installé et dans le PATH

### Installer ffmpeg sur Windows (méthode rapide)

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

> Les tests de conversion MP3/WAV nécessitent ffmpeg. Ils sont automatiquement ignorés (skip) si ffmpeg n'est pas disponible.

## Structure

```
audio_converter/
├── converter.py       # Application complète (ConversionEngine + AppUI)
├── requirements.txt   # pydub
└── tests/
    └── test_engine.py # Tests unitaires du moteur de conversion
```
