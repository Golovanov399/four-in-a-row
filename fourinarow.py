#!/usr/bin/python2
# -*- coding: utf-8 -*-

import pyglet
from math import sin, cos, pi
import random
import sys


class Game(object):
    """The board is of size n*m, to win one has to put k his
    letters in a row (horizontal, vertical or diagonal)"""
    def __init__(self, turn='x', n=7, m=6, k=4):
        self.n, self.m, self.k = n, m, k
        self.field = [[] for i in xrange(self.n)]
        self.turn = turn

    def get_symb(self, x, y):
        return self.field[x][y] if 0 <= y < len(self.field[x]) else None

    def get_win_positions(self, x, y):
        dx = [1, 1, 0, -1]
        dy = [0, 1, 1, 1]
        symb = self.field[x][y]
        for i in xrange(len(dx)):
            result = [(x, y)]
            nx, ny = x + dx[i], y + dy[i]
            while (0 <= nx < self.n and 0 <= ny < len(self.field[nx]) and
                   self.field[nx][ny] == symb):
                result.append((nx, ny))
                nx += dx[i]
                ny += dy[i]
            nx, ny = x - dx[i], y - dy[i]
            while (0 <= nx < self.n and 0 <= ny < len(self.field[nx]) and
                   self.field[nx][ny] == symb):
                result.append((nx, ny))
                nx -= dx[i]
                ny -= dy[i]
            if len(result) >= self.k:
                return result

    def is_valid(self, x):
        return 0 <= x < self.n and len(self.field[x]) < self.m

    def erase_last(self, x):
        if len(self.field[x]) > 0:
            self.field[x].pop()

    def make_move(self, x, turn=None):
        if turn is None:
            turn = self.turn
        self.field[x].append(turn)
        return (x, len(self.field[x]) - 1)

    def new_instance(self):
        new_field = [x[:] for x in self.field]
        result = Game(self.turn)
        result.field = new_field
        return result

    def is_draw(self):
        for i in xrange(self.n):
            if len(self.field[i]) < self.m:
                return False
        return True


def draw_field_console(game):
    for i in xrange(game.m):
        toprint = []
        for j in xrange(game.n):
            if len(game.field[j]) >= game.m - i:
                toprint.append(game.field[j][game.m - i - 1])
            else:
                toprint.append(".")
        print "".join(toprint)


class Decision(object):
    def __init__(self, game, it=4, last=None):
        self.game = game.new_instance()
        self.win = None
        self.last = last
        self.it = it
        self.vars = []
        self.move = None
        if last:
            if game.get_win_positions(*last):
                self.win = (game.turn == game.get_symb(*last))
                return
        if self.win is None and it > 0:
            new_turn = 'x' if game.turn == 'o' else 'o'
            allwin = True
            for i in xrange(game.n):
                if game.is_valid(i):
                    new_game = game.new_instance()
                    new_game.turn = new_turn
                    new_last = new_game.make_move(i, game.turn)
                    self.vars.append((i, Decision(new_game, it - 1, new_last)))
                    if self.vars[-1][1].win is False:
                        self.move = i
                        self.win = True
                    if not self.vars[-1][1].win:
                        allwin = False
                    # if self.vars[-1][1].win:
                    # 	self.vars.pop()
            if allwin:
                self.win = False

    def deep(self):
        self.it += 1
        if self.it == 1:
            self.reset(self.game, self.it, self.last)
        else:
            self.win = None
            self.move = None
            to_delete = []
            allwin = True
            for x in self.vars:
                x[1].deep()
                if x[1].win is False:
                    self.move = x[0]
                    self.win = True
                if not x[1].win:
                    allwin = False
            if allwin:
                self.win = False

    def reset(self, game, it=4, last=None):
        self.game = game.new_instance()
        self.win = None
        self.last = last
        self.it = it
        self.vars = []
        self.move = None
        if last:
            if game.get_win_positions(*last):
                self.win = (game.turn == game.get_symb(*last))
                return
        if self.win is None and it > 0:
            new_turn = 'x' if game.turn == 'o' else 'o'
            allwin = True
            for i in xrange(game.n):
                if game.is_valid(i):
                    new_game = game.new_instance()
                    new_game.turn = new_turn
                    new_last = new_game.make_move(i, game.turn)
                    self.vars.append((i, Decision(new_game, it - 1, new_last)))
                    if self.vars[-1][1].win is False:
                        self.move = i
                        self.win = True
                    if not self.vars[-1][1].win:
                        allwin = False
            if allwin:
                self.win = False


