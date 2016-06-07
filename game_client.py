#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import time
import pickle
from threading import Thread


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
        self.field = [[] for i in range(self.n)]
        self.turn = turn

    def get_symb(self, x, y):
        return self.field[x][y] if 0 <= y < len(self.field[x]) else None

    def get_win_positions(self, x, y):
        dx = [1, 1, 0, -1]
        dy = [0, 1, 1, 1]
        symb = self.field[x][y]
        for i in range(len(dx)):
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
        for i in range(self.n):
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
        print ("".join(toprint))


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
            for i in range(game.n):
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
            for i in range(game.n):
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
    for i in range(n):
        xs.append(cos(2 * pi * i / n) * 0.4)
        xs.append(sin(2 * pi * i / n) * 0.4)
    for i in range(n):
        xs.append(cos(2 * pi * i / n) * 0.3)
        xs.append(sin(2 * pi * i / n) * 0.3)
    for i in range(n):
        j = (i + 1) % n
        indices += [i, j, j + n, i + n]
    for i in range(4 * n):
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
    for i in range(1, n):
        pyglet.graphics.draw_indexed(
            4, pyglet.gl.GL_QUADS, [0, 1, 2, 3],
            ('v2f', (sz * (i - 0.005), 0, sz * (i + 0.005), 0,
                     sz * (i + 0.005), sz * m, sz * (i - 0.005), sz * m)),
            ('c3B', (255, 255, 255) * 4),
        )
    for i in range(1, m):
        pyglet.graphics.draw_indexed(
            4, pyglet.gl.GL_QUADS, [0, 1, 2, 3],
            ('v2f', (0, sz * (i - 0.005), 0, sz * (i + 0.005),
                     sz * n, sz * (i + 0.005), sz * n, sz * (i - 0.005))),
            ('c3B', (255, 255, 255) * 4),
        )
    for i in range(n):
        for j in range(len(game.field[i])):
            if game.field[i][j] == 'x':
                draw_X(i, j)
            else:
                draw_O(i, j)


def protocol(column, turn, ended):
    return {'column':column, 'turn':turn, 'ended':ended}


if __name__ == "__main__":

    sock = socket.socket()
    sock.connect(('localhost', 9090))
    data = pickle.loads(sock.recv(1024))
    player_turn = data['player_turn']
    other_player_turn = 'o'
    if player_turn == 'o':
        other_player_turn = 'x'
    print ('player_turn=', player_turn)
    print ('other_player_turn=', other_player_turn)

    sys.stdout.flush()

    sz = 100
    window = pyglet.window.Window(width=sz*7, height=sz*6)
    game = Game()

    current = game.n
    playermove = -1
    ended = False
    this_client_move = (player_turn == 'x')

    print ('this_client_move=', this_client_move)
    sys.stdout.flush()

    class Sender(Thread):
        def __init__(self):
            super(Sender, self).__init__()

        def run(self):
            global playermove
            global this_client_move
            while True:
                if this_client_move:
                    print ('this client move')
                    while playermove == -1:
                        time.sleep(0.1)
                    print ('kekoise')
                    last = game.make_move(playermove, player_turn)
                    res = game.get_win_positions(*last)
                    if res:
                        for pos in res:
                            draw_colored_square(*pos, col=(0, 0, 96))
                        ended = True
                        sock.send(pickle.dumps(protocol(playermove, player_turn, True)))
                    on_draw()
                    sock.send(pickle.dumps(protocol(playermove, player_turn, False)))
                    this_client_move = False
                else:
                    print ('other client move')
                    data = pickle.loads(sock.recv(1024))
                    last = game.make_move(data['column'], other_player_turn)
                    res = game.get_win_positions(*last)
                    if res:
                        for pos in res:
                            draw_colored_square(*pos, col=(0, 0, 96))
                        ended = True
                        sock.send(pickle.dumps(protocol(playermove, player_turn, True)))
                    on_draw()

                    this_client_move = True
                    playermove = -1


    t = Sender()
    t.start()


    @window.event
    def on_key_press(symbol, modifiers):
        print ('on_key_press1!')
        sys.stdout.flush()
        if not this_client_move:
            return
        print ('on key_press2!')
        sys.stdout.flush()
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

    def render(n, m, current):
        for i in range(n):
            if i == current:
                pyglet.graphics.draw_indexed(
                    4, pyglet.gl.GL_QUADS, [0, 1, 2, 3],
                    ('v2f', (i * sz, 0, (i + 1) * sz, 0,
                             (i + 1) * sz, m * sz, i * sz, m * sz)),
                    ('c3B', (64, 12, 12) * 4),
                )

    @window.event
    def on_draw():
        print('on_draw!1')
        sys.stdout.flush()
        global playermove
        global ended
        window.clear()
        n, m = game.n, game.m
        render(n, m, current)

        print('on draw2!')
        sys.stdout.flush()

        if game.is_draw():
            ended = True
            sock.send(pickle.loads(protocol(-1, player_turn, True)))
            draw_table_pyglet(game)
            return

        print ('on draw3!')

        draw_table_pyglet(game)

    # window.push_handlers(pyglet.window.event.WindowEventLogger())
    pyglet.app.run()



