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

__all__ = (
    'to_linear',
    'from_linear'
)


def srgb_to_linear(cb):
    c = cb / 255.0
    a = 0.055
    array_if = c / 12.92
    array_else = np.power((c + a) / (1 + a), 2.4)
    return np.where(c <= 0.04045, array_if, array_else)


def float_to_byte(a):
    return np.fmax(np.fmin(np.rint(255.0 * a), 255.0), 0.0)


def linear_to_srgb_gamma_correction(lin):
    a = 0.055
    array_if = lin * 12.92
    array_else = np.power(lin, 1.0 / 2.4) * (1 + a) - a
    return np.where(lin <= 0.0031308, array_if, array_else)


def linear_to_srgb(lin):
    return float_to_byte(linear_to_srgb_gamma_correction(lin))


def to_linear(r, g, b, a):
    result = np.zeros((r.shape[0], r.shape[1], 4), dtype=np.single)
    result[:, :, 0] = srgb_to_linear(r)
    result[:, :, 1] = srgb_to_linear(g)
    result[:, :, 2] = srgb_to_linear(b)
    result[:, :, 3] = a / 255.0
    return result


def from_linear(linear_rgba):
    lr = linear_rgba[:, :, 0]
    lg = linear_rgba[:, :, 1]
    lb = linear_rgba[:, :, 2]
    la = linear_rgba[:, :, 3]
    result = np.zeros((lr.shape[0], lr.shape[1], 4), dtype=np.single)
    result[:, :, 0] = linear_to_srgb(lr)
    result[:, :, 1] = linear_to_srgb(lg)
    result[:, :, 2] = linear_to_srgb(lb)
    result[:, :, 3] = float_to_byte(la)
    return result
