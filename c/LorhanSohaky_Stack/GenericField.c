/*
The MIT License (MIT)
Copyright (c) 2015 Lorhan Sohaky
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

#include <stdlib.h>
#include <GenericField.h>

/*Function to malloc a new GenericField*/
GenericField *setField(const int type,void *value){
	if(type<0){
		return NULL;
	}
    GenericField *field;
    field=(GenericField *)malloc(sizeof(GenericField));
	if(field==NULL){
		return NULL;
	}
    field->Type=type;
    field->Value=value;
    return field;
}

/* Function to get the value of the GenericField*/
void *getFieldValue(const GenericField *field){
    if(field!=NULL){
        return field->Value;
    }
    return NULL;
}

/* Function to get a type of the GenericField*/
int getFieldType(const GenericField *field){
    if(field!=NULL){
        return field->Type;
    }
    return -1;
}
