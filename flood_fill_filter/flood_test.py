import numpy as np
import os
import unittest
from PIL import Image

import flood_fill_filter.flood as flood


def load_folder(folder_name):
    directory = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir), folder_name)
    input_list = sorted([f for f in os.listdir(directory) if f.endswith('_orig.jpg') or f.endswith('_orig.png')])
    output_list = sorted([f for f in os.listdir(directory) if f.endswith('_fff.png')])

    diff_list = []

    for i, input_image in enumerate(input_list):
        input = flood.read_linear(os.path.join(directory, input_image))
        ouput = flood.filter(input)

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
    samples = load_folder('samples')
    samples2 = load_folder('samples2')

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

    def test2_90(self):
        for image in self.samples2:
            diff_per_cent = image['diff_count'] / (image['shape'][0] * image['shape'][1]) * 100
            assert diff_per_cent < (100 - 90), \
                '{} {} has {} different pixels ({}%)'.format(
                    image['file'],
                    image['output_file'],
                    image['diff_count'],
                    diff_per_cent
                )

    def test2_99(self):
        for image in self.samples2:
            diff_per_cent = image['diff_count'] / (image['shape'][0] * image['shape'][1]) * 100
            assert diff_per_cent < (100 - 99), \
                '{} {} has {} different pixels ({}%)'.format(
                    image['file'],
                    image['output_file'],
                    image['diff_count'],
                    diff_per_cent
                )
