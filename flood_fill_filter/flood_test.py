import os
import unittest
import pytest

import numpy as np
import math
from PIL import Image

import flood_fill_filter.flood as flood


@pytest.fixture(scope="class")
def cli_params_class(pytestconfig, request):
    request.cls.single_thread = pytestconfig.getoption("--single-thread")


def load_folder(folder_name, y_threshold, denoise=False, single_thread=False, filename_predicate=lambda s: True):
    directory = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir), folder_name)
    input_list = sorted([f for f in os.listdir(directory) if
                         (f.endswith('_orig.bmp')) and filename_predicate(f)])
    output_list = sorted([f for f in os.listdir(directory) if f.endswith('_fff.png') and filename_predicate(f)])

    diff_list = []

    for i, input_image in enumerate(input_list):
        input = flood.read_linear(os.path.join(directory, input_image))
        output = flood.filter(input, y_threshold=y_threshold, denoise=denoise,
                              single_thread=single_thread)

        expected_output_filename = output_list[i]
        expected_output = np.array(Image.open(os.path.join(directory, expected_output_filename)).convert('L')) > 128
        diff_count = np.sum(np.logical_xor(output, expected_output))

        diff_list.append({
            'file': input_image,
            'output_file': expected_output_filename,
            'shape': input.shape,
            'diff_count': diff_count
        })

    return diff_list


def load_samples3(single_thread):
    directory = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir), 'samples3')
    input_list = ['xm50.bmp', 'xm20.bmp']
    output_list = ['xm50_fff_denoise.png', 'xm20_fff_denoise.png']

    diff_list = []

    for i, input_image in enumerate(input_list):
        input = flood.read_linear(os.path.join(directory, input_image))
        ouput = flood.filter(input, y_threshold=0.08, kernel_margin=4, ratio_threshold=0.45, denoise=True,
                             single_thread=single_thread)

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


@pytest.mark.usefixtures("cli_params_class")
class TestSamples(unittest.TestCase):

    @classmethod
    def initialize_samples(cls, o):
        if not hasattr(cls, "samples"):
            assert hasattr(o, "single_thread")
            cls.samples = load_folder('samples', y_threshold=0.092, single_thread=o.single_thread)

    def test_adjacent_matrix_holder_2(self):
        holder = flood.AdjacentMatrixHolder(2)
        assert len(holder.offsets) == 25

        for offset1_index, offset1 in enumerate(holder.offsets):
            request_mask = np.zeros((len(holder.offsets)), dtype=np.bool)
            request_mask[offset1_index] = True
            request_mask = int(np.packbits(request_mask).data.hex(), 16)

            adjacent_offsets = holder.get_or_result(request_mask)
            adjacent_offsets_bytes = adjacent_offsets.to_bytes(math.ceil(len(holder.offsets) / 8), byteorder='big')
            adjacent_offsets_array = np.unpackbits(np.frombuffer(adjacent_offsets_bytes, dtype=np.uint8))

            for offset2_index, offset2 in enumerate(holder.offsets):
                if ((abs(offset1[0] - offset2[0]) == 1) and (offset1[1] == offset2[1])) or \
                        ((abs(offset1[1] - offset2[1]) == 1) and (offset1[0] == offset2[0])):
                    assert adjacent_offsets_array[offset2_index]
                else:
                    assert False == adjacent_offsets_array[offset2_index]

    def test_adjacent_matrix_holder_5(self):
        holder = flood.AdjacentMatrixHolder(5)
        assert len(holder.offsets) == 121

        for offset1_index, offset1 in enumerate(holder.offsets):
            request_mask = np.zeros((len(holder.offsets)), dtype=np.bool)
            request_mask[offset1_index] = True
            request_mask = int(np.packbits(request_mask).data.hex(), 16)

            adjacent_offsets = holder.get_or_result(request_mask)
            adjacent_offsets_bytes = adjacent_offsets.to_bytes(math.ceil(len(holder.offsets) / 8), byteorder='big')
            adjacent_offsets_array = np.unpackbits(np.frombuffer(adjacent_offsets_bytes, dtype=np.uint8))

            for offset2_index, offset2 in enumerate(holder.offsets):
                if ((abs(offset1[0] - offset2[0]) == 1) and (offset1[1] == offset2[1])) or \
                        ((abs(offset1[1] - offset2[1]) == 1) and (offset1[0] == offset2[0])):
                    assert adjacent_offsets_array[offset2_index]
                else:
                    assert False == adjacent_offsets_array[offset2_index]

    def test_90(self):
        self.initialize_samples(self)
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
        self.initialize_samples(self)
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
        self.initialize_samples(self)
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
        self.initialize_samples(self)
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
        assert hasattr(self, "single_thread")
        samples2 = load_folder('samples2', y_threshold=0.08, denoise=True,
                               single_thread=self.single_thread,
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
        assert hasattr(self, "single_thread")
        samples2 = load_folder('samples2', y_threshold=0.08, denoise=True,
                               single_thread=self.single_thread,
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
        assert hasattr(self, "single_thread")
        samples2 = load_folder('samples2', y_threshold=0.08, denoise=True,
                               single_thread=self.single_thread,
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
        assert hasattr(self, "single_thread")
        samples2 = load_folder('samples2', y_threshold=0.08, denoise=True,
                               single_thread=self.single_thread,
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
        assert hasattr(self, "single_thread")
        denoise_samples = load_samples3(single_thread=self.single_thread)
        for image in denoise_samples:
            diff_per_cent = image['diff_count'] / (image['shape'][0] * image['shape'][1]) * 100
            assert diff_per_cent == 0, \
                '{} {} has {} different pixels ({}%)'.format(
                    image['file'],
                    image['output_file'],
                    image['diff_count'],
                    diff_per_cent
                )
