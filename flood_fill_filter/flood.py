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

import functools

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


def window_square(left_border, right_border, top_border, bottom_border):
    return (1 + right_border - left_border) * (1 + bottom_border - top_border)


@functools.lru_cache(maxsize=5000)
def lrtb(coordinate, size, kernel_margin):
    a = max(0, coordinate - kernel_margin)
    b = min(size - 1, coordinate + kernel_margin)
    return a, b


def square_of_point(x, w, t, b, kernel_margin):
    l, r = lrtb(x, w, kernel_margin)
    return window_square(l, r, t, b) - 1


def connect_offsets(adjacency_martix, p1, p2):
    adjacency_martix[p1, p2] = True
    adjacency_martix[p2, p1] = True


class AdjacentMatrixHolder:
    def __init__(self, kernel_margin, prototype=None):
        if prototype:
            self.kernel_margin = prototype.kernel_margin
            self.matrix = prototype.matrix.copy()
            self.offsets = prototype.offsets.copy()
        else:
            self.kernel_margin = kernel_margin
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

            self.matrix = np.packbits(adjacency_martix, axis=1)
            self.offsets = offsets
        self.offsets_origin = int(len(self.offsets) / 2)

    @functools.lru_cache(maxsize=32000)
    def get_or_result(self, previous_filling_iteration_result):
        adjacent_offset_rows = self.matrix[list(previous_filling_iteration_result)]
        return np.bitwise_or.reduce(adjacent_offset_rows, axis=0)

    @functools.lru_cache(maxsize=64000)
    def get_adjacent_offsets(self, previous_filling_iteration_result, filled_offsets):
        or_result = self.get_or_result(previous_filling_iteration_result)
        adjacent_offsets = np.bitwise_and(or_result, np.bitwise_not(np.asarray(filled_offsets, dtype=np.uint8)))
        r1 = np.nonzero(np.unpackbits(adjacent_offsets))[0]
        return [(self.offsets[i], i) for i in r1.tolist()]


def filter_chunk(input):
    equality_matrices_rows, h, w, min_y, max_y_exclusive, kernel_margin, \
    adjacency_martix_holder, ratio_threshold = input

    offsets_origin = adjacency_martix_holder.offsets_origin

    result = np.zeros((max_y_exclusive - min_y, w), dtype=np.bool)

    filled_offsets = np.zeros((len(adjacency_martix_holder.offsets)), dtype=np.bool)

    for y in range(min_y, max_y_exclusive):
        yi = y - min_y

        t, b = lrtb(y, h, kernel_margin)

        for x in range(w):
            count_threshold = int(square_of_point(x, w, t, b, kernel_margin) * ratio_threshold)

            filled_offsets.fill(False)
            filled_offsets_count = 0

            previous_filling_iteration_result = [offsets_origin]

            get_eq_matrix = equality_matrices_rows[yi, x]

            while (len(previous_filling_iteration_result) > 0) and (filled_offsets_count <= count_threshold):

                filled_offsets[offsets_origin] = False

                params = adjacency_martix_holder.get_adjacent_offsets(
                    tuple(previous_filling_iteration_result),
                    tuple(np.packbits(filled_offsets).tolist())
                )

                previous_filling_iteration_result = []
                for offset, offset_index in params:
                    if get_eq_matrix[offset[0] + kernel_margin, offset[1] + kernel_margin]:
                        previous_filling_iteration_result.append(offset_index)
                        filled_offsets[offset_index] = True
                        filled_offsets_count += 1

            result[yi, x] = filled_offsets_count > count_threshold

    return {
        'min_y': min_y,
        'max_y_exclusive': max_y_exclusive,
        'array': result
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
    assert ratio_threshold > 0.0
    assert ratio_threshold < 1.0
    equality_matrices = calculations.equality_matrices(original_image, kernel_margin, y_threshold)

    adjacency_martix_holder = AdjacentMatrixHolder(kernel_margin)

    flood_fill_result = np.zeros((original_image.h, original_image.w), dtype=np.bool)

    h, w = original_image.h, original_image.w

    worker_count = os.cpu_count()
    if worker_count > 8:
        worker_count = worker_count - 2
    elif worker_count > 4:
        worker_count = worker_count - 1

    chunk_size = int(h / min(worker_count, h))
    chunk_count = math.ceil(h / chunk_size)
    # chunk_size = h
    # chunk_count = 1

    input_rows = [
        (
            equality_matrices[(chunk * chunk_size):(min(h, ((chunk + 1) * chunk_size)))].copy(),
            h, w,
            (chunk * chunk_size),
            (min(h, ((chunk + 1) * chunk_size))),
            kernel_margin,
            AdjacentMatrixHolder(0, adjacency_martix_holder),
            ratio_threshold
        )
        for chunk in range(chunk_count)
    ]

    pool = Pool(worker_count)
    filled_rows = pool.imap_unordered(filter_chunk, input_rows)
    pool.close()
    # filled_rows = list(map(filter_chunk, input_rows))

    for filled_row in filled_rows:
        flood_fill_result[filled_row['min_y']:filled_row['max_y_exclusive'], :] = filled_row['array']

    return flood_fill_result


def to_8_bit(a):
    return np.clip(a, 0, 255).astype(np.uint8)


def save(grayscale_numpy_image, filename):
    img = Image.fromarray(grayscale_numpy_image, 'L')
    img.save(filename)
