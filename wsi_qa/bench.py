"""Tile-read benchmark: open time, latency percentiles and throughput per slide and level."""
import random
import time

import openslide


def percentile(values, p):
    """Linear-interpolated percentile, p in [0, 100]."""
    s = sorted(values)
    k = (len(s) - 1) * p / 100
    lo = int(k)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


def bench_slide(path, tile=256, reads=50, seed=0):
    rng = random.Random(seed)
    t = time.perf_counter()
    slide = openslide.OpenSlide(str(path))
    open_ms = (time.perf_counter() - t) * 1000
    result = {"slide": str(path), "format": openslide.OpenSlide.detect_format(str(path)),
              "open_ms": round(open_ms, 2), "levels": []}
    with slide:
        for level, (w, h) in enumerate(slide.level_dimensions):
            ds = slide.level_downsamples[level]
            size = (min(tile, w), min(tile, h))
            times = []
            for _ in range(reads):
                x, y = rng.randrange(w - size[0] + 1), rng.randrange(h - size[1] + 1)
                t = time.perf_counter()
                slide.read_region((int(x * ds), int(y * ds)), level, size)
                times.append(time.perf_counter() - t)
            total = sum(times)
            result["levels"].append({
                "level": level,
                "tile": list(size),
                "p50_ms": round(percentile(times, 50) * 1000, 2),
                "p95_ms": round(percentile(times, 95) * 1000, 2),
                "tiles_per_s": round(reads / total, 1),
                "mpix_per_s": round(reads * size[0] * size[1] / total / 1e6, 2),
            })
    return result


def to_markdown(results):
    lines = ["| Slide | Format | Open (ms) | Level | Tile | p50 (ms) | p95 (ms) | Tiles/s | MPix/s |",
             "|---|---|---|---|---|---|---|---|---|"]
    for r in results:
        name = r["slide"].rsplit("/", 1)[-1]
        for lv in r["levels"]:
            lines.append(f"| {name} | {r['format']} | {r['open_ms']} | {lv['level']} | {lv['tile'][0]}x{lv['tile'][1]} "
                         f"| {lv['p50_ms']} | {lv['p95_ms']} | {lv['tiles_per_s']} | {lv['mpix_per_s']} |")
    return "\n".join(lines) + "\n"


def over_budget(results, max_p95_ms):
    return [(r["slide"], lv["level"], lv["p95_ms"]) for r in results for lv in r["levels"] if lv["p95_ms"] > max_p95_ms]
