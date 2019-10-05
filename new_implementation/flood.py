#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import sys
from PIL import Image

import calculations
import linear_srgb_conv
import xyz_loader

KERNEL_MARGIN = 4
KERNEL_DIAMETER = KERNEL_MARGIN + 1 + KERNEL_MARGIN
RATIO_THRESHOLD = int(KERNEL_DIAMETER * KERNEL_DIAMETER * 0.45)


def read_linear(file):
    im = Image.open(file).convert('RGBA')
    im = np.array(im, dtype=np.float32)
    return linear_srgb_conv.to_linear(im[:, :, 0], im[:, :, 1], im[:, :, 2], im[:, :, 3])


def get_eq(s, y_offset, x_offset):
    return s[y_offset + KERNEL_MARGIN, x_offset + KERNEL_MARGIN]


def recursive_step(a, filled, yx_tuple):
    if not (yx_tuple in filled) \
            and len(filled) <= RATIO_THRESHOLD \
            and get_eq(a, yx_tuple[0], yx_tuple[1]) == True:
        filled.add(yx_tuple)

        if yx_tuple[0] > -KERNEL_MARGIN:
            recursive_step(a, filled, (yx_tuple[0] - 1, yx_tuple[1]))

        if yx_tuple[0] < KERNEL_MARGIN:
            recursive_step(a, filled, (yx_tuple[0] + 1, yx_tuple[1]))

        if yx_tuple[1] > -KERNEL_MARGIN:
            recursive_step(a, filled, (yx_tuple[0], yx_tuple[1] - 1))

        if yx_tuple[1] < KERNEL_MARGIN:
            recursive_step(a, filled, (yx_tuple[0], yx_tuple[1] + 1))


def recursive_flood_fill(a):
    filled_points = set()
    recursive_step(a, filled_points, (-1, 0))
    recursive_step(a, filled_points, (1, 0))
    recursive_step(a, filled_points, (0, -1))
    recursive_step(a, filled_points, (0, 1))
    return len(filled_points)


def main(rgba, y_threshold):
    original_image = xyz_loader.from_rgba(rgba)
    equality_matrices = calculations.equality_matrices(original_image, KERNEL_MARGIN, y_threshold)

    flood_fill_sum = np.zeros((original_image.h, original_image.w), dtype=np.short)

    for y in range(equality_matrices.shape[0]):
        for x in range(equality_matrices.shape[1]):
            flood_fill_sum[y, x] = recursive_flood_fill(equality_matrices[y, x])

    return flood_fill_sum > RATIO_THRESHOLD


# TODO удалить позже
def to_8_bit(a):
    return np.clip(a, 0, 255).astype(np.uint8)


# TODO удалить позже
def show(grayscale_numpy_image, scale=1):
    img = Image.fromarray(grayscale_numpy_image, 'L')

    if (scale > 1):
        new_size = (img.size[0] * scale, img.size[1] * scale)
        img = img.resize(new_size, Image.NEAREST)

    img.show()


if __name__ == "__main__":
    y_threshold = 0.1
    input = read_linear(sys.argv[1])
    result = main(input, y_threshold)
    show(to_8_bit(result * 255))
