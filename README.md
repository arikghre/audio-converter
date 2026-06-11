# Media Converter

Convertisseur de fichiers audio, vidéo et image — interface graphique Windows.

## Formats supportés

| Audio | Vidéo | Image |
|-------|-------|-------|
| MP3, WAV, FLAC | MP4, AVI, MOV | HEIC, JPG, PNG |

Toutes les conversions sont bidirectionnelles.

## Télécharger

👉 [Releases](../../releases) — télécharge `MediaConverter_Setup_v1.1.0.exe` et lance l'installeur.

> **Prérequis :** ffmpeg doit être installé sur le système.
> ```powershell
> winget install --id Gyan.FFmpeg --source winget
> ```

## Lancer depuis le code source

```powershell
pip install -r requirements.txt
python converter.py
```

## Construire l'installeur depuis les sources

Double-clique sur **`build.bat`** — le script installe les dépendances, génère l'exe et compile l'installeur. Le résultat est dans `installer\`.
