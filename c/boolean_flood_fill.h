
#include "Stack.h"

typedef struct FloodFiller {
    long * selected_points; // Array with capacity w*h (of the window).
    int selected_points_count;
    int startx;
    int starty;
    int min_x;
    int min_y;
    int max_x;
    int max_y;
    bool (*equal)(Filter *, int, int, int, int);
    bool * result;
    Filter * filter;
    long max_stack_length;
} FloodFiller;

typedef struct FloodFillerStackItem {
    int x;
    int y;
    int state;
} FloodFillerStackItem;

static inline FloodFillerStackItem * allocate(int x, int y, int state) {
    FloodFillerStackItem * result = malloc(sizeof(FloodFillerStackItem));
    result->x = x;
    result->y = y;
    result->state = state;
    return result;
}
static inline long stackLength(Stack * stack) {
    if (stack->last == NULL) {
        return 0;
    }

    long len = 1;
    Node * node = stack->last;
    while (node->next != NULL) {
        len++;
        node = node->next;
    }
    return len;
}


/// Add to the array like this is a set.
static inline void selected_points_add(FloodFiller * self, long value) {
    for (int i = 0; i < (self->selected_points_count); i++) {
        if (value == self->selected_points[i]) {
            return;
        }
    }
    self->selected_points[self->selected_points_count] = value;
    self->selected_points_count++;
}

static inline long key(int x, int y) {
    return ((long)x) * 1073676287 + y;
}
static inline void remember(FloodFiller * self, int x, int y) {
    selected_points_add(self, key(x, y));
}
static inline bool has(FloodFiller * self, int x, int y) {
    long k = key(x, y);
    for (int i = 0; i < self->selected_points_count; i++) {
        if (k == self->selected_points[i]) {
            return true;
        }
    }
    return false;
}


typedef struct BoolMatrix {
    int sum;
} BoolMatrix;

static void check_step(FloodFiller * self, Stack * check_stack);

static BoolMatrix processFloodFiller(FloodFiller * self) {
    Stack * check_stack = createStack();

    int resultHeight = self->max_y - self->min_y + 1;
    int resultWidth = self->max_x - self->min_x + 1;
    
    // logT(" >>>> x y %d %d\n", self->startx, self->starty);
    insertElement(check_stack, allocate(self->startx, self->starty, 0), 1);

    int counter = 0;
    while (stackLength(check_stack) > 0) {
        check_step(self, check_stack);
        counter++;
    }

    BoolMatrix bm;
    bm.sum = 0;

    for (int y = 0; y < resultHeight; y++) {
        for (int x = 0; x < resultWidth; x++) {
            if (self->result[y * resultWidth + x]) {
                bm.sum++;
            }
        }
    }

/*
    if (self->max_y < 100) {
        logT("maxy = %d, counter = %d, bm.sum = %d\n", self->max_y, counter, bm.sum);
    }
*/

    clearStack(check_stack);
    return bm;
}

static void popStack(Stack * stack) {
    void * v = getFieldValue(getElement(stack));
    if (v != 0) {
        free(v);
    }
    nextElement(stack);
}

static bool equals_to_start(FloodFiller * self, int x, int y) {
    return self->equal(self->filter, x, y, self->startx, self->starty);
}

static void remember_max_stack_length(FloodFiller * self, Stack * check_stack) {
    long current = stackLength(check_stack);
    self->max_stack_length = lmax(self->max_stack_length, current);
}

static void stop_check_step_if_it_is_time_to_stop(FloodFiller * self, Stack * check_stack) {
    int resultHeight = self->max_y - self->min_y + 1;
    int resultWidth = self->max_x - self->min_x + 1;

    int result_count = 0;
    for (int y = 0; y < resultHeight; y++) {
        for (int x = 0; x < resultWidth; x++) {
            if (self->result[y * resultWidth + x]) {
                result_count++;
            }
        }
    }

    float resultRatio = (float)(result_count - 1) / (float)(MAX_WINDOW_SIZE - 1);
    if (resultRatio > RATIO_THRESHOLD) {
        // Stop.
        while(check_stack->last != NULL){
            popStack(check_stack);
        }
    }
}

static void check_step(FloodFiller * self, Stack * check_stack) {
    FloodFillerStackItem * full_state = (FloodFillerStackItem*) getFieldValue(getElement(check_stack));
    int x = full_state->x;
    int y = full_state->y;
    int resultWidth = self->max_x - self->min_x + 1;

    // logT("x,min,max,start = %d %d %d %d    y,min,max,start = %d %d %d %d\n", x, self->min_x, self->max_x, self->startx, y, self->min_y, self->max_y, self->starty);
    if ((x < self->min_x) || (y < self->min_y) || (x > self->max_x) || (y > self->max_y)) {

        popStack(check_stack);

    } else if (full_state->state == 0) {
        
        // logT("full_state->state == 0\n");

        if (has(self, x, y)) {
            popStack(check_stack);
        } else if (equals_to_start(self, x, y)) {
            self->result[(y - self->min_y) * resultWidth + (x - self->min_x)] = true;
            full_state->state = 1;
            remember_max_stack_length(self, check_stack);
            stop_check_step_if_it_is_time_to_stop(self, check_stack);
        } else {
            popStack(check_stack);
        }
        remember(self, x, y);

    } else if (full_state->state == 1) {
        // logT("full_state->state == 1\n");
        insertElement(check_stack, allocate(x-1, y, 0), 1);
        full_state->state = 2;

    } else if (full_state->state == 2) {
        // logT("full_state->state == 2\n");
        insertElement(check_stack, allocate(x+1, y, 0), 1);
        full_state->state = 3;

    } else if (full_state->state == 3) {
        // logT("full_state->state == 3\n");
        insertElement(check_stack, allocate(x, y-1, 0), 1);
        full_state->state = 4;

    } else if (full_state->state == 4) {
        // logT("full_state->state == 4\n");
        popStack(check_stack);
        insertElement(check_stack, allocate(x, y+1, 0), 1);
    }
}



// ------------------------------

inline FloodFiller * newFloodFiller(
        Filter * filterPtr,
        bool (*compare)(struct Filter *, int, int, int, int)) {
    FloodFiller * filler = malloc(sizeof(FloodFiller));
    filler->selected_points = allocateLongsLayer(9, 9);
    filler->result = allocateBooleanLayer(9, 9);
    filler->equal = compare;
    filler->filter = filterPtr;
    filler->max_stack_length = 1;
    return filler;
}

inline void destructFloodFiller(FloodFiller * filler) {
    free(filler->selected_points);
    free(filler->result);
    free(filler);
}



struct BoolMatrix boolean_flood_fill(
        int x, int y, int l, int t, int r, int b,
        FloodFiller * filler) {

    filler->selected_points_count = 0;
    filler->startx = x;
    filler->starty = y;
    filler->min_x = l;
    filler->min_y = t;
    filler->max_x = r;
    filler->max_y = b;

    for (int i = 0; i < 81; i++) {
        filler->selected_points[i] = 0;
        filler->result[i] = false;
    }

    BoolMatrix result = processFloodFiller(filler);
    return result;
}
