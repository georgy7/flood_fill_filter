import numpy as np

from flood_fill_filter.private.xyz import Xyz


def white_lowering_function(luma):
    """
    White is not very important for this filter.
    """
    t = 0.7
    if luma > t:
        return luma - luma * 0.25 * ((luma - t) / (1 - t))
    else:
        return luma


v_white_lowering_function = \
    np.vectorize(white_lowering_function)


def from_rgba(rgba):
    r = rgba[:, :, 0]
    g = rgba[:, :, 1]
    b = rgba[:, :, 2]

    yXYZ = r * 0.2126 + g * 0.7152 + b * 0.0722
    xXYZ = r * 0.4124 + g * 0.3576 + b * 0.1805
    zXYZ = r * 0.0193 + g * 0.1192 + b * 0.9505

    yGamma = yXYZ ** (1 / 2.2)
    yGammaLowWhite = v_white_lowering_function(yGamma)

    return Xyz(yGammaLowWhite, xXYZ, zXYZ)
