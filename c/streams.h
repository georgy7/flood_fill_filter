/**
 * This file is released into the public domain.
 * 
 * You may use it under the terms of the Unlicense.
 * For more information, please refer to <http://unlicense.org/>
 * 
 * Author: Georgy Ustinov
 */

#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdarg.h>
#include <stdbool.h>

#ifdef _WIN32
    #include <io.h>
    #include <fcntl.h>
#endif

struct App {
    int32_t w, h;
    float * pixels;
    float * result;
};

void logT(const char * format, ...) {
    va_list args;
    va_start (args, format);
    vfprintf(stderr, format, args);
    va_end (args);
}

void prepareStreams(struct App * appRef) {

    #ifdef _WIN32
    _setmode(_fileno(stdout), O_BINARY);
    _setmode(_fileno(stdin), O_BINARY);
    #endif

    read(0, &(appRef->w), sizeof(int32_t));
    read(0, &(appRef->h), sizeof(int32_t));

    fwrite(&(appRef->w), sizeof(int32_t), 1, stdout);
    fwrite(&(appRef->h), sizeof(int32_t), 1, stdout);
}

void readImage(struct App * appRef) {
    size_t countOfFloats = (appRef->w) * (appRef->h) * 4;

    (*appRef).pixels = calloc(countOfFloats, sizeof(float));
    (*appRef).result = calloc(countOfFloats, sizeof(float));

    size_t floatsRead = fread((appRef->pixels), sizeof(float), countOfFloats, stdin);
    // logT("\n%zd floats read.\n\n", floatsRead);
}

void start(struct App * appRef) {
    prepareStreams(appRef);
    readImage(appRef);
}

void end(struct App * appRef) {
    fwrite((*appRef).result, sizeof(float), (*appRef).w * (*appRef).h * 4, stdout);
    free((*appRef).pixels);
    free((*appRef).result);
}

float * allocateLayer(int32_t w, int32_t h) {
    float * layer = calloc(w * h, sizeof(float));
    return layer;
}

bool * allocateBooleanLayer(int32_t w, int32_t h) {
    bool * layer = calloc(w * h, sizeof(bool));
    return layer;
}
