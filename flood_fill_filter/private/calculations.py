import numpy as np


def equality_matrices(original_image, kernel_margin, y_threshold, offsets):
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

    return np.packbits(result, axis=2)
