"""The benchmark and dataset tooling itself."""
import hashlib

import pytest

from wsi_qa import bench, datasets


def test_percentile():
    values = list(range(1, 11))
    assert bench.percentile(values, 0) == 1
    assert bench.percentile(values, 50) == 5.5
    assert bench.percentile(values, 100) == 10
    assert bench.percentile([7], 95) == 7


@pytest.mark.req("WSI-BENCH-01")
def test_bench_reports_every_level(synthetic_paths):
    result = bench.bench_slide(synthetic_paths["tiled-raw-256"], reads=10)
    assert result["format"] == "generic-tiff"
    assert [lv["level"] for lv in result["levels"]] == [0, 1, 2, 3]
    for lv in result["levels"]:
        assert 0 < lv["p50_ms"] <= lv["p95_ms"]
        assert lv["tiles_per_s"] > 0
    assert bench.over_budget([result], max_p95_ms=0)
    assert not bench.over_budget([result], max_p95_ms=1e9)
    assert "generic-tiff" in bench.to_markdown([result])


@pytest.mark.req("WSI-DATA-01")
def test_fetch_rejects_a_corrupt_download(tmp_path):
    source = tmp_path / "src"
    source.mkdir()
    (source / "slide.svs").write_bytes(b"payload")
    manifest = {"base_url": source.as_uri() + "/",
                "slides": [{"id": "s", "file": "slide.svs", "sha256": "0" * 64}]}
    with pytest.raises(ValueError, match="checksum"):
        datasets.fetch(manifest, tmp_path / "cache")
    manifest["slides"][0]["sha256"] = hashlib.sha256(b"payload").hexdigest()
    assert datasets.fetch(manifest, tmp_path / "cache")["s"].read_bytes() == b"payload"
