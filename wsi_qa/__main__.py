"""python -m wsi_qa bench datasets/slides.json [--data DIR] [--json OUT] [--md OUT] [--max-p95-ms N]

Fetches the manifest's slides, benchmarks tile reads on every level, writes JSON and Markdown.
Exit code 1 when a level's p95 latency exceeds --max-p95-ms.
"""
import argparse
import json
import sys
from pathlib import Path

from . import bench, datasets


def main(argv=None):
    p = argparse.ArgumentParser(prog="wsi_qa")
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("bench")
    b.add_argument("manifest")
    b.add_argument("--data", default=".data")
    b.add_argument("--reads", type=int, default=50)
    b.add_argument("--json")
    b.add_argument("--md")
    b.add_argument("--max-p95-ms", type=float)
    a = p.parse_args(argv)

    paths = datasets.fetch(datasets.load_manifest(a.manifest), a.data)
    results = [bench.bench_slide(path, reads=a.reads) for path in paths.values()]
    md = bench.to_markdown(results)
    print(md)
    if a.json:
        Path(a.json).write_text(json.dumps(results, indent=2))
    if a.md:
        Path(a.md).write_text("## Tile-read benchmark\n\n" + md)
    if a.max_p95_ms is not None:
        slow = bench.over_budget(results, a.max_p95_ms)
        for slide, level, p95 in slow:
            print(f"OVER BUDGET {slide} level {level}: p95 {p95} ms > {a.max_p95_ms} ms", file=sys.stderr)
        return 1 if slow else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
