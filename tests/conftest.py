import os
from pathlib import Path

import openslide
import pytest

from wsi_qa import datasets, synth

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = datasets.load_manifest(ROOT / "datasets" / "slides.json")
SLIDES = {s["id"]: s for s in MANIFEST["slides"]}

# Synthetic pyramids: exact pixels are known, so access can be checked to the pixel.
SYNTHETIC = [
    {"id": "tiled-raw-256", "width": 2048, "height": 1536, "levels": 4, "tile": 256, "compression": None},
    {"id": "tiled-deflate-512", "width": 4096, "height": 2048, "levels": 3, "tile": 512, "compression": "zlib"},
    {"id": "odd-size-raw-256", "width": 1000, "height": 777, "levels": 3, "tile": 256, "compression": None},
]


@pytest.fixture(autouse=True)
def _export_requirements(request, record_property):
    """@pytest.mark.req("ID") -> <property name="requirement" value="ID"/> in the JUnit XML."""
    for marker in request.node.iter_markers("req"):
        for req in marker.args:
            record_property("requirement", req)


@pytest.fixture(scope="session")
def slide_paths():
    try:
        return datasets.fetch(MANIFEST, os.environ.get("WSI_DATA_DIR", ROOT / ".data"))
    except OSError as e:
        if os.environ.get("WSI_REQUIRE_DATA"):
            raise
        pytest.skip(f"slide data unavailable: {e}")


@pytest.fixture(params=list(SLIDES))
def real_slide(request, slide_paths):
    slide = openslide.OpenSlide(str(slide_paths[request.param]))
    yield SLIDES[request.param], slide
    slide.close()


@pytest.fixture(scope="session")
def synthetic_paths(tmp_path_factory):
    folder = tmp_path_factory.mktemp("synthetic")
    return {
        spec["id"]: synth.write_pyramid(
            folder / f"{spec['id']}.tiff", spec["width"], spec["height"],
            levels=spec["levels"], tile=spec["tile"], compression=spec["compression"])
        for spec in SYNTHETIC
    }


@pytest.fixture(params=SYNTHETIC, ids=[s["id"] for s in SYNTHETIC])
def synthetic(request, synthetic_paths):
    slide = openslide.OpenSlide(str(synthetic_paths[request.param["id"]]))
    yield request.param, slide
    slide.close()
