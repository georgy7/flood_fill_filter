# flood-fill-filter - edge bunches detection tool.
# Copyright (C) 2020  Georgy Ustinov  <georgy.ustinov.hello@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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

        csv_offsets = np.loadtxt(os.path.join(directory, 'xm20_eq_offsets.csv'), delimiter=',')

        expected = np.loadtxt(os.path.join(directory, 'xm20_eq.csv.gz'), delimiter=',')
        expected = expected.reshape((136, 195, kernel_diameter * kernel_diameter))

        for csv_offset_index in range(csv_offsets.shape[0]):
            csv_offset = tuple(csv_offsets[csv_offset_index])
            holder_offset_index = adjacency_martix_holder.offsets.index(csv_offset)
            assert np.allclose(equality_masks[:, :, holder_offset_index], expected[:, :, csv_offset_index])
