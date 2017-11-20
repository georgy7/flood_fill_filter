#!/bin/sh

clang \
	-Ic/LorhanSohaky_Stack \
	-Wall \
	-o c/flood \
	c/flood.c \
	c/LorhanSohaky_Stack/Stack.c \
	c/LorhanSohaky_Stack/GenericField.c \
	-lm
