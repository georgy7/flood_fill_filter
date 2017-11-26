
## Usage

```
$ c/build.sh

$ lineara samples/1to_fragment1.png | c/flood | lineara -b test.png
```

## Performance

```
% time ./test_py.sh 
Image 454x206 (3 channels).
Using default threshold: 0.1
0-0 processed.
0-1 processed.
...
0-204 processed.
0-205 processed.
STDIN image size: 454x206.
131.26466250419617
131.357u 0.015s 2:11.41 99.9%   5+167k 272+1io 0pf+0w

% time ./test_c.sh 
Image 454x206 (3 channels).
STDIN image size: 454x206.
20.916u 0.007s 0:20.92 99.9%    15+167k 9+1io 0pf+0w
```

131.4 / 20.9 ~= 6 times faster

## Third-party code

https://github.com/LorhanSohaky/Stack (MIT)
