"""Metadata extraction on real vendor slides, checked against the dataset manifest."""
import pytest
from openslide import OpenSlide


@pytest.mark.req("WSI-FMT-01")
def test_vendor_format_is_detected(real_slide):
    expected, slide = real_slide
    assert OpenSlide.detect_format(slide._filename) == expected["format"]
    assert slide.properties["openslide.vendor"] == expected["format"]


@pytest.mark.req("WSI-META-01")
def test_dimensions_and_level_count(real_slide):
    expected, slide = real_slide
    assert list(slide.dimensions) == expected["dimensions"]
    assert slide.level_count == expected["level_count"]


@pytest.mark.req("WSI-META-02")
def test_microns_per_pixel(real_slide):
    expected, slide = real_slide
    for axis, mpp in zip("xy", expected["mpp"]):
        assert float(slide.properties[f"openslide.mpp-{axis}"]) == pytest.approx(mpp, rel=1e-3)


@pytest.mark.req("WSI-META-03")
def test_objective_power(real_slide):
    expected, slide = real_slide
    assert slide.properties.get("openslide.objective-power") == expected["objective_power"]


@pytest.mark.req("WSI-META-04")
def test_pyramid_is_consistent(real_slide):
    _, slide = real_slide
    downsamples = slide.level_downsamples
    assert downsamples[0] == 1.0
    assert all(a < b for a, b in zip(downsamples, downsamples[1:]))
    w0, h0 = slide.dimensions
    for (w, h), ds in zip(slide.level_dimensions, downsamples):
        assert abs(w0 / ds - w) <= 1 and abs(h0 / ds - h) <= 1


@pytest.mark.req("WSI-META-05")
def test_associated_images(real_slide):
    expected, slide = real_slide
    assert set(expected["associated_images"]) <= set(slide.associated_images)
    for name in expected["associated_images"]:
        w, h = slide.associated_images[name].size
        assert w > 0 and h > 0
