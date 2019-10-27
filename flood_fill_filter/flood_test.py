import os
import unittest

import numpy as np
from PIL import Image
import itertools

import flood_fill_filter.flood as flood


def load_folder(folder_name, y_threshold, denoise=False, filename_predicate=lambda s: True):
    directory = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir), folder_name)
    input_list = sorted([f for f in os.listdir(directory) if
                         (f.endswith('_orig.jpg') or f.endswith('_orig.png')) and filename_predicate(f)])
    output_list = sorted([f for f in os.listdir(directory) if f.endswith('_fff.png') and filename_predicate(f)])

    diff_list = []

    for i, input_image in enumerate(input_list):
        input = flood.read_linear(os.path.join(directory, input_image))
        ouput = flood.filter(input, y_threshold=y_threshold, denoise=denoise)

        expected_output_filename = output_list[i]
        expected_output = np.array(Image.open(os.path.join(directory, expected_output_filename)).convert('L')) > 128
        diff_count = np.sum(np.logical_xor(ouput, expected_output))

        diff_list.append({
            'file': input_image,
            'output_file': expected_output_filename,
            'shape': input.shape,
            'diff_count': diff_count
        })

    return diff_list


def load_samples3():
    directory = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir), 'samples3')
    input_list = ['xm50.jpg', 'xm20.jpg']
    output_list = ['xm50_fff_denoise.png', 'xm20_fff_denoise.png']

    diff_list = []

    for i, input_image in enumerate(input_list):
        input = flood.read_linear(os.path.join(directory, input_image))
        ouput = flood.filter(input, y_threshold=0.08, kernel_margin=4, ratio_threshold=0.45, denoise=True)

        expected_output_filename = output_list[i]
        expected_output = np.array(Image.open(os.path.join(directory, expected_output_filename)).convert('L')) > 128
        diff_count = np.sum(np.logical_xor(ouput, expected_output))

        diff_list.append({
            'file': input_image,
            'output_file': expected_output_filename,
            'shape': input.shape,
            'diff_count': diff_count
        })

    return diff_list


