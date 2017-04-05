#!/usr/bin/python3.2


class State:
    FLAGGED, DUG, UNTOUCHED = tuple(range(3))

    def __init__(self, has_bomb, state):
        if state not in range(3):
            raise ValueError("State must be either FLAGGED, DUG or UNTOUCHED")
        self.has_bomb = has_bomb
        self.state = state


class Board:

    def __init__(self, size):
        self.size = size
        self.squares = []

        # TO-DO Properly implement this method
        for i in range(size):
            self.squares.append(list())

            for j in range(size):
                self.squares[i].append(State(False, State.UNTOUCHED))

    def __len__(self):
        return self.size

    def __getitem__(self, item):
        return self.squares[item]

    def __iter__(self):
        return iter(self.squares)

    def __contains__(self, key):
        return key[0] < len(self.squares) and key[1] < len(self.squares[0])

    def set_state(self, x, y, state):
        self.squares[x][y] = state

    def get_state(self, x, y):
        return self.squares[x][y].state

    def has_bomb(self, x, y):
        return self.squares[x][y].has_bomb == True
