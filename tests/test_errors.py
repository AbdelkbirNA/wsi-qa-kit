"""Unsupported, truncated and missing files are rejected cleanly."""
import pytest
from openslide import OpenSlide, OpenSlideUnsupportedFormatError


@pytest.mark.req("WSI-ERR-01")
def test_non_slide_file_is_rejected(tmp_path):
    path = tmp_path / "notes.txt"
    path.write_text("not a slide")
    assert OpenSlide.detect_format(str(path)) is None
    with pytest.raises(OpenSlideUnsupportedFormatError):
        OpenSlide(str(path))


@pytest.mark.req("WSI-ERR-02")
def test_truncated_slide_is_rejected(tmp_path, slide_paths):
    truncated = tmp_path / "truncated.svs"
    truncated.write_bytes(slide_paths["aperio-svs"].read_bytes()[:200_000])
    with pytest.raises(OpenSlideUnsupportedFormatError):
        OpenSlide(str(truncated))


@pytest.mark.req("WSI-ERR-03")
def test_missing_file_is_rejected(tmp_path):
    with pytest.raises(OpenSlideUnsupportedFormatError):
        OpenSlide(str(tmp_path / "missing.svs"))