class TestSamples(unittest.TestCase):
    samples = load_folder('samples', y_threshold=0.092)

    def test_fill_center(self):
        filled_matrix = np.zeros((5, 5), dtype=np.bool)
        counter = itertools.count()
        flood.fill(filled_matrix, 0, 0, 0, 2, counter)

        assert 5 == 2 + 1 + 2
        assert np.sum(filled_matrix) == counter.__next__()

        expected_result = np.array([
            [False, False, False, False, False],
            [False, False, False, False, False],
            [False, False, True, False, False],
            [False, False, False, False, False],
            [False, False, False, False, False]
        ], dtype=np.bool)

        assert np.array_equal(expected_result, filled_matrix), \
            filled_matrix

    def test_fill_center_to_right(self):
        filled_matrix = np.zeros((5, 5), dtype=np.bool)
        counter = itertools.count()
        flood.fill(filled_matrix, 0, 0, 2, 2, counter)

        assert 5 == 2 + 1 + 2
        assert np.sum(filled_matrix) == counter.__next__()

        expected_result = np.array([
            [False, False, False, False, False],
            [False, False, False, False, False],
            [False, False, True, True, True],
            [False, False, False, False, False],
            [False, False, False, False, False]
        ], dtype=np.bool)

        assert np.array_equal(expected_result, filled_matrix), \
            filled_matrix

    def test_fill_center_to_left(self):
        filled_matrix = np.zeros((5, 5), dtype=np.bool)
        counter = itertools.count()
        flood.fill(filled_matrix, 0, -2, 0, 2, counter)

        assert 5 == 2 + 1 + 2
        assert np.sum(filled_matrix) == counter.__next__()

        expected_result = np.array([
            [False, False, False, False, False],
            [False, False, False, False, False],
            [True, True, True, False, False],
            [False, False, False, False, False],
            [False, False, False, False, False]
        ], dtype=np.bool)

        assert np.array_equal(expected_result, filled_matrix), \
            filled_matrix

    def test_fill_top_row(self):
        filled_matrix = np.zeros((5, 5), dtype=np.bool)
        counter = itertools.count()
        flood.fill(filled_matrix, -2, -2, 2, 2, counter)

        assert 5 == 2 + 1 + 2
        assert np.sum(filled_matrix) == counter.__next__()

        expected_result = np.array([
            [True, True, True, True, True],
            [False, False, False, False, False],
            [False, False, False, False, False],
            [False, False, False, False, False],
            [False, False, False, False, False]
        ], dtype=np.bool)

        assert np.array_equal(expected_result, filled_matrix), \
            filled_matrix

    def test_fill_bottom_row(self):
        filled_matrix = np.zeros((5, 5), dtype=np.bool)
        counter = itertools.count()
        flood.fill(filled_matrix, 2, -2, 2, 2, counter)

        assert 5 == 2 + 1 + 2
        assert np.sum(filled_matrix) == counter.__next__()

        expected_result = np.array([
            [False, False, False, False, False],
            [False, False, False, False, False],
            [False, False, False, False, False],
            [False, False, False, False, False],
            [True, True, True, True, True]
        ], dtype=np.bool)

        assert np.array_equal(expected_result, filled_matrix), \
            filled_matrix

    def test_center_filled(self):
        matrix = np.array([
            [False, False, False, False, False],
            [False, False, False, False, False],
            [False, False, True, False, False],
            [False, False, False, False, False],
            [False, False, False, False, False]
        ], dtype=np.bool)

        assert flood.filled(matrix, 0, 0, 2)
        assert not flood.filled(matrix, -1, 0, 2)
        assert not flood.filled(matrix, 1, 0, 2)
        assert not flood.filled(matrix, 0, -1, 2)
        assert not flood.filled(matrix, 0, 1, 2)

    def test_left_filled(self):
        matrix = np.array([
            [False, False, False, False, False],
            [False, False, False, False, False],
            [True, False, False, False, False],
            [False, False, False, False, False],
            [False, False, False, False, False]
        ], dtype=np.bool)

        assert flood.filled(matrix, 0, -2, 2)

    def test_right_filled(self):
        matrix = np.array([
            [False, False, False, False, False],
            [False, False, False, False, False],
            [False, False, False, False, True],
            [False, False, False, False, False],
            [False, False, False, False, False]
        ], dtype=np.bool)

        assert flood.filled(matrix, 0, 2, 2)

    def test_top_filled(self):
        matrix = np.array([
            [False, False, True, False, False],
            [False, False, False, False, False],
            [False, False, False, False, False],
            [False, False, False, False, False],
            [False, False, False, False, False]
        ], dtype=np.bool)

        assert flood.filled(matrix, -2, 0, 2)

    def test_bottom_filled(self):
        matrix = np.array([
            [False, False, False, False, False],
            [False, False, False, False, False],
            [False, False, False, False, False],
            [False, False, False, False, False],
            [False, False, True, False, False]
        ], dtype=np.bool)

        assert flood.filled(matrix, 2, 0, 2)

    def test_90(self):
        for image in self.samples:
            diff_per_cent = image['diff_count'] / (image['shape'][0] * image['shape'][1]) * 100
            assert diff_per_cent < (100 - 90), \
                '{} {} has {} different pixels ({}%)'.format(
                    image['file'],
                    image['output_file'],
                    image['diff_count'],
                    diff_per_cent
                )

    def test_99(self):
        for image in self.samples:
            diff_per_cent = image['diff_count'] / (image['shape'][0] * image['shape'][1]) * 100
            assert diff_per_cent < (100 - 99), \
                '{} {} has {} different pixels ({}%)'.format(
                    image['file'],
                    image['output_file'],
                    image['diff_count'],
                    diff_per_cent
                )

    def test_999(self):
        for image in self.samples:
            diff_per_cent = image['diff_count'] / (image['shape'][0] * image['shape'][1]) * 100
            assert diff_per_cent < (100 - 99.9), \
                '{} {} has {} different pixels ({}%)'.format(
                    image['file'],
                    image['output_file'],
                    image['diff_count'],
                    diff_per_cent
                )

    def test_999615(self):
        for image in self.samples:
            diff_per_cent = image['diff_count'] / (image['shape'][0] * image['shape'][1]) * 100
            assert diff_per_cent < (100 - 99.9615), \
                '{} {} has {} different pixels ({}%)'.format(
                    image['file'],
                    image['output_file'],
                    image['diff_count'],
                    diff_per_cent
                )

    def test_2_q20(self):
        samples2 = load_folder('samples2', y_threshold=0.08, denoise=True,
                               filename_predicate=lambda f: '_q20_' in f)
        for image in samples2:
            diff_per_cent = image['diff_count'] / (image['shape'][0] * image['shape'][1]) * 100
            assert diff_per_cent < (100 - 99.99), \
                '{} {} has {} different pixels ({}%)'.format(
                    image['file'],
                    image['output_file'],
                    image['diff_count'],
                    diff_per_cent
                )

    def test_2_q40(self):
        samples2 = load_folder('samples2', y_threshold=0.08, denoise=True,
                               filename_predicate=lambda f: '_q40_' in f)
        for image in samples2:
            diff_per_cent = image['diff_count'] / (image['shape'][0] * image['shape'][1]) * 100
            assert diff_per_cent < (100 - 99.99), \
                '{} {} has {} different pixels ({}%)'.format(
                    image['file'],
                    image['output_file'],
                    image['diff_count'],
                    diff_per_cent
                )

    def test_2_q70(self):
        samples2 = load_folder('samples2', y_threshold=0.08, denoise=True,
                               filename_predicate=lambda f: '_q70_' in f)
        for image in samples2:
            diff_per_cent = image['diff_count'] / (image['shape'][0] * image['shape'][1]) * 100
            assert diff_per_cent < (100 - 99.99), \
                '{} {} has {} different pixels ({}%)'.format(
                    image['file'],
                    image['output_file'],
                    image['diff_count'],
                    diff_per_cent
                )

    def test_2_q100(self):
        samples2 = load_folder('samples2', y_threshold=0.08, denoise=True,
                               filename_predicate=lambda f: '_q100_' in f)
        for image in samples2:
            diff_per_cent = image['diff_count'] / (image['shape'][0] * image['shape'][1]) * 100
            assert diff_per_cent < (100 - 99.99), \
                '{} {} has {} different pixels ({}%)'.format(
                    image['file'],
                    image['output_file'],
                    image['diff_count'],
                    diff_per_cent
                )

    def test_denoise(self):
        denoise_samples = load_samples3()
        for image in denoise_samples:
            diff_per_cent = image['diff_count'] / (image['shape'][0] * image['shape'][1]) * 100
            assert diff_per_cent == 0, \
                '{} {} has {} different pixels ({}%)'.format(
                    image['file'],
                    image['output_file'],
                    image['diff_count'],
                    diff_per_cent
                )
