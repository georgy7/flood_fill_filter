# -*- coding: utf-8 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Author: Georgy Ustinov
# November 2017

"""
The idea is to inject the comparison function from outside.

The function is like

    equal(x1,y1,x2,y2): boolean

Example:

    result = u.boolean_flood_fill(471, 140, 0, 0, 799, 599,
                                  lambda x1, y1, x2, y2: (abs(yXYZ[y1, x1] - yXYZ[y2, x2]) < y_threshold))
"""

import numpy as np

def boolean_flood_fill(x, y, min_x, min_y, max_x, max_y, equal):
    filler = FloodFiller(x, y, min_x, min_y, max_x, max_y, equal)
    return filler.process()

class FloodFiller:
    def __init__(self, startx, starty, min_x, min_y, max_x, max_y, equal):
        self.selected_points = set()
        self.startx = startx
        self.starty = starty
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y
        self.equal = equal
        self.result = np.zeros((max_y - min_y + 1, max_x - min_x + 1), dtype=bool)

    def key(self, x, y):
        return x * 1073676287 + y

    def remember(self, x, y):
        self.selected_points.add(self.key(x, y))

    def has(self, x, y):
        return self.key(x, y) in self.selected_points

    def process(self):
        check_stack = []
        check_stack.append([self.startx, self.starty, 0])
        while len(check_stack) > 0:
            self.check_step(check_stack)
        return self.result

    def check_step(self, check_stack):
        full_state = check_stack[-1]
        x, y = full_state[0], full_state[1]

        if (x < self.min_x) or (y < self.min_y) or (x > self.max_x) or (y > self.max_y):
            check_stack.pop()

        elif full_state[2] == 0:
            if self.has(x, y):
                check_stack.pop()
            elif self.equals_to_start(x, y):
                self.result[y-self.min_y, x-self.min_x] = True
                full_state[2] = 1
            else:
                check_stack.pop()
            self.remember(x, y)
        elif full_state[2] == 1:
            check_stack.append([x-1, y, 0])
            full_state[2] = 2
        elif full_state[2] == 2:
            check_stack.append([x+1, y, 0])
            full_state[2] = 3
        elif full_state[2] == 3:
            check_stack.append([x, y-1, 0])
            full_state[2] = 4
        elif full_state[2] == 4:
            check_stack.pop()
            check_stack.append([x, y+1, 0])

    def equals_to_start(self, x, y):
        return self.equal(x, y, self.startx, self.starty)

