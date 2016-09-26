#!/usr/bin/python
import curses
import sys
import time
from random import randint

FOOD_SYMBOL = 'F'

class Food(object):

    def __init__(self, stdscr, position, color_pair):
        self.position = position
        self.stdscr = stdscr
        self.color_pair = color_pair
        self.draw()
        
    def eaten(self):
        self.position = complex(randint(0, 50), randint(0, 50))
        self.draw()

    def draw(self):
        x, y = int(self.position.real), int(self.position.imag)
        self.stdscr.addstr(x, y, FOOD_SYMBOL, self.color_pair)
        

class Snake(object):

    def __init__(self, stdscr, color_pair, food):
        self.positions = [complex(0, 0), complex(0, 1), complex(0, 2), complex(0, 3)]
        self.stdscr = stdscr
        self.color_pair = color_pair
        self.direction = complex(0, 1)
        self.old_tail = self.positions[0]
        self.time_to_grow = 0
        self.food = food
        
    def _implicit_direction(self):
        return self.positions[-1] - self.positions[-2]


    def valid(self, direction):
        return self._implicit_direction() != -direction

    def head(self):
        return self.positions[-1]
    
    def foodAtHead(self):
        return self.head() == self.food.position
        
    def move(self, direction=None):
        if direction is not None and self.valid(direction):
            new_direction = direction
        else:
            new_direction = self._implicit_direction()
        self.old_tail = self.positions[0]

        if self.foodAtHead():
            self.time_to_grow += 2
            self.food.eaten()
        
        if self.time_to_grow > 0:
            self.time_to_grow -= 1
            self.positions += [(self.positions[-1] + new_direction)]
        else:
            self.positions = (self.positions[1:]
                              + [(self.positions[-1] + new_direction)])

    def draw(self):
        for x, y in [(int(c.real), int(c.imag)) for c in self.positions]:
            self.stdscr.addstr(x, y, 'X', curses.color_pair(self.color_pair))
        x, y = int(self.old_tail.real), int(self.old_tail.imag)
        self.stdscr.addstr(x, y, ' ', curses.color_pair(self.color_pair))



def main(stdscr):
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    stdscr.refresh()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    snake = Snake(stdscr, 1, Food(stdscr, complex(10, 10), 2))
    stdscr.nodelay(True)
    while True:
        time.sleep(0.1)
        k = stdscr.getch()
        if k == curses.KEY_UP:
            stdscr.addstr(0, 100, "up!", curses.color_pair(1))
            snake.move(direction=complex(-1, 0))
        elif k == curses.KEY_DOWN:
            stdscr.addstr(0, 100, "down!", curses.color_pair(1))
            snake.move(direction=complex(1, 0))
            pass
        elif k == curses.KEY_LEFT:
            stdscr.addstr(0, 100, "left!", curses.color_pair(1))
            snake.move(direction=complex(0, -1))
            pass
        elif k == curses.KEY_RIGHT:
            stdscr.addstr(0, 100, "right!", curses.color_pair(1))
            snake.move(direction=complex(0, 1))
            pass
        elif k == ord('q'):
            stdscr.addstr(0, 100, "Quitting!", curses.color_pair(1))
            stdscr.refresh()
            break
        elif k == ord('m'):
            stdscr.addstr(0, 100, "Moving!", curses.color_pair(1))
            snake.move()
        elif k == curses.ERR:
            snake.move()
        snake.draw()
        stdscr.refresh()
        
    # terminate
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()


if __name__ == "__main__":
    curses.wrapper(main)
