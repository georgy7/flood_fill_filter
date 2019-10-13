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