class SmartBot(object):
    def __init__(self, game=None, symb='x'):
        if game:
            self.game = game.new_instance()
        else:
            self.game = Game()
        self.game.turn = symb
        self.dec = Decision(self.game)
        self.symb = symb
        self.nsymb = 'o' if symb == 'x' else 'x'

    def get_move(self):
        move = None
        if self.dec.win:
            move = self.dec.move
        else:
            valid_moves = []
            for x in self.dec.vars:
                if not x[1].win:
                    valid_moves.append(x[0])
            if len(valid_moves) == 0:
                move = None
            else:
                move = random.choice(valid_moves)

        if move is None:
            if len(self.dec.vars) == 0:
                return None
            move = random.choice(self.dec.vars)[0]
        pos = 0
        while pos < len(self.dec.vars) and self.dec.vars[pos][0] != move:
            pos += 1
        if pos == len(self.dec.vars):
            self.game = self.game.new_instance()
            self.game.make_move(move)
            self.game.turn = 'x' if self.game.turn == 'o' else 'o'
            self.dec = Decision(self.game)
        else:
            tmp = self.dec.vars[pos][1]
            del self.dec
            self.dec = tmp
            self.dec.deep()
        return move

    def was_move(self, x):
        pos = 0
        while pos < len(self.dec.vars) and self.dec.vars[pos][0] != x:
            pos += 1
        if pos == len(self.dec.vars):
            self.game = self.game.new_instance()
            self.game.make_move(x)
            self.game.turn = 'x' if self.game.turn == 'o' else 'o'
            self.dec = Decision(self.game)
        else:
            tmp = self.dec.vars[pos][1]
            del self.dec
            self.dec = tmp
            self.dec.deep()

    def print_state(self):
        if self.dec.win:
            print "I win"
            print "I go", self.move + 1, "and here is what happens:"
            pos = 0
            while self.dec.vars[pos][0] != move:
                pos += 1
            draw_field_console(self.dec.vars[pos][1].game)
        else:
            if self.dec.win is None:
                print "I don't know if I win"
            else:
                print "I lose"
            for x in self.dec.vars:
                print "If I go", x[0] + 1, "then here is what happens:"
                draw_field_console(x[1].game)


class RandomBot(object):
    def __init__(self, symb='x'):
        self.game = Game()
        self.symb = symb
        self.nsymb = 'o' if symb == 'x' else 'x'

    def get_move(self):
        valid_moves = []
        for i in xrange(self.game.n):
            if self.game.is_valid(i):
                valid_moves.append(i)
        move = None
        if len(valid_moves) > 0:
            move = random.choice(valid_moves)
        if move:
            self.game.make_move(move, self.symb)
        return move

    def was_move(self, move):
        self.game.make_move(move, self.nsymb)


class Player(object):
    def __init__(self, symb='x'):
        self.game = Game()
        self.symb = symb
        self.nsymb = 'o' if symb == 'x' else 'x'

    def get_move(self):
        while True:
            try:
                x = int(raw_input())
            except:
                continue
            if not self.game.is_valid(x - 1):
                continue
            self.game.make_move(x - 1, self.symb)
            return x - 1

    def was_move(self, move):
        self.game.make_move(move, self.nsymb)


def test_consoled():
    winrate = [0, 0]
    for i in xrange(16):
        winrate[1] += 1
        game = Game()
        player1 = SmartBot()
        player2 = RandomBot()
        turn = 'x'
        while True:
            if game.is_draw():
                print "Draw!"
                break
            last = None
            if turn == 'x':
                move = player1.get_move()
                if move is None:
                    print turn, "doesn't respond"
                    break
                last = game.make_move(move, turn)
                player2.was_move(move)
                # print
            else:
                move = player2.get_move()
                if move is None:
                    print turn, "doesn't respond"
                    winrate[0] += 1
                    break
                last = game.make_move(move, turn)
                player1.was_move(move)
                # print
            # draw_field_console(game)
            res = game.get_win_positions(*last)
            if res:
                print turn, "wins"
                if turn == 'x':
                    winrate[0] += 1
                break
            turn = 'o' if turn == 'x' else 'x'
    print "Smart bot won %d times of %d, %.2f%%" % (
        winrate[0], winrate[1], 100.0 * winrate[0] / winrate[1])


def draw_X(x, y):
    pyglet.graphics.draw_indexed(
        4, pyglet.gl.GL_QUADS, [0, 1, 2, 3],
        ('v2f', (sz * (x + .1), sz * (y + .2), sz * (x + .2), sz * (y + .1),
                 sz * (x + .9), sz * (y + .8), sz * (x + .8), sz * (y + .9))),
        ('c3B', (255, 0, 0, 255, 0, 0, 255, 0, 0, 255, 0, 0)),
    )
    pyglet.graphics.draw_indexed(
        4, pyglet.gl.GL_QUADS, [0, 1, 2, 3],
        ('v2f', (sz * (x + .1), sz * (y + .8), sz * (x + .2), sz * (y + .9),
                 sz * (x + .9), sz * (y + .2), sz * (x + .8), sz * (y + .1))),
        ('c3B', (255, 0, 0, 255, 0, 0, 255, 0, 0, 255, 0, 0)),
    )


