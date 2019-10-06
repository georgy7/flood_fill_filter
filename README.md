## Summary

The notable moderate JPEG noises may be found in the white area.

They are mostly in the white area near edges.

The filter is just a window 9x9, that walks through the image.
There is flood fill happening for each pixel.
And if the count of the filled pixels (inside the window) is greater than some threshold,
the result pixel is white.
For more information please read the python source code.
It's pretty short and simple.

## Usage

    flood_fill_filter input.jpg output.png

## Changelog

2017-11-18 — Python prototype — 4m 51s

2017-11-28 — C version — 1.2s

2018-10-07 — New Python implementation — 18s
