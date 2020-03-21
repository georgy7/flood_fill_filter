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


class Xyz:
    def __init__(self, yXYZ, xXYZ, zXYZ):
        assert yXYZ.shape[0] == xXYZ.shape[0]
        assert yXYZ.shape[0] == zXYZ.shape[0]
        assert yXYZ.shape[1] == xXYZ.shape[1]
        assert yXYZ.shape[1] == zXYZ.shape[1]
        self.yXYZ = yXYZ
        self.xXYZ = xXYZ
        self.zXYZ = zXYZ
        self.h = yXYZ.shape[0]
        self.w = yXYZ.shape[1]

    def expand(self, margin):
        """Expand with inverted lightness border."""
        invert = lambda array: -array + 1.0
        first_row = lambda array: array[:1]
        last_row = lambda array: array[-1:]

        first_column = lambda array: array[:, :1]
        last_column = lambda array: array[:, -1:]

        y = np.concatenate(
            (
                np.repeat(invert(first_row(self.yXYZ)), margin, axis=0),
                self.yXYZ,
                np.repeat(invert(last_row(self.yXYZ)), margin, axis=0)
            ))

        x = np.concatenate(
            (
                np.repeat(first_row(self.xXYZ), margin, axis=0),
                self.xXYZ,
                np.repeat(last_row(self.xXYZ), margin, axis=0)
            ))

        z = np.concatenate(
            (
                np.repeat(first_row(self.zXYZ), margin, axis=0),
                self.zXYZ,
                np.repeat(last_row(self.zXYZ), margin, axis=0)
            ))

        y = np.concatenate(
            (
                np.repeat(invert(first_column(y)), margin, axis=1),
                y,
                np.repeat(invert(last_column(y)), margin, axis=1)
            ),
            axis=1
        )

        x = np.concatenate(
            (
                np.repeat(first_column(x), margin, axis=1),
                x,
                np.repeat(last_column(x), margin, axis=1)
            ),
            axis=1
        )

        z = np.concatenate(
            (
                np.repeat(first_column(z), margin, axis=1),
                z,
                np.repeat(last_column(z), margin, axis=1)
            ),
            axis=1
        )

        return Xyz(y, x, z)

    def shape(self):
        return self.yXYZ.shape

    def left(self, n=1):
        if 0 == n:
            return self
        elif n < 0:
            return self.right(-n)
        return Xyz(self.yXYZ[:, :-n], self.xXYZ[:, :-n], self.zXYZ[:, :-n])

    def right(self, n=1):
        if 0 == n:
            return self
        elif n < 0:
            return self.left(-n)
        return Xyz(self.yXYZ[:, n:], self.xXYZ[:, n:], self.zXYZ[:, n:])

    def top(self, n=1):
        if 0 == n:
            return self
        elif n < 0:
            return self.bottom(-n)
        return Xyz(self.yXYZ[:-n, :], self.xXYZ[:-n, :], self.zXYZ[:-n, :])

    def bottom(self, n=1):
        if 0 == n:
            return self
        elif n < 0:
            return self.top(-n)
        return Xyz(self.yXYZ[n:, :], self.xXYZ[n:, :], self.zXYZ[n:, :])

    def eq(self, other, y_threshold):
        chroma_threshold_factor = 4

        y_equal = np.abs(other.yXYZ - self.yXYZ) < y_threshold

        xd = np.abs(other.xXYZ - self.xXYZ)
        zd = np.abs(other.zXYZ - self.zXYZ)

        tf = y_threshold * chroma_threshold_factor

        return np.logical_and(
            y_equal,
            np.logical_or(
                np.logical_or(self.yXYZ <= (25 / 255), other.yXYZ <= (25 / 255)),
                np.logical_or(
                    np.logical_and(
                        np.logical_and(
                            np.logical_or(self.yXYZ > 0.5, other.yXYZ > 0.5),
                            xd < tf * 2
                        ),
                        zd < tf * 2
                    ),
                    np.logical_and(
                        xd < tf,
                        zd < tf
                    )
                )
            )
        )
