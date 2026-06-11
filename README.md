# Media Converter

Convertisseur de fichiers audio, vidéo et image — interface graphique Windows.

## Formats supportés

| Audio | Vidéo | Image |
|-------|-------|-------|
| MP3, WAV, FLAC | MP4, AVI, MOV | HEIC, JPG, PNG |

Toutes les conversions sont bidirectionnelles.

## Lancer l'app

**Sans installation** — télécharge `MediaConverter.exe` dans [Releases](../../releases) et double-clique.

> ffmpeg doit être installé : `winget install --id Gyan.FFmpeg --source winget`

## Lancer depuis le code source

```powershell
pip install -r requirements.txt
python converter.py
```

## Reconstruire l'exe

```powershell
python -m PyInstaller MediaConverter.spec
```
