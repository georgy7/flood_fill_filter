
/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

// Copyright (C) 2017 Georgy Ustinov

#define RATIO_THRESHOLD 0.45
#define MAX_WINDOW_SIZE 81
#define STACK_SIZE_ITEMS 100

#include "streams.h"
#include "window_flood_fill_filter.h"
#include <math.h>

/**
 * White is not very important.
 */
float white_lowering_function(float luma) {
    float t = 0.7;
    if (luma > t) {
        return luma - luma * 0.25 * ((luma - t) / (1.0 - t));
    } else {
        return luma;
    }
}

float * floodfiltered(float * yXYZ,
                      float * xXYZ,
                      float * zXYZ,
                      float y_threshold,
                      int32_t w,
                      int32_t h) {

    float * yGammaLowWhite = allocateLayer(w, h);
    for (long i = 0; i < w * h; i++) {
        float yGamma = pow(yXYZ[i], (1.0/2.2));
        yGammaLowWhite[i] = white_lowering_function(yGamma);
    }

    float * result = window_flood_fill_filter(
            yGammaLowWhite,
            y_threshold,
            xXYZ,
            zXYZ,
            w, h);

    for (long i = 0; i < w * h; i++) {
        if (result[i] > RATIO_THRESHOLD) {
            result[i] = 1.0;
        } else {
            result[i] = 0.0;
        }
    }

    free(yGammaLowWhite);
    return result;
}

int main() {
    float yThreshold = 0.1;

    // TODO парсить аргументы

    struct App app;
    start(&app);

    float * yXYZ = allocateLayer(app.w, app.h);
    float * xXYZ = allocateLayer(app.w, app.h);
    float * zXYZ = allocateLayer(app.w, app.h);
    float * resultLayer;

    for (long i = 0; i < app.w * app.h; i++) {
        float r = app.pixels[4*i + 0];
        float g = app.pixels[4*i + 1];
        float b = app.pixels[4*i + 2];
        yXYZ[i] = 0.2126 * r + 0.7152 * g + 0.0722 * b;
        xXYZ[i] = 0.4124 * r + 0.3576 * g + 0.1805 * b;
        zXYZ[i] = 0.0193 * r + 0.1192 * g + 0.9505 * b;
    }

    resultLayer = floodfiltered(
            yXYZ, xXYZ, zXYZ, yThreshold,
            app.w, app.h);

    free(yXYZ);
    free(xXYZ);
    free(zXYZ);

    for (long i = 0; i < app.w * app.h; i++) {
        app.result[4*i + 0] = resultLayer[i];
        app.result[4*i + 1] = resultLayer[i];
        app.result[4*i + 2] = resultLayer[i];
        app.result[4*i + 3] = 1.0;
    }

    free(resultLayer);

    end(&app);
    return 0;
}
