"""Met en miroir les binaires décrits dans manifest.json sous forme de releases GitHub.

Pour chaque fichier dont la première URL pointe vers ce dépôt :
  1. télécharge le fichier depuis la source officielle (URL suivante du manifeste) ;
  2. vérifie sa taille et son empreinte SHA-256 (refus en cas d'écart) ;
  3. le publie dans la release `<binaire>-<version>`.
Les fichiers déjà publiés ne sont pas retéléchargés. Les archives de sources exigées par les
licences (sources.json) sont publiées dans la même release.

Exécuté par .github/workflows/mirror.yml ; nécessite `gh` et `curl`.
"""

import hashlib
import json
import os
import subprocess
import sys
import tempfile

REPO = os.environ["GITHUB_REPOSITORY"]
PREFIX = f"https://github.com/{REPO}/releases/download/"

LICENSES = {
    "aria2": "GPL-2.0-or-later — sources : https://github.com/aria2/aria2",
    "ffmpeg": "LGPL-2.1-or-later — sources : https://ffmpeg.org (build : https://github.com/BtbN/FFmpeg-Builds)",
    "yt-dlp": "Unlicense — sources : https://github.com/yt-dlp/yt-dlp",
    "whisper": "MIT — sources : https://github.com/ggml-org/whisper.cpp",
}


def gh(*args, check=True):
    return subprocess.run(["gh", *args], capture_output=True, text=True, check=check)


def release_assets(tag):
    result = gh("release", "view", tag, "--repo", REPO, "--json", "assets", check=False)
    if result.returncode != 0:
        return None
    return {asset["name"] for asset in json.loads(result.stdout)["assets"]}


def ensure_release(tag, name, version):
    assets = release_assets(tag)
    if assets is not None:
        return assets
    notes = (
        f"Miroir de {name} {version}, fichiers identiques aux publications officielles "
        f"(empreintes SHA-256 vérifiées, voir manifest.json).\n\nLicence : {LICENSES.get(name, '?')}"
    )
    gh("release", "create", tag, "--repo", REPO, "--title", f"{name} {version}", "--notes", notes)
    return set()


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(url, destination):
    subprocess.run(
        ["curl", "--fail", "--location", "--silent", "--show-error", "--retry", "5", "-o", destination, url],
        check=True,
    )


def main():
    manifest = json.load(open("manifest.json", encoding="utf-8"))
    sources = json.load(open("sources.json", encoding="utf-8"))
    errors = []
    with tempfile.TemporaryDirectory() as work:
        for name, entry in manifest["binaries"].items():
            tag = f"{name}-{entry['version']}"
            for target, artifact in entry["platforms"].items():
                mirrors = [url for url in artifact["urls"] if url.startswith(PREFIX)]
                upstream = [url for url in artifact["urls"] if not url.startswith(PREFIX)]
                if not mirrors:
                    continue
                mirror = mirrors[0]
                if not mirror.startswith(f"{PREFIX}{tag}/"):
                    errors.append(f"{name} {target} : URL de miroir hors de la release {tag}")
                    continue
                file_name = mirror.rsplit("/", 1)[1]
                assets = ensure_release(tag, name, entry["version"])
                if file_name in assets:
                    print(f"= {tag}/{file_name} déjà publié")
                    continue
                path = os.path.join(work, file_name)
                print(f"↓ {tag}/{file_name} depuis {upstream[0]}")
                download(upstream[0], path)
                size, digest = os.path.getsize(path), sha256(path)
                if size != artifact["size"] or digest != artifact["sha256"]:
                    errors.append(
                        f"{tag}/{file_name} : attendu {artifact['size']} o / {artifact['sha256']}, "
                        f"obtenu {size} o / {digest}"
                    )
                    continue
                gh("release", "upload", tag, path, "--repo", REPO)
                os.remove(path)
                print(f"✓ {tag}/{file_name} vérifié et publié")

            for source in sources.get(tag, []):
                assets = ensure_release(tag, name, entry["version"])
                if source["name"] in assets:
                    continue
                path = os.path.join(work, source["name"])
                print(f"↓ sources {tag}/{source['name']}")
                download(source["url"], path)
                gh("release", "upload", tag, path, "--repo", REPO)
                os.remove(path)

    if errors:
        print("\n".join(f"✗ {error}" for error in errors), file=sys.stderr)
        sys.exit(1)
    print("Miroir à jour.")


if __name__ == "__main__":
    main()
