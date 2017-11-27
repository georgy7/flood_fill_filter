
/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

// Author: Georgy Ustinov
// November 2017

/*
This is a window filter.
It uses 9x9 window (smaller near the borders of the image).

From the center of the window, the filter makes flood fill.
The result is the count of the filled pixels (except for
the current) divided by the total number of pixels (except
for the current).
*/

// Chroma is less important than luma.
// This is the importance (0-1).
#define CHROMA_FACTOR 0.25

#include <math.h>

static inline int imax(int a, int b) {
    return (a > b) ? a : b;
}
static inline long lmax(long a, long b) {
    return (a > b) ? a : b;
}

static inline int imin(int a, int b) {
    return (a < b) ? a : b;
}


typedef struct Filter {
    float y_threshold;
    float * yGammaLowWhite;
    float * xXYZ;
    float * zXYZ;
    int h;
    int w;
    int radius;
} Filter;

#include "boolean_flood_fill.h"

static float process_window(Filter * self, int x, int y, FloodFiller * floodFiller);
static float window_square(int left_border, int right_border, int top_border, int bottom_border);
bool compare(Filter * self, int x1, int y1, int x2, int y2);

static float * process(Filter * self) {
    float * result = allocateLayer(self->w, self->h);

    FloodFiller * floodFiller = newFloodFiller(self, &compare);

    for (int y = 0; y < (self->h); y++) {
        for (int x = 0; x < (self->w); x++) {
            result[(self->w) * y + x] = process_window(self, x, y, floodFiller);
        }
    }

    logT("The maximum stack length is %d.\n", floodFiller->max_stack_length);

    destructFloodFiller(floodFiller);
    return result;
}

bool compare(Filter * self, int x1, int y1, int x2, int y2) {
    bool y_equal = (fabsf(
            self->yGammaLowWhite[(self->w) * y1 + x1] -
            self->yGammaLowWhite[(self->w) * y2 + x2]) < (self->y_threshold));

    //logT("x1,y1,x2,y2 = %d %d %d %d\t\tyG1,yG2 = %f %f\n\t\t\ty_threshold = %f\n", x1,y1,x2,y2,self->yGammaLowWhite[(self->w) * y1 + x1], self->yGammaLowWhite[(self->w) * y2 + x2], self->y_threshold);
    if (y_equal && ((self->yGammaLowWhite[(self->w) * y1 + x1] > 0.9) ||
            (self->yGammaLowWhite[(self->w) * y2 + x2] > 0.9))) {
        return true;
    }

    float tf = self->y_threshold / CHROMA_FACTOR;
    float xd = fabsf(self->xXYZ[(self->w) * y1 + x1] - self->xXYZ[(self->w) * y2 + x2]);
    float zd = fabsf(self->zXYZ[(self->w) * y1 + x1] - self->zXYZ[(self->w) * y2 + x2]);

    if (y_equal && ((self->yGammaLowWhite[(self->w) * y1 + x1] > 0.5) ||
            (self->yGammaLowWhite[(self->w) * y2 + x2] > 0.5)) &&
            (xd < tf / 0.5) && (zd < tf / 0.5)) {
        return true;
    } else {
        return y_equal && (xd < tf) && (zd < tf);
    }
}

static float process_window(Filter * self, int x, int y, FloodFiller * floodFiller) {
    int radius = self->radius;
    int l = imax(0, x - radius);
    int t = imax(0, y - radius);
    int r = imin((self->w) - 1, x + radius);
    int b = imin((self->h) - 1, y + radius);

    struct BoolMatrix boolmatrix = boolean_flood_fill(x, y, l, t, r, b, floodFiller);
    float count = boolmatrix.sum - 1;

    float square = window_square(l, r, t, b) - 1;
    float ratio = count / square;

/*
    if (count >= 0) {
        logT("count = %f, square = %f, ratio = %f\n", count, square, ratio);
    }
*/

    return ratio;
}

static float window_square(int left_border, int right_border, int top_border, int bottom_border) {
    return (1 + right_border - left_border) * (1 + bottom_border - top_border);
}

// ----------------------------

float * window_flood_fill_filter(
        float * yGammaLowWhite,
        float y_threshold, float * xXYZ, float * zXYZ,
        int32_t w, int32_t h
) {
    Filter f;
    f.radius = 4;
    f.y_threshold = y_threshold;
    f.yGammaLowWhite = yGammaLowWhite;
    f.xXYZ = xXYZ;
    f.zXYZ = zXYZ;
    f.w = w;
    f.h = h;

    float * result = process(&f);
    return result;
}
