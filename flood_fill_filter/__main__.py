#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

import flood_fill_filter.flood as flood


def main():
    input = flood.read_linear(sys.argv[1])
    result = flood.filter(input)

    flood.save(
        flood.to_8_bit(result * 255),
        sys.argv[2]
    )


if __name__ == "__main__":
    main()
