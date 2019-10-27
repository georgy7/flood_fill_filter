import itertools
import os
from multiprocessing import Pool

import numpy as np
from PIL import Image

import flood_fill_filter.private.calculations as calculations
import flood_fill_filter.private.xyz_loader as xyz_loader
from flood_fill_filter.linear_srgb_conv import *
from flood_fill_filter.private.xyz import Xyz

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


def get_eq(s, y_offset, x_offset, kernel_margin):
    return s[y_offset + kernel_margin, x_offset + kernel_margin]


def filled(filled_matrix, y_offset, x_offset, kernel_margin):
    return filled_matrix[
        (y_offset + kernel_margin),
        (x_offset + kernel_margin)
    ]


def fill(filled_matrix, y_offset, left_x_offset_inclusive, right_x_offset_inclusive, kernel_margin, counter):
    filled_matrix[
    y_offset + kernel_margin,
    (left_x_offset_inclusive + kernel_margin):(right_x_offset_inclusive + kernel_margin + 1)
    ] = True

    assert right_x_offset_inclusive >= left_x_offset_inclusive

    last_value = 0

    for _ in itertools.repeat(None, (right_x_offset_inclusive - left_x_offset_inclusive + 1)):
        last_value = counter.__next__()

    return last_value


def recursive_step(a, filled_matrix, yx_tuple, count_threshold, kernel_margin, counter):
    y = yx_tuple[0]
    initial_x = yx_tuple[1]

    left_border_inclusive = initial_x
    right_border_inclusive = initial_x

    for x in range(initial_x - 1, -kernel_margin - 1, -1):
        if get_eq(a, y, x, kernel_margin):
            left_border_inclusive = x
        else:
            break

    for x in range(initial_x + 1, kernel_margin + 1, 1):
        if get_eq(a, y, x, kernel_margin):
            right_border_inclusive = x
        else:
            break

    value = fill(filled_matrix, y, left_border_inclusive, right_border_inclusive, kernel_margin, counter)

    # assert (np.sum(filled_matrix) - 1) == value

    if value > count_threshold:
        return

    if y > -kernel_margin:
        for x in range(left_border_inclusive, right_border_inclusive + 1):
            if not filled(filled_matrix, y - 1, x, kernel_margin) and get_eq(a, y - 1, x, kernel_margin):
                recursive_step(a, filled_matrix, (y - 1, x), count_threshold, kernel_margin, counter)

    if y < kernel_margin:
        for x in range(left_border_inclusive, right_border_inclusive + 1):
            if not filled(filled_matrix, y + 1, x, kernel_margin) and get_eq(a, y + 1, x, kernel_margin):
                recursive_step(a, filled_matrix, (y + 1, x), count_threshold, kernel_margin, counter)


def recursive_flood_fill(a, count_threshold, kernel_margin):
    kernel_diameter = kernel_margin + 1 + kernel_margin
    filled_points = np.zeros((kernel_diameter, kernel_diameter), dtype=np.bool)
    counter = itertools.count()
    recursive_step(a, filled_points, (0, 0), count_threshold, kernel_margin, counter)
    return counter.__next__() - 1


def window_square(left_border, right_border, top_border, bottom_border):
    return (1 + right_border - left_border) * (1 + bottom_border - top_border)


def filter_row(input):
    equality_matrices_row, h, w, y, kernel_margin, ratio_threshold = input

    t = max(0, y - kernel_margin)
    b = min(h - 1, y + kernel_margin)

    row_result = np.zeros((w), dtype=np.bool)

    for x in range(w):
        l = max(0, x - kernel_margin)
        r = min(w - 1, x + kernel_margin)

        square = window_square(l, r, t, b) - 1
        count_threshold = int(square * ratio_threshold)

        row_result[x] = recursive_flood_fill(
            equality_matrices_row[x], count_threshold, kernel_margin
        ) > count_threshold

    return {
        'y': y,
        'array': row_result
    }


def filter(linear_rgba, y_threshold=0.08, kernel_margin=4, ratio_threshold=0.45, denoise=False):
    original_image = xyz_loader.from_rgba(linear_rgba)
    first_pass = one_pass(original_image, y_threshold, kernel_margin, ratio_threshold).astype(np.float32)

    if denoise:
        first_pass_xyz = Xyz(first_pass, np.zeros_like(first_pass), np.zeros_like(first_pass))
        second_pass = np.logical_not(one_pass(first_pass_xyz, y_threshold=0.08, kernel_margin=4, ratio_threshold=0.05))
        return np.logical_or(first_pass, second_pass)
    else:
        return first_pass


def one_pass(original_image, y_threshold, kernel_margin, ratio_threshold):
    equality_matrices = calculations.equality_matrices(original_image, kernel_margin, y_threshold)

    flood_fill_result = np.zeros((original_image.h, original_image.w), dtype=np.bool)

    h, w = original_image.h, original_image.w

    input_rows = [
        (
            equality_matrices[y, :].copy(),
            h, w,
            y, kernel_margin, ratio_threshold
        )
        for y in range(h)
    ]

    worker_count = os.cpu_count()
    if worker_count > 8:
        worker_count = worker_count - 2
    elif worker_count > 4:
        worker_count = worker_count - 1

    pool = Pool(worker_count)
    filled_rows = pool.map(filter_row, input_rows)

    for filled_row in filled_rows:
        flood_fill_result[filled_row['y'], :] = filled_row['array']

    return flood_fill_result


def to_8_bit(a):
    return np.clip(a, 0, 255).astype(np.uint8)


def save(grayscale_numpy_image, filename):
    img = Image.fromarray(grayscale_numpy_image, 'L')
    img.save(filename)
