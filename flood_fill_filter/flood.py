import itertools
import os

import math
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

builtin_filter = filter

def read_linear(file):
    im = Image.open(file).convert('RGBA')
    im = np.array(im, dtype=np.float32)
    return to_linear(im[:, :, 0], im[:, :, 1], im[:, :, 2], im[:, :, 3])


def get_eq(s, y_offset, x_offset, kernel_margin):
    return s[y_offset + kernel_margin, x_offset + kernel_margin]


def window_square(left_border, right_border, top_border, bottom_border):
    return (1 + right_border - left_border) * (1 + bottom_border - top_border)


def square_of_point(y, x, h, w, kernel_margin):
    t = max(0, y - kernel_margin)
    b = min(h - 1, y + kernel_margin)

    l = max(0, x - kernel_margin)
    r = min(w - 1, x + kernel_margin)

    return window_square(l, r, t, b) - 1


def get_adjacent_offsets(adjacency_martix, previous_filling_iteration_result, offsets_origin, filled_offsets):
    adjacent_offset_rows = adjacency_martix[previous_filling_iteration_result]
    adjacent_offsets = adjacent_offset_rows.any(axis=0)  # logical OR of the rows
    adjacent_offsets[offsets_origin] = False
    adjacent_offsets = np.logical_and(adjacent_offsets, np.logical_not(filled_offsets))
    return np.nonzero(adjacent_offsets)[0]


def filter_chunk(input):
    equality_matrices_rows, h, w, min_y, max_y_exclusive, kernel_margin, \
    filling_graph_adjacency_martix, filling_graph_offsets, ratio_threshold = input

    offsets_origin = int(len(filling_graph_offsets) / 2)

    row_result = np.zeros((max_y_exclusive - min_y, w), dtype=np.bool)

    filled_offsets = np.zeros((len(filling_graph_offsets)), dtype=np.bool)

    for y, x in itertools.product(range(min_y, max_y_exclusive), range(w)):
        yi = y - min_y
        equality_matrices_row = equality_matrices_rows[yi]

        count_threshold = int(square_of_point(y, x, h, w, kernel_margin) * ratio_threshold)

        filled_offsets.fill(False)
        filled_offsets_count = 0

        previous_filling_iteration_result = [offsets_origin]

        equality_matrix = equality_matrices_row[x]

        while (len(previous_filling_iteration_result) > 0) and (filled_offsets_count <= count_threshold):

            adjacent_offsets = get_adjacent_offsets(
                filling_graph_adjacency_martix,
                previous_filling_iteration_result,
                offsets_origin,
                filled_offsets
            )

            params = [(filling_graph_offsets[i], i) for i in adjacent_offsets.tolist()]

            previous_filling_iteration_result = []
            for offset, offset_index in params:
                if get_eq(equality_matrix, offset[0], offset[1], kernel_margin):
                    previous_filling_iteration_result.append(offset_index)
                    filled_offsets[offset_index] = True
                    filled_offsets_count = filled_offsets_count + 1

        row_result[yi, x] = filled_offsets_count > count_threshold

    return {
        'min_y': min_y,
        'max_y_exclusive': max_y_exclusive,
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


def connect_offsets(adjacency_martix, p1, p2):
    adjacency_martix[p1, p2] = True
    adjacency_martix[p2, p1] = True


def build_adjacency_matrix_of_pixels_with_desctiption(kernel_margin):
    kernel_diameter = kernel_margin + 1 + kernel_margin
    offsets = []

    for yo in range(-kernel_margin, kernel_margin + 1):
        for xo in range(-kernel_margin, kernel_margin + 1):
            offsets.append((yo, xo))

    assert len(offsets) == (kernel_diameter * kernel_diameter)

    origin = int((kernel_diameter * kernel_diameter) / 2)

    assert offsets[origin] == (0, 0)
    assert offsets[origin - kernel_diameter] == (-1, 0)
    assert offsets[origin + kernel_diameter] == (1, 0)
    assert offsets[origin - 1] == (0, -1)
    assert offsets[origin + 1] == (0, 1)

    adjacency_martix = np.zeros((len(offsets), len(offsets)), dtype=np.bool)

    for yo in range(-kernel_margin, kernel_margin):
        for xo in range(-kernel_margin, kernel_margin):
            left_top = origin + yo * kernel_diameter + xo
            right_top = left_top + 1
            left_bottom = left_top + kernel_diameter
            right_bottom = left_bottom + 1
            connect_offsets(adjacency_martix, left_top, right_top)
            connect_offsets(adjacency_martix, left_top, left_bottom)
            connect_offsets(adjacency_martix, right_top, right_bottom)
            connect_offsets(adjacency_martix, left_bottom, right_bottom)

    return adjacency_martix, offsets


def one_pass(original_image, y_threshold, kernel_margin, ratio_threshold):
    assert ratio_threshold > 0.0
    assert ratio_threshold < 1.0
    equality_matrices = calculations.equality_matrices(original_image, kernel_margin, y_threshold)

    filling_graph_adjacency_martix, filling_graph_offsets = \
        build_adjacency_matrix_of_pixels_with_desctiption(kernel_margin)

    flood_fill_result = np.zeros((original_image.h, original_image.w), dtype=np.bool)

    h, w = original_image.h, original_image.w

    chunk_size = int(h / min(32, h))
    chunk_count = math.ceil(h / chunk_size)

    input_rows = [
        (
            equality_matrices[(chunk * chunk_size):(min(h, ((chunk + 1) * chunk_size)))].copy(),
            h, w,
            (chunk * chunk_size),
            (min(h, ((chunk + 1) * chunk_size))),
            kernel_margin,
            filling_graph_adjacency_martix.copy(), filling_graph_offsets.copy(),
            ratio_threshold
        )
        for chunk in range(chunk_count)
    ]

    worker_count = os.cpu_count()
    if worker_count > 8:
        worker_count = worker_count - 2
    elif worker_count > 4:
        worker_count = worker_count - 1

    pool = Pool(worker_count)
    filled_rows = pool.imap_unordered(filter_chunk, input_rows)

    for filled_row in filled_rows:
        flood_fill_result[filled_row['min_y']:filled_row['max_y_exclusive'], :] = filled_row['array']

    return flood_fill_result


def to_8_bit(a):
    return np.clip(a, 0, 255).astype(np.uint8)


def save(grayscale_numpy_image, filename):
    img = Image.fromarray(grayscale_numpy_image, 'L')
    img.save(filename)