def draw_O(x, y):
    n = 20		# it's exactly how I see it
    indices = []
    xs = []
    for i in xrange(n):
        xs.append(cos(2 * pi * i / n) * 0.4)
        xs.append(sin(2 * pi * i / n) * 0.4)
    for i in xrange(n):
        xs.append(cos(2 * pi * i / n) * 0.3)
        xs.append(sin(2 * pi * i / n) * 0.3)
    for i in xrange(n):
        j = (i + 1) % n
        indices += [i, j, j + n, i + n]
    for i in xrange(4 * n):
        xs[i] += sz * ((x if i % 2 == 0 else y) + xs[i] + 0.5)
    pyglet.graphics.draw_indexed(
        2 * n, pyglet.gl.GL_QUADS, indices,
        ('v2f', tuple(xs)),
        ('c3B', (0, 0, 255) * (2 * n)),
    )


def draw_colored_square(x, y, col):
    pyglet.graphics.draw_indexed(
        4, pyglet.gl.GL_QUADS, [0, 1, 2, 3],
        ('v2f', (sz * x, sz * y, sz * (x + 1), sz * y,
                 sz * (x + 1), sz * (y + 1), sz * x, sz * (y + 1))),
        ('c3B', col * 4),
    )


def draw_table_pyglet(game):
    n, m = game.n, game.m
    for i in xrange(1, n):
        pyglet.graphics.draw_indexed(
            4, pyglet.gl.GL_QUADS, [0, 1, 2, 3],
            ('v2f', (sz * (i - 0.005), 0, sz * (i + 0.005), 0,
                     sz * (i + 0.005), sz * m, sz * (i - 0.005), sz * m)),
            ('c3B', (255, 255, 255) * 4),
        )
    for i in xrange(1, m):
        pyglet.graphics.draw_indexed(
            4, pyglet.gl.GL_QUADS, [0, 1, 2, 3],
            ('v2f', (0, sz * (i - 0.005), 0, sz * (i + 0.005),
                     sz * n, sz * (i + 0.005), sz * n, sz * (i - 0.005))),
            ('c3B', (255, 255, 255) * 4),
        )
    for i in xrange(n):
        for j in xrange(len(game.field[i])):
            if game.field[i][j] == 'x':
                draw_X(i, j)
            else:
                draw_O(i, j)


if __name__ == "__main__":
    if "test" in sys.argv:
        test_consoled()
    else:
        sz = 100
        window = pyglet.window.Window(width=sz*7, height=sz*6)
        game = Game()

        bot = SmartBot()
        current = game.n
        playermove = -1
        ended = False

        @window.event
        def on_key_press(symbol, modifiers):
            global ended
            global current
            global playermove
            if ended:
                sys.exit(0)
            if symbol == pyglet.window.key.LEFT:
                current -= 1
                current %= (game.n + 1)
            elif symbol == pyglet.window.key.RIGHT:
                current += 1
                current %= (game.n + 1)
            elif symbol == pyglet.window.key.DOWN:
                if playermove == -1 and current < game.n:
                    playermove = current

        @window.event
        def on_draw():
            global playermove
            global ended
            window.clear()
            n, m = game.n, game.m
            for i in xrange(n):
                if i == current:
                    pyglet.graphics.draw_indexed(
                        4, pyglet.gl.GL_QUADS, [0, 1, 2, 3],
                        ('v2f', (i * sz, 0, (i + 1) * sz, 0,
                                 (i + 1) * sz, m * sz, i * sz, m * sz)),
                        ('c3B', (64, 12, 12) * 4),
                    )
            if not ended:
                if game.is_draw():
                    ended = True
                elif playermove > -1:
                    if game.is_valid(playermove):
                        last = game.make_move(playermove)
                        res = game.get_win_positions(*last)
                        if res:
                            for pos in res:
                                draw_colored_square(*pos, col=(96, 0, 0))
                            ended = True
                        else:
                            bot.was_move(playermove)
                            move = bot.get_move()
                            last = game.make_move(move, 'o')
                            res = game.get_win_positions(*last)
                            if res:
                                for pos in res:
                                    draw_colored_square(*pos, col=(0, 0, 96))
                                ended = True
                    playermove = -1
            draw_table_pyglet(game)

        # window.push_handlers(pyglet.window.event.WindowEventLogger())
        pyglet.app.run()
