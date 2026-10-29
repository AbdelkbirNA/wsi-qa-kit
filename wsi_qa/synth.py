"""Synthetic pyramidal tiled TIFFs whose every pixel the tests can predict."""
import numpy as np
import tifffile


def pattern(height, width, downsample=1):
    """RGB pixel at level coordinates (x, y) encodes the level-0 position (x*ds, y*ds)."""
    y, x = np.mgrid[0:height, 0:width]
    x, y = x * downsample, y * downsample
    return np.stack([x % 256, y % 256, (x // 256 + y // 256) % 256], axis=-1).astype(np.uint8)


def write_pyramid(path, width, height, levels=3, tile=256, compression=None, mpp=0.25):
    """Write a tiled TIFF with one directory per level, each half the size of the previous one."""
    pixels_per_cm = 1e4 / mpp
    with tifffile.TiffWriter(path) as tw:
        for level in range(levels):
            ds = 2 ** level
            tw.write(
                pattern(-(-height // ds), -(-width // ds), ds),
                tile=(tile, tile),
                compression=compression,
                photometric="rgb",
                resolution=(pixels_per_cm / ds, pixels_per_cm / ds),
                resolutionunit="CENTIMETER",
                subfiletype=0 if level == 0 else 1,
            )
    return path
