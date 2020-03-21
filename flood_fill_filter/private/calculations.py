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


def equality_matrices(original_image, kernel_margin, y_threshold, offsets, pack=True):

    assert np.min(original_image.yXYZ) >= 0.0
    assert np.min(original_image.xXYZ) >= 0.0
    assert np.min(original_image.zXYZ) >= 0.0

    assert np.max(original_image.yXYZ) <= 1.0
    assert np.max(original_image.xXYZ) <= 1.0
    assert np.max(original_image.zXYZ) <= 1.089

    image = original_image.expand(kernel_margin)

    result = np.zeros(
        (
            original_image.h,
            original_image.w,
            len(offsets)
        ),
        dtype=np.bool
    )

    for offset_index in range(len(offsets)):
        y_offset, x_offset = offsets[offset_index]

        if (0 == y_offset) and (0 == x_offset):
            continue

        data_to_compare = image

        if 0 == y_offset:
            data_to_compare = data_to_compare.top(kernel_margin).bottom(kernel_margin)
        elif y_offset < 0:
            data_to_compare = data_to_compare \
                .bottom(kernel_margin + abs(y_offset)) \
                .top(kernel_margin - abs(y_offset))
        else:
            data_to_compare = data_to_compare \
                .top(kernel_margin + y_offset) \
                .bottom(kernel_margin - y_offset)

        if 0 == x_offset:
            data_to_compare = data_to_compare.left(kernel_margin).right(kernel_margin)
        elif x_offset < 0:
            data_to_compare = data_to_compare \
                .right(kernel_margin + abs(x_offset)) \
                .left(kernel_margin - abs(x_offset))
        else:
            data_to_compare = data_to_compare \
                .left(kernel_margin + x_offset) \
                .right(kernel_margin - x_offset)

        result[:, :, offset_index] = \
            data_to_compare.eq(original_image, y_threshold)

    if pack:
        return np.packbits(result, axis=2)
    else:
        return result
