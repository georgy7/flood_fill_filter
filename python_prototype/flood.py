#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Author: Georgy Ustinov
# November 2017


from utils import streams, window_flood_fill_filter
import numpy as np

def white_lowering_function(luma):
    """
    White is not very important.
    """
    t = 0.7
    if luma > t:
        return luma - luma * 0.25 * ((luma - t) / (1 - t))
    else:
        return luma


v_white_lowering_function = \
        np.vectorize(white_lowering_function)


def floodfiltered(yXYZ, xXYZ, zXYZ, y_threshold):
    yGamma = yXYZ ** (1/2.2)
    yGammaLowWhite = v_white_lowering_function(yGamma)

    result = window_flood_fill_filter.window_flood_fill_filter(
            yGammaLowWhite,
            y_threshold,
            xXYZ,
            zXYZ)

    return (result > 0.45)


def main(y_threshold):
    app = streams.Start()

    r = app.pixels[:,:,0]
    g = app.pixels[:,:,1]
    b = app.pixels[:,:,2]
    yXYZ = 0.2126 * r + 0.7152 * g + 0.0722 * b
    xXYZ = 0.4124 * r + 0.3576 * g + 0.1805 * b
    zXYZ = 0.0193 * r + 0.1192 * g + 0.9505 * b

    result = floodfiltered(yXYZ, xXYZ, zXYZ, y_threshold)
    app.result[:,:,0] = result
    app.result[:,:,1] = result
    app.result[:,:,2] = result
    app.result[:,:,3] = 1
    app.end()


def valid(n):
    try:
        float(n)
        return True
    except ValueError:
        return False

if __name__ == "__main__":
    y_threshold = 0.1

    import sys
    if (len(sys.argv) > 1) and (valid(sys.argv[1])):
        y_threshold = float(sys.argv[1])
        streams.log('Threshold: ' + str(y_threshold))
    else:
        streams.log('Using default threshold: ' + str(y_threshold))

    main(y_threshold)

