import numpy as np
import os
import unittest
from PIL import Image

import flood_fill_filter.flood as flood


class TestSamples(unittest.TestCase):

    sample_dir = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir), 'samples')
    input_list = sorted([f for f in os.listdir(sample_dir) if f.endswith('_orig.jpg') or f.endswith('_orig.png')])
    output_list = sorted([f for f in os.listdir(sample_dir) if f.endswith('_fff.png')])

    diff_list = []

    for i, input_image in enumerate(input_list):
        input = flood.read_linear(os.path.join(sample_dir, input_image))
        ouput = flood.filter(input)

        expected_output = np.array(Image.open(os.path.join(sample_dir, output_list[i])).convert('L')) > 128
        diff_count = np.sum(np.logical_xor(ouput, expected_output))

        diff_list.append({
            'file': input_image,
            'shape': input.shape,
            'diff_count': diff_count
        })

    def test_90(self):
        for image in self.diff_list:
            diff_per_cent = image['diff_count'] / (image['shape'][0] * image['shape'][1]) * 100
            assert diff_per_cent < (100 - 90), \
                '{} has {} different pixels ({}%)'.format(
                    image['file'],
                    image['diff_count'],
                    diff_per_cent
                )

    def test_99(self):
        for image in self.diff_list:
            diff_per_cent = image['diff_count'] / (image['shape'][0] * image['shape'][1]) * 100
            assert diff_per_cent < (100 - 99), \
                '{} has {} different pixels ({}%)'.format(
                    image['file'],
                    image['diff_count'],
                    diff_per_cent
                )

    def test_999(self):
        for image in self.diff_list:
            diff_per_cent = image['diff_count'] / (image['shape'][0] * image['shape'][1]) * 100
            assert diff_per_cent < (100 - 99.9), \
                '{} has {} different pixels ({}%)'.format(
                    image['file'],
                    image['diff_count'],
                    diff_per_cent
                )

    def test_999615(self):
        for image in self.diff_list:
            diff_per_cent = image['diff_count'] / (image['shape'][0] * image['shape'][1]) * 100
            assert diff_per_cent < (100 - 99.9615), \
                '{} has {} different pixels ({}%)'.format(
                    image['file'],
                    image['diff_count'],
                    diff_per_cent
                )
