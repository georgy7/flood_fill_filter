#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys

import flood_fill_filter.flood as flood

USAGE_EPILOG = '''Example:

    flood_fill_filter input.jpg output.png
    flood_fill_filter -r 5 input.jpg output.png
    flood_fill_filter -d 0.05 input.jpg output.png
    flood_fill_filter -r 13 -a 0.05 input.jpg output.pcx

It is recommended to leave the optional parameters at their default values.
'''


def float_from_0_to_1_exclusive(arg):
    try:
        f = float(arg)
    except ValueError as e:
        raise argparse.ArgumentTypeError(str(e))

    if f <= 0.0:
        raise argparse.ArgumentTypeError("Must be greater than zero.")
    elif 1.0 <= f:
        raise argparse.ArgumentTypeError("Must be less than one.")

    return f

def radius_type(arg):
    try:
        i = int(arg)
    except ValueError as e:
        raise argparse.ArgumentTypeError(str(e))

    if i < 1:
        raise argparse.ArgumentTypeError("Must be greater than or equal 1.")

    return i

def main():
    parser = argparse.ArgumentParser(
        description='Pixel-accurate JPEG-noise-resistant edge detection algorithm.',
        epilog=USAGE_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('-d', '--diff', type=float_from_0_to_1_exclusive, default=0.1,
                        help='Y (CIE XYZ) sensitivity. Default: 0.1.')

    parser.add_argument('-a', '--activation-threshold', type=float_from_0_to_1_exclusive, default=0.45,
                        help='The fraction of filled pixels within the fill window needed '
                             'for the white pixel in the output. Default: 0.45.')

    parser.add_argument('-r', '--radius', type=radius_type, default=4,
                        help='The fill window margin. The window width equals 2r+1. Default: 4.')

    parser.add_argument('input')
    parser.add_argument('output')

    namespace = parser.parse_args(sys.argv[1:])

    input = flood.read_linear(namespace.input)
    result = flood.filter(input,
                          y_threshold=namespace.diff,
                          kernel_margin=namespace.radius,
                          ratio_threshold=namespace.activation_threshold)

    flood.save(
        flood.to_8_bit(result * 255),
        namespace.output
    )


if __name__ == "__main__":
    main()
