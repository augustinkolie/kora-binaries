# Binaires de l'application Kora

Miroir des outils libres que l'application de bureau Kora (nom provisoire) télécharge à la demande, et manifeste qui les décrit.

- **`manifest.json`** : versions, URL, tailles et empreintes SHA-256 de chaque outil, par plateforme. L'application le consulte au démarrage, en arrière-plan ; s'il est plus récent (`revision`) que sa copie embarquée, elle l'utilise.
- **Releases** : une release par outil et par version (`ffmpeg-8.1.3`, `yt-dlp-2026.10.21`…). Les fichiers sont **identiques** aux publications officielles : le workflow les télécharge depuis la source, vérifie leur empreinte SHA-256 et refuse tout écart.

Chaque entrée du manifeste liste d'abord ce miroir, puis la source officielle : si l'un des deux est indisponible, l'application utilise l'autre. Elle vérifie toujours l'empreinte avant installation.

## Outils et licences

| Outil | Licence | Sources |
|---|---|---|
| aria2 1.37.0 | GPL-2.0-or-later | https://github.com/aria2/aria2 — archive des sources jointe à la release `aria2-1.37.0` |
| FFmpeg 8.1.3 (build LGPL de BtbN) | LGPL-2.1-or-later | https://ffmpeg.org, build https://github.com/BtbN/FFmpeg-Builds (commit FFmpeg `92611900bb`) — archive des sources jointe à la release `ffmpeg-8.1.3` |
| yt-dlp 2026.10.21 | Unlicense | https://github.com/yt-dlp/yt-dlp |
| whisper.cpp b5454 | MIT | https://github.com/ggml-org/whisper.cpp |

Les builds Linux d'aria2 proviennent de https://github.com/abcfy2/aria2-static-build.

## Mettre à jour un outil

1. Modifier `manifest.json` dans le dépôt de l'application (`backend/desktop-core/resources/binaries/manifest.json`) : version, URL officielle, taille, empreinte SHA-256 ; URL du miroir en premier (`https://github.com/augustinkolie/kora-binaries/releases/download/<outil>-<version>/<fichier>`) ; incrémenter `revision`.
2. Copier ce fichier ici et pousser : le workflow **Miroir des binaires** publie les nouveaux fichiers après vérification.
3. Si la licence l'exige (GPL, LGPL), ajouter l'archive des sources correspondantes dans `sources.json`.
