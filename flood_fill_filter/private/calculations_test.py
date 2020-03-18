import numpy as np
import unittest

import os

from flood_fill_filter.flood import read_linear, AdjacentMatrixHolder
import flood_fill_filter.private.xyz_loader as xyz_loader

from flood_fill_filter.private.calculations import *

class TestCalculations(unittest.TestCase):
    def test_equality_matrices(self):
        directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir, 'samples3')
        input_image = 'xm20.bmp'

        linear_rgba = read_linear(os.path.join(directory, input_image))
        xyz = xyz_loader.from_rgba(linear_rgba)

        kernel_margin = 4
        adjacency_martix_holder = AdjacentMatrixHolder(kernel_margin)

        equality_masks = equality_matrices(xyz, kernel_margin, 0.08, adjacency_martix_holder.offsets, pack=False)

        kernel_diameter = kernel_margin + 1 + kernel_margin

        assert equality_masks.shape[0] == 136
        assert equality_masks.shape[1] == 195
        assert equality_masks.shape[2] == kernel_diameter * kernel_diameter

        expected = np.loadtxt(os.path.join(directory, 'xm20_eq.csv.gz'), delimiter=',')
        expected = expected.reshape((136, 195, kernel_diameter * kernel_diameter))

        assert np.allclose(equality_masks, expected)
