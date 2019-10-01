import numpy as np


class Xyz:
    def __init__(self, yXYZ, xXYZ, zXYZ):
        self.yXYZ = yXYZ
        self.xXYZ = xXYZ
        self.zXYZ = zXYZ
        self.h = yXYZ.shape[0]
        self.w = yXYZ.shape[1]

    def shape(self):
        return self.yXYZ.shape

    def left(self):
        return Xyz(self.yXYZ[:, :-1], self.xXYZ[:, :-1], self.zXYZ[:, :-1])

    def right(self):
        return Xyz(self.yXYZ[:, 1:], self.xXYZ[:, 1:], self.zXYZ[:, 1:])

    def top(self):
        return Xyz(self.yXYZ[:-1, :], self.xXYZ[:-1, :], self.zXYZ[:-1, :])

    def bottom(self):
        return Xyz(self.yXYZ[1:, :], self.xXYZ[1:, :], self.zXYZ[1:, :])

    def eq(self, other, y_threshold):
        CHROMA_FACTOR = 0.25

        y_equal = np.abs(other.yXYZ - self.yXYZ) < y_threshold

        tf = y_threshold / CHROMA_FACTOR

        return np.logical_or(
            np.logical_and(
                y_equal,
                np.logical_or(self.yXYZ > 0.9, other.yXYZ > 0.9)
            ),
            np.logical_and(
                np.logical_and(
                    np.logical_and(
                        y_equal,
                        np.logical_or(self.yXYZ > 0.5, other.yXYZ > 0.5)
                    ),
                    np.abs(other.xXYZ - self.xXYZ) < (tf / 0.5)
                ),
                np.abs(other.zXYZ - self.zXYZ) < (tf / 0.5)
            ),
            np.logical_and(
                np.logical_and(
                    y_equal,
                    np.abs(other.xXYZ - self.xXYZ) < tf
                ),
                np.abs(other.zXYZ - self.zXYZ) < tf
            )
        )
