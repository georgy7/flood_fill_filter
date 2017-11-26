## Summary

The notable moderate JPEG noises may be found in the white area.

They are mostly in the white area near edges.

The filter is just a window 9x9, that walks through the image.
There is flood fill happening for each pixel.
And if the count of the filled pixels (inside the window) is greater than some threshold,
the result pixel is white.
For more information please read the python source code.
It's pretty short and simple.


## See the video demonstration on YouTube

[![Flood Fill Filter video demonstration on YouTube](https://img.youtube.com/vi/1NPU90AELg0/0.jpg)](https://www.youtube.com/watch?v=1NPU90AELg0)


## Usage

    lineara source.jpg | c/flood | lineara -b result.png

## Contributing

* Please do not send the code that isn't yours.
  Or if you do not agree to publish it under the terms of MPL 2.0.
* Please, add *your* copyright to the files you add/modify.

Currently, the filter (even the C imlementation) is very very slow.
I was wondering if one may be able to write a faster version.
Or to optimize the existing C implementation.

I will likely merge a pull request with a working implementation written
in any suitable programming language (Go/C/D/Nim/Haskell/Lisp/Cobol?).
It just must be in a separate folder like the prototype does.
