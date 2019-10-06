import numpy as np
from PIL import Image

import flood_fill_filter.private.calculations as calculations
import flood_fill_filter.private.xyz_loader as xyz_loader
from flood_fill_filter.linear_srgb_conv import *

KERNEL_MARGIN = 4
KERNEL_DIAMETER = KERNEL_MARGIN + 1 + KERNEL_MARGIN
RATIO_THRESHOLD = 0.45

__all__ = (
    'read_linear',
    'filter',
    'to_8_bit',
    'save'
)


def read_linear(file):
    im = Image.open(file).convert('RGBA')
    im = np.array(im, dtype=np.float32)
    return to_linear(im[:, :, 0], im[:, :, 1], im[:, :, 2], im[:, :, 3])


def get_eq(s, y_offset, x_offset):
    return s[y_offset + KERNEL_MARGIN, x_offset + KERNEL_MARGIN]


def recursive_step(a, filled, yx_tuple, ratio_threshold):
    if not (yx_tuple in filled) \
            and len(filled) <= ratio_threshold \
            and get_eq(a, yx_tuple[0], yx_tuple[1]) == True:
        filled.add(yx_tuple)

        if yx_tuple[0] > -KERNEL_MARGIN:
            recursive_step(a, filled, (yx_tuple[0] - 1, yx_tuple[1]), ratio_threshold)

        if yx_tuple[0] < KERNEL_MARGIN:
            recursive_step(a, filled, (yx_tuple[0] + 1, yx_tuple[1]), ratio_threshold)

        if yx_tuple[1] > -KERNEL_MARGIN:
            recursive_step(a, filled, (yx_tuple[0], yx_tuple[1] - 1), ratio_threshold)

        if yx_tuple[1] < KERNEL_MARGIN:
            recursive_step(a, filled, (yx_tuple[0], yx_tuple[1] + 1), ratio_threshold)


def recursive_flood_fill(a, ratio_threshold):
    filled_points = set()
    recursive_step(a, filled_points, (-1, 0), ratio_threshold)
    recursive_step(a, filled_points, (1, 0), ratio_threshold)
    recursive_step(a, filled_points, (0, -1), ratio_threshold)
    recursive_step(a, filled_points, (0, 1), ratio_threshold)
    return len(filled_points)


def window_square(left_border, right_border, top_border, bottom_border):
    return (1 + right_border - left_border) * (1 + bottom_border - top_border)


def filter(rgba, y_threshold):
    original_image = xyz_loader.from_rgba(rgba)
    equality_matrices = calculations.equality_matrices(original_image, KERNEL_MARGIN, y_threshold)

    flood_fill_result = np.zeros((original_image.h, original_image.w), dtype=np.bool)

    for y in range(equality_matrices.shape[0]):
        for x in range(equality_matrices.shape[1]):
            l = max(0, x - KERNEL_MARGIN)
            t = max(0, y - KERNEL_MARGIN)
            r = min(original_image.w - 1, x + KERNEL_MARGIN)
            b = min(original_image.h - 1, y + KERNEL_MARGIN)

            square = window_square(l, r, t, b) - 1
            count_threshold = int(square * RATIO_THRESHOLD)

            flood_fill_result[y, x] = recursive_flood_fill(equality_matrices[y, x], count_threshold) > count_threshold

    return flood_fill_result


def to_8_bit(a):
    return np.clip(a, 0, 255).astype(np.uint8)


def save(grayscale_numpy_image, filename):
    img = Image.fromarray(grayscale_numpy_image, 'L')
    img.save(filename)