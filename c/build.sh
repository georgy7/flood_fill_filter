#!/bin/sh

clang \
	-Ic/LorhanSohaky_Stack \
	-Wall \
	-O3 \
	-o c/flood \
	c/flood.c \
	-lm
