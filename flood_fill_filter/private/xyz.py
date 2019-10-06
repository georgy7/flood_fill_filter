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
        CHROMA_FACTOR = 0.25

        y_equal = np.abs(other.yXYZ - self.yXYZ) < y_threshold

        xd = np.abs(other.xXYZ - self.xXYZ)
        zd = np.abs(other.zXYZ - self.zXYZ)

        tf = y_threshold / CHROMA_FACTOR

        return np.logical_or(
            np.logical_and(
                y_equal,
                np.logical_or(self.yXYZ > 0.9, other.yXYZ > 0.9)
            ),
            np.logical_or(
                np.logical_and(
                    y_equal,
                    np.logical_and(
                        np.logical_and(
                            np.logical_or(self.yXYZ > 0.5, other.yXYZ > 0.5),
                            xd < tf / 0.5
                        ),
                        zd < tf / 0.5
                    )
                ),
                np.logical_and(
                    y_equal,
                    np.logical_and(
                        xd < tf,
                        zd < tf
                    )
                )
            )
        )
