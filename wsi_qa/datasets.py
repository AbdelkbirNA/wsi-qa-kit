"""Fetch the slides listed in a manifest, verify their checksum, unpack archives."""
import hashlib
import json
import shutil
import urllib.request
import zipfile
from pathlib import Path


def load_manifest(path):
    return json.loads(Path(path).read_text())


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(manifest, cache_dir):
    """Return {slide id: local path to open}. Downloads only what is missing or corrupt."""
    cache = Path(cache_dir)
    cache.mkdir(parents=True, exist_ok=True)
    paths = {}
    for slide in manifest["slides"]:
        target = cache / Path(slide["file"]).name
        if not target.exists() or sha256(target) != slide["sha256"]:
            tmp = target.with_suffix(target.suffix + ".part")
            with urllib.request.urlopen(manifest["base_url"] + slide["file"]) as r, open(tmp, "wb") as f:
                shutil.copyfileobj(r, f)
            if sha256(tmp) != slide["sha256"]:
                tmp.unlink()
                raise ValueError(f"{slide['id']}: checksum mismatch for {slide['file']}")
            tmp.rename(target)
        if target.suffix == ".zip":
            folder = cache / target.stem
            if not (folder / slide["open"]).exists():
                with zipfile.ZipFile(target) as z:
                    z.extractall(folder)
            target = folder / slide["open"]
        paths[slide["id"]] = target
    return paths
