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

from flood_fill_filter.private.xyz import Xyz
from flood_fill_filter.linear_srgb_conv import linear_to_srgb_gamma_correction


def white_lowering_function(gamma_corrected_luma):
    """
    White is not very important for this filter.
    """
    t = 0.7
    if gamma_corrected_luma > t:
        return gamma_corrected_luma - gamma_corrected_luma * 0.25 * ((gamma_corrected_luma - t) / (1 - t))
    else:
        return gamma_corrected_luma


v_white_lowering_function = \
    np.vectorize(white_lowering_function)


def from_rgba(linear_rgba):
    r = linear_rgba[:, :, 0]
    g = linear_rgba[:, :, 1]
    b = linear_rgba[:, :, 2]

    y = r * 0.2126 + g * 0.7152 + b * 0.0722
    x = r * 0.4124 + g * 0.3576 + b * 0.1805
    z = r * 0.0193 + g * 0.1192 + b * 0.9505

    y_gamma = linear_to_srgb_gamma_correction(y)
    y_gamma_low_white = v_white_lowering_function(y_gamma)

    return Xyz(y_gamma_low_white, x, z)
