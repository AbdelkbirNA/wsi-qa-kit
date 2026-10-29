# wsi-qa-kit

Automated validation and benchmarking of **whole slide image (WSI)** access, the large
multi-resolution images used in digital pathology. It tests the
[OpenSlide](https://openslide.org) reader the way a QA team would test its own slide-reading
library: image access, metadata extraction, format compatibility and read performance,
across a dataset of real vendor slides and generated pyramids.

> Written with [Claude Code](https://claude.com/claude-code).

## What is tested

| Area | How |
|---|---|
| **Format compatibility** | Real CC0 slides from the OpenSlide test data: Aperio SVS, Mirax MRXS, Zeiss CZI, Huron TIFF; plus generated generic tiled TIFFs (raw and deflate, 256 and 512 px tiles, odd sizes) |
| **Metadata extraction** | Dimensions, level count, microns per pixel on both axes, objective power, pyramid consistency, associated images (label, macro, thumbnail), checked against [`datasets/slides.json`](datasets/slides.json) |
| **Image access** | A region on every level, real image data on the lowest level, repeatable reads, transparent out-of-bounds regions, thumbnails |
| **Pixel exactness** | Generated pyramids encode each pixel's level-0 position in its RGB value, so regions straddling tile corners are compared pixel for pixel on every level |
| **Error handling** | Non-slide, truncated and missing files are rejected with `OpenSlideUnsupportedFormatError` |
| **Performance** | Open time, p50 / p95 tile-read latency, tiles/s and MPix/s per slide and level, with a p95 budget that fails the run |

Every test carries a requirement ID (`@pytest.mark.req`), exported to the JUnit XML. The CI
runs [qa-report-kit](https://github.com/AbdelkbirNA/qa-report-kit) as a quality gate: 100 %
pass rate and every requirement in [`requirements.csv`](requirements.csv) covered.

## Run it

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"            # openslide-bin ships the OpenSlide library
pytest -q --junitxml results/junit.xml
python -m wsi_qa bench datasets/slides.json --md results/bench.md --max-p95-ms 250
```

Slides are downloaded once into `.data/` (about 43 MB) and verified against their SHA-256.
Offline, the real-slide tests are skipped unless `WSI_REQUIRE_DATA=1`.

### In Docker

```bash
docker build -t wsi-qa-kit .
docker run --rm -e WSI_REQUIRE_DATA=1 -v "$PWD/.data:/data" -v "$PWD/results:/results" -u "$(id -u)" wsi-qa-kit
docker run --rm -v "$PWD/.data:/data" -u "$(id -u)" wsi-qa-kit python -m wsi_qa bench datasets/slides.json --data /data
```

## CI

GitHub Actions: the suites with the quality gate and traceability report, then the same
suites and the benchmark inside the Docker image. Both reports land in the job summary and
as artifacts.

## Adding a dataset

Add an entry to `datasets/slides.json` (file, SHA-256, expected format, dimensions, levels,
microns per pixel, objective power, associated images). Every metadata and access test runs
on it automatically.

## Layout

```
wsi_qa/datasets.py   download, checksum, unpack
wsi_qa/synth.py      generated pyramidal TIFFs with predictable pixels
wsi_qa/bench.py      tile-read benchmark and Markdown report
tests/               metadata, access, synthetic, errors, tooling
```
