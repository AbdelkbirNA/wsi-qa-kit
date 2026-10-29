"""Generated pyramidal TIFFs: pixel-exact access, pyramid geometry, resolution metadata."""
import numpy as np
import pytest
from openslide import OpenSlide

from wsi_qa.synth import pattern


@pytest.mark.req("WSI-FMT-02")
def test_generic_tiff_is_detected(synthetic):
    _, slide = synthetic
    assert OpenSlide.detect_format(slide._filename) == "generic-tiff"


@pytest.mark.req("WSI-SYN-01")
def test_level_geometry(synthetic):
    spec, slide = synthetic
    assert slide.level_count == spec["levels"]
    for level, dims in enumerate(slide.level_dimensions):
        ds = 2 ** level
        assert dims == (-(-spec["width"] // ds), -(-spec["height"] // ds))


@pytest.mark.req("WSI-SYN-02")
def test_pixel_exact_regions_across_tile_boundaries(synthetic):
    spec, slide = synthetic
    exact_sizes = spec["width"] % 2 ** (spec["levels"] - 1) == 0 and spec["height"] % 2 ** (spec["levels"] - 1) == 0
    # Odd sizes give fractional downsamples, which OpenSlide resamples: only level 0 is pixel-exact there.
    levels = range(spec["levels"]) if exact_sizes else [0]
    for level in levels:
        ds = 2 ** level
        lw, lh = slide.level_dimensions[level]
        # straddles a tile corner when the level is larger than one tile
        x, y = min(spec["tile"] - 37, lw // 2), min(spec["tile"] - 21, lh // 2)
        size = (min(100, lw - x), min(80, lh - y))
        got = np.asarray(slide.read_region((x * ds, y * ds), level, size))
        want = pattern(lh, lw, ds)[y:y + size[1], x:x + size[0]]
        assert np.array_equal(got[..., :3], want), f"level {level}"
        assert (got[..., 3] == 255).all()


@pytest.mark.req("WSI-SYN-03")
def test_resolution_tags_become_mpp(synthetic):
    _, slide = synthetic
    assert float(slide.properties["openslide.mpp-x"]) == pytest.approx(0.25)
    assert float(slide.properties["openslide.mpp-y"]) == pytest.approx(0.25)
