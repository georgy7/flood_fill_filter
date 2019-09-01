#!/bin/sh

clang \
	-Wall \
	-O3 \
	-o c/flood \
	c/flood.c \
	-lm
