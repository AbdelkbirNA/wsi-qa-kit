"""Image access on real vendor slides: every level, out of bounds, determinism, thumbnails."""
import numpy as np
import pytest


def _center_region(slide, level, size=256):
    w, h = slide.level_dimensions[level]
    ds = slide.level_downsamples[level]
    size = (min(size, w), min(size, h))
    x, y = (w - size[0]) // 2, (h - size[1]) // 2
    return (int(x * ds), int(y * ds)), size


@pytest.mark.req("WSI-ACC-01")
def test_read_region_on_every_level(real_slide):
    _, slide = real_slide
    for level in range(slide.level_count):
        location, size = _center_region(slide, level)
        region = slide.read_region(location, level, size)
        assert region.mode == "RGBA"
        assert region.size == size


@pytest.mark.req("WSI-ACC-02")
def test_lowest_level_contains_image_data(real_slide):
    _, slide = real_slide
    level = slide.level_count - 1
    pixels = np.asarray(slide.read_region((0, 0), level, slide.level_dimensions[level]))
    assert (pixels[..., 3] == 255).any(), "no opaque pixel on the whole lowest level"
    assert pixels[..., :3].std() > 0, "image is a single flat colour"


@pytest.mark.req("WSI-ACC-03")
def test_reads_are_deterministic(real_slide):
    _, slide = real_slide
    location, size = _center_region(slide, 0)
    first = np.asarray(slide.read_region(location, 0, size))
    second = np.asarray(slide.read_region(location, 0, size))
    assert np.array_equal(first, second)


@pytest.mark.req("WSI-ACC-04")
def test_out_of_bounds_region_is_transparent(real_slide):
    _, slide = real_slide
    w, h = slide.dimensions
    pixels = np.asarray(slide.read_region((w + 10, h + 10), 0, (64, 64)))
    assert (pixels[..., 3] == 0).all()


@pytest.mark.req("WSI-ACC-05")
def test_thumbnail_fits_and_keeps_aspect_ratio(real_slide):
    _, slide = real_slide
    thumb = slide.get_thumbnail((512, 512))
    assert max(thumb.size) <= 512
    w, h = slide.dimensions
    assert thumb.size[0] / thumb.size[1] == pytest.approx(w / h, rel=0.05)
