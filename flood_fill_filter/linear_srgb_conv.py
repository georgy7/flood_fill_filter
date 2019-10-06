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


def linear_to_srgb(lin):
    a = 0.055
    array_if = float_to_byte(lin * 12.92)
    array_else = float_to_byte(np.power(lin, 1.0 / 2.4) * (1 + a) - a)
    return np.where(lin <= 0.0031308, array_if, array_else)


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
