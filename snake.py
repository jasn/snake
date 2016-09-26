#!/usr/bin/python
import curses
import sys
import time
from random import randint

FOOD_SYMBOL = 'F'

class Board(object):

    def __init__(self, stdscr):
        # board setup
        self.xmin = 0
        self.xmax = 20
        self.ymin = 0
        self.ymax = 20

        # curses setup
        self.snake_color_pair = 1
        self.food_color_pair = 2
        self.background_color_pair = 3
        self.border_color_pair = 4
        self.text_color_pair = 5
        curses.init_pair(self.snake_color_pair,
                         curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(self.food_color_pair,
                         curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(self.background_color_pair,
                         curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(self.border_color_pair,
                         curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(self.text_color_pair,
                         curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)
        stdscr.refresh()
        stdscr.nodelay(True)

        self.stdscr = stdscr       

        self.snake = Snake()
        self.food = Food(self)

        self.border = [complex(x, y) for y in range(self.ymin, self.ymax, 1)
                       for x in [self.xmin, self.xmax]]

        self.border += [complex(x, y) for x in range(self.xmin, self.xmax, 1)
                        for y in [self.ymin, self.ymax]]
        self.border = list(set(self.border))


    def check_food(self):
        return self.snake.positions[-1] == self.food.position

    def check_collision(self):
        head = self.snake.positions[-1]
        if head in self.border:  # snake hits border
            return True
        if head in self.snake.positions[:-1]:  # snake hits itself
            return True
        return False
    
    def replace_food(self):
        while self.food.position in self.snake.positions:
            self.food.eaten()

    def play(self):
        stdscr = self.stdscr
        time_to_grow = 0
        while True:
            time.sleep(0.125)
            found_food = self.check_food()
            collision = self.check_collision()
            if collision:
                stdscr.addstr(self.xmax+1, self.ymin+1,
                              "You died!",
                              curses.color_pair(self.text_color_pair))
                stdscr.refresh()
                break
            if found_food:
                time_to_grow += 2
                self.replace_food()
            k = stdscr.getch()
            if k == curses.KEY_UP:
                stdscr.addstr(0, 100, "up!", curses.color_pair(1))
                self.snake.move(direction=complex(-1, 0),
                                grow=(time_to_grow > 0))
            elif k == curses.KEY_DOWN:
                stdscr.addstr(0, 100, "down!", curses.color_pair(1))
                self.snake.move(direction=complex(1, 0),
                                grow=(time_to_grow > 0))
            elif k == curses.KEY_LEFT:
                stdscr.addstr(0, 100, "left!", curses.color_pair(1))
                self.snake.move(direction=complex(0, -1),
                                grow=(time_to_grow > 0))
            elif k == curses.KEY_RIGHT:
                stdscr.addstr(0, 100, "right!", curses.color_pair(1))
                self.snake.move(direction=complex(0, 1),
                                grow=(time_to_grow > 0))
            elif k == ord('q'):
                stdscr.addstr(0, 100, "Quitting!", curses.color_pair(1))
                stdscr.refresh()
                break
            elif k == ord('m'):
                stdscr.addstr(0, 100, "Moving!", curses.color_pair(1))
                self.snake.move(grow=(time_to_grow > 0))
            elif k == curses.ERR:
                self.snake.move(grow=(time_to_grow > 0))
            self.draw()
            stdscr.refresh()
            if time_to_grow > 0:
                time_to_grow -= 1

        # terminate
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()    

    def draw(self):
        stdscr = self.stdscr
        for x in range(self.xmin, self.xmax, 1):
            for y in range(self.ymin, self.ymax, 1):
                stdscr.addstr(x, y, ' ', self.background_color_pair)

        snake_positions = self.snake.positions
        food_position = self.food.position

        self._draw_food(food_position)
        self._draw_border()
        self._draw_snake(snake_positions)

    def _draw_food(self, food_position):
        x, y = int(food_position.real), int(food_position.imag)
        self.stdscr.addstr(x, y, FOOD_SYMBOL, self.food_color_pair)
        
    def _draw_snake(self, snake_positions):
        for x, y in [(int(c.real), int(c.imag)) for c in snake_positions]:
            self.stdscr.addstr(x, y, 'X', curses.color_pair(self.snake_color_pair))

    def _draw_border(self):
        for y in range(self.ymin, self.ymax, 1):
            for x in [self.xmin, self.xmax]:
                self.stdscr.addstr(x, y, '-',
                                   curses.color_pair(self.border_color_pair))
    
        for x in range(self.xmin, self.xmax, 1):
            for y in [self.ymin, self.ymax]:
                self.stdscr.addstr(x, y, '|',
                                   curses.color_pair(self.border_color_pair))

        for x in [self.xmin, self.xmax]:
            for y in [self.ymin, self.ymax]:
                self.stdscr.addstr(x, y, '+',
                                   curses.color_pair(self.border_color_pair))

class Food(object):

    def __init__(self, board):
        self.board = board
        self.position = self._get_new_position()
        
    def eaten(self):
        self.position = self._get_new_position()
        
    def _get_new_position(self):
        board = self.board
        return complex(randint(board.xmin+1, board.xmax-1),
                       randint(board.ymin+1, board.ymax-1))
        
class Snake(object):

    def __init__(self):
        self.positions = [complex(1, 1), complex(1, 2), complex(1, 3), complex(1, 4)]
        self.direction = complex(0, 1)
        self.old_tail = self.positions[0]
        
    def _implicit_direction(self):
        return self.positions[-1] - self.positions[-2]

    def valid(self, direction):
        return self._implicit_direction() != -direction

    def head(self):
        return self.positions[-1]
    
    def foodAtHead(self):
        return self.head() == self.food.position
        
    def move(self, direction=None, grow=False):
        if direction is not None and self.valid(direction):
            new_direction = direction
        else:
            new_direction = self._implicit_direction()
        self.old_tail = self.positions[0]

        if grow:
            self.positions += [(self.positions[-1] + new_direction)]
        else:
            self.positions = (self.positions[1:]
                              + [(self.positions[-1] + new_direction)])


def main(stdscr):
    board = Board(stdscr)
    board.play()

if __name__ == "__main__":
    curses.wrapper(main)
