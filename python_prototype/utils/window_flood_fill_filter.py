# -*- coding: utf-8 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Author: Georgy Ustinov
# November 2017

"""
This is a window filter.
It uses 9x9 window (smaller near the borders of the image).

From the center of the window, the filter makes flood fill.
The result is the count of the filled pixels (except for
the current) divided by the total number of pixels (except
for the current).
"""

# Chroma is less important than luma.
# This is the importance (0-1).
CHROMA_FACTOR = 0.25

import numpy as np
from utils import streams, boolean_flood_fill

class Filter:
    def __init__(self, yXYZ, y_threshold, xXYZ, zXYZ):
        self.y_threshold = y_threshold
        self.yXYZ = yXYZ
        self.xXYZ = xXYZ
        self.zXYZ = zXYZ
        self.h = yXYZ.shape[0]
        self.w = yXYZ.shape[1]
        self.radius = 4         # 4 + current + 4 == 9

    def process(self):
        result = np.zeros_like(self.yXYZ)
        for index, value in np.ndenumerate(self.yXYZ):
            yi = index[0]
            xi = index[1]
            result[yi, xi] = self.process_window(xi, yi)

            if xi == 0:
                streams.log(str(xi) + '-' + str(yi) + ' processed.')

        return result

    def process_window(self, x, y):
        radius = self.radius
        l = max(0, x-radius)
        t = max(0, y-radius)
        r = min(self.w-1, x+radius)
        b = min(self.h-1, y+radius)

        def compare(x1, y1, x2, y2):
            y_equal = (abs(self.yXYZ[y1, x1] - self.yXYZ[y2, x2]) < self.y_threshold)
            if y_equal and ((self.yXYZ[y1, x1] > 0.9) or (self.yXYZ[y2, x2] > 0.9)):
                return True

            tf = self.y_threshold / CHROMA_FACTOR
            xd = abs(self.xXYZ[y1, x1] - self.xXYZ[y2, x2])
            zd = abs(self.zXYZ[y1, x1] - self.zXYZ[y2, x2])

            if y_equal and ((self.yXYZ[y1, x1] > 0.5) or (self.yXYZ[y2, x2] > 0.5)) and \
                 (xd < tf / 0.5) and (zd < tf / 0.5):
                return True
            else:
                return y_equal and (xd < tf) and (zd < tf)

        boolmatrix = boolean_flood_fill.boolean_flood_fill(x, y, l, t, r, b, compare)
        count = np.sum(boolmatrix) - 1
        square = self.window_square(l, r, t, b) - 1
        ratio = float(count) / square
        return ratio

    def window_square(self, left_border, right_border, top_border, bottom_border):
        return (1 + right_border - left_border) * (1 + bottom_border - top_border)


def window_flood_fill_filter(yXYZ, y_threshold, xXYZ, zXYZ):
    f = Filter(yXYZ, y_threshold, xXYZ, zXYZ)
    return f.process()

