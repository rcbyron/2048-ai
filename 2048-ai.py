import random
import pyglet
import sys

from pyglet.window import key
from pyglet.gl import (GL_COLOR_BUFFER_BIT, GL_TRIANGLE_STRIP, GL_BLEND,
                       GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, glClear,
                       glEnable, glDisable, glBlendFunc)


class TransparentGroup(pyglet.graphics.Group):
    def set_state(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def unset_state(self):
        glDisable(GL_BLEND)


SQ_SIZE = 58
SPACING = 10

BG_COLORS = {
    1: ('c3B', (238, 228, 219, 238, 228, 219, 238, 228, 219, 238, 228, 219)),
    2: ('c3B', (237, 224, 201, 237, 224, 201, 237, 224, 201, 237, 224, 201)),
    3: ('c3B', (241, 177, 125, 241, 177, 125, 241, 177, 125, 241, 177, 125)),
    4: ('c3B', (243, 149, 104, 243, 149, 104, 243, 149, 104, 243, 149, 104)),
    5: ('c3B', (243, 127, 100, 243, 127, 100, 243, 127, 100, 243, 127, 100)),
    6: ('c3B', (244, 96, 67, 244, 96, 67, 244, 96, 67, 244, 96, 67)),
    7: ('c3B', (236, 206, 120, 236, 206, 120, 236, 206, 120, 236, 206, 120)),
    8: ('c3B', (237, 204, 97, 237, 204, 97, 237, 204, 97, 237, 204, 97)),
    9: ('c3B', (237, 200, 80, 237, 200, 80, 237, 200, 80, 237, 200, 80)),
    10: ('c3B', (237, 197, 63, 237, 197, 63, 237, 197, 63, 237, 197, 63)),
    11: ('c3B', (237, 194, 46, 237, 194, 46, 237, 194, 46, 237, 194, 46)),
    12: ('c3B', (119, 110, 101, 119, 110, 101, 119, 110, 101, 119, 110, 101)),
    13: ('c3B', (119, 110, 101, 119, 110, 101, 119, 110, 101, 119, 110, 101)),
    14: ('c3B', (119, 110, 101, 119, 110, 101, 119, 110, 101, 119, 110, 101)),
}
TEXT_COLORS = {
    1: (119, 110, 101, 255),
    2: (255, 255, 255, 255),
}
LOST_SCREEN_COLOR = ('c4B', (238, 228, 219, 128,
                             238, 228, 219, 128,
                             238, 228, 219, 128,
                             238, 228, 219, 128))

WINDOW = pyglet.window.Window(280, 280)
BACKGROUND = pyglet.graphics.OrderedGroup(0)
FOREGROUND = pyglet.graphics.OrderedGroup(1)

BG = pyglet.image.load('bg.png')
BG_SPRITE = pyglet.sprite.Sprite(BG)

FULL_SCREEN_VECTOR = ('v2f', (0, 0,
                              0, WINDOW.height,
                              WINDOW.width, 0,
                              WINDOW.width, WINDOW.height))

LOST_SCREEN = pyglet.graphics.Batch()
LOST_SCREEN.add_indexed(4, GL_TRIANGLE_STRIP,
                        TransparentGroup(), [0, 1, 2, 3],
                        FULL_SCREEN_VECTOR,
                        LOST_SCREEN_COLOR)
LOST_TEXT = pyglet.text.Label('Final Score: 0',
                              font_name='Arial',
                              font_size=18,
                              x=WINDOW.width//2, y=WINDOW.height//2,
                              anchor_x='center', anchor_y='center',
                              batch=LOST_SCREEN, group=FOREGROUND)


class Tile:
    def __init__(self, val, x, y):
        self.val = val
        self.x = x
        self.y = y
        self.merged_flag = False

    def move(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return str(self.val)+' at '+str(self.x)+', '+str(self.y)


class GraphicTile(Tile):
    def __init__(self, val, x, y):
        super().__init__(val, x, y)
        self.gx = lambda: self.x * (SQ_SIZE+SPACING) + SPACING
        self.gy = lambda: WINDOW.height - (self.y+1) * (SQ_SIZE+SPACING)  # 0, 0 is bottom-left
        self.batch = pyglet.graphics.Batch()
        self.v_list = self.batch.add_indexed(4, GL_TRIANGLE_STRIP,
                                             BACKGROUND, [0, 1, 2, 3],
                                             ('v2f', (self.gx(), self.gy(),
                                                      self.gx(), self.gy()+SQ_SIZE,
                                                      self.gx()+SQ_SIZE, self.gy(),
                                                      self.gx()+SQ_SIZE, self.gy()+SQ_SIZE)),
                                             BG_COLORS[1])
        self.label = pyglet.text.Label(str(2**val),
                                       font_name='Arial',
                                       bold=True,
                                       font_size=32,
                                       color=TEXT_COLORS[1],
                                       x=self.gx()+SQ_SIZE//2, y=self.gy()+SQ_SIZE//2,
                                       anchor_x='center', anchor_y='center',
                                       batch=self.batch, group=FOREGROUND)
        if self.val in BG_COLORS:
            self.v_list.colors = BG_COLORS[self.val][1]

    def move(self, x, y):
        super().move(x, y)
        self.v_list.vertices = [self.gx(), self.gy(),
                                self.gx(), self.gy()+SQ_SIZE,
                                self.gx()+SQ_SIZE, self.gy(),
                                self.gx()+SQ_SIZE, self.gy()+SQ_SIZE]
        self.label.x = self.gx()+SQ_SIZE//2
        self.label.y = self.gy()+SQ_SIZE//2
        self.label.text = str(2**self.val)

        if self.val in BG_COLORS:
            self.v_list.colors = BG_COLORS[self.val][1]

        if self.val > 9:
            self.label.font_size = 16
        elif self.val > 6:
            self.label.font_size = 24
        elif self.val > 2:
            self.label.color = TEXT_COLORS[2]


class Board:
    def __init__(self, graphic=False):
        self.graphic = graphic
        self.board = [[None for i in range(4)] for j in range(4)]
        self.score = 0
        self.lost = False

    def show(self):
        for i in range(0, 4):
            for j in range(0, 4):
                if self.board[i][j] is None:
                    print('_ ', end='')
                else:
                    print(str(self.board[i][j].val)+' ', end='')
            print()

    def inbounds(self, x, y):
        return 0 <= y and y < len(self.board) and 0 <= x and x < len(self.board[0])

    def exist(self, x, y):
        return self.inbounds(x, y) and self.board[y][x] is not None

    def get_empty_spots(self):
        empty_spots = []
        for y in range(0, 4):
            for x in range(0, 4):
                if self.board[y][x] is None:
                    empty_spots.append((x, y))
        return empty_spots

    def spawn_tile(self):
        empty_spots = self.get_empty_spots()
        if len(empty_spots) is 0:
            return False

        spot = random.choice(empty_spots)
        if not self.graphic:
            if random.random() < 0.90:
                self.board[spot[1]][spot[0]] = Tile(1, spot[0], spot[1])
            else:
                self.board[spot[1]][spot[0]] = Tile(2, spot[0], spot[1])
        else:
            if random.random() < 0.90:
                self.board[spot[1]][spot[0]] = GraphicTile(1, spot[0], spot[1])
            else:
                self.board[spot[1]][spot[0]] = GraphicTile(2, spot[0], spot[1])
        return True

    @staticmethod
    def mini_shift(tile_line):
        # Shift one row or column forward
        moved_flag = False
        points = 0
        for i in range(0, 3):
            r = 2-i
            if tile_line[r] is not None:
                z = r
                while z < 3:
                    if tile_line[z+1] is not None:
                        break
                    z += 1
                if tile_line[z] is None:
                    # If found a new empty spot, swap tiles
                    tile_line[z] = tile_line[r]
                    tile_line[r] = None
                    moved_flag = True
                # Check for merge
                if z < 3 and not tile_line[z+1].merged_flag and \
                   tile_line[z+1].val is tile_line[z].val:
                    tile_line[z+1].val += 1
                    points += 2**tile_line[z+1].val
                    tile_line[z+1].merged_flag = True
                    tile_line[z] = None
                    moved_flag = True
        return (tile_line, moved_flag, points)

    def shift(self, direction):
        moved_flag = False
        if direction is 'w' or direction is 's':
            for col in range(0, 4):
                tile_line = [self.board[row][col] for row in range(0, 4)]
                if direction is 'w':
                    tile_line.reverse()
                shifted_tiles, made_move, points = Board.mini_shift(tile_line)
                self.score += points
                moved_flag |= made_move
                if direction is 'w':
                    shifted_tiles.reverse()
                for row in range(0, 4):
                    self.board[row][col] = shifted_tiles[row]
        elif direction is 'a' or direction is 'd':
            for row in range(0, 4):
                tile_line = list(self.board[row])
                if direction is 'a':
                    tile_line.reverse()
                shifted_tiles, made_move, points = Board.mini_shift(tile_line)
                self.score += points
                moved_flag |= made_move
                if direction is 'a':
                    shifted_tiles.reverse()
                self.board[row] = shifted_tiles
        return moved_flag

    def check_loss(self):
        for y in range(0, 4):
            for x in range(0, 4):
                if self.board[y][x] is None or \
                   (self.exist(x-1, y) and self.board[y][x-1].val is self.board[y][x].val) or \
                   (self.exist(x+1, y) and self.board[y][x+1].val is self.board[y][x].val) or \
                   (self.exist(x, y-1) and self.board[y-1][x].val is self.board[y][x].val) or \
                   (self.exist(x, y+1) and self.board[y+1][x].val is self.board[y][x].val):
                    return False
        return True

    def computer_move(self):
        for row in range(0, 4):
            for col in range(0, 4):
                if self.board[row][col] is not None:
                    self.board[row][col].move(col, row)
                    self.board[row][col].merged_flag = False
        self.spawn_tile()
        self.lost |= self.check_loss()

    def hash(self):
        return hash(tuple(tuple(row) for row in self.board))


@WINDOW.event
def on_key_press(symbol, modifiers):
    moved_flag = False
    if symbol is key.UP or symbol is key.W:
        moved_flag = board.shift('w')
    elif symbol is key.RIGHT or symbol is key.D:
        moved_flag = board.shift('d')
    elif symbol is key.DOWN or symbol is key.S:
        moved_flag = board.shift('s')
    elif symbol is key.LEFT or symbol is key.A:
        moved_flag = board.shift('a')
    if moved_flag:
        board.computer_move()


@WINDOW.event
def on_draw():
    glClear(GL_COLOR_BUFFER_BIT)
    BG_SPRITE.y = WINDOW.height - BG_SPRITE.height
    BG_SPRITE.draw()

    for row in board.board:
        for tile in row:
            if tile is not None:
                tile.batch.draw()
    if board.lost:
        LOST_TEXT.text = "Final Score: "+str(board.score)
        LOST_SCREEN.draw()


""" ------------ AI STUFF ------------ """

# Board masks
COL_MASK = 0xF000F000F000F000
ROW_MASK = 0xFFFF000000000000
EDGE_MASK = 0xF00FF00FF00FF00F
FIRST_MASK = 0xF000000000000000
TWO_MASK = 0x2000000000000000
FOUR_MASK = 0x4000000000000000

# Tuning parameters and weights
MAX_DEPTH = 4
EMPTY_TILE_POINTS = 12
SMOOTHNESS_WEIGHT = 30
EDGE_WEIGHT = 30
LOSS_PENALTY = -200000
MONOTONICITY_POWER = 4.0
MONOTONICITY_WEIGHT = 47.0
SUM_POWER = 3.5
SUM_WEIGHT = 11.0
MERGES_WEIGHT = 700.0
EMPTY_WEIGHT = 270.0

MOVE_TABLE_DEPTH = 12
MOVE_TESTS = {
    (0x0001, False): (0x0001, 0),
    (0x1111, False): (0x0022, 8),
    (0x5500, False): (0x0006, 64),
    (0x1000, False): (0x0001, 0),
    (0xC0C0, False): (0x000D, 8192),
    (0x2030, False): (0x0023, 0),
    (0x0001, True): (0x1000, 0),
    (0x1111, True): (0x2200, 8),
    (0x0088, True): (0x9000, 512),
    (0x1000, True): (0x1000, 0),
    (0x00CC, True): (0xD000, 8192),
}

move_table_bot_right = {}
move_table_top_left = {}


def reverse_tiles(tiles):
    """ Reverses tiles in a 16-bit row """
    new_tiles = 0
    for i in range(0, 4):
        new_tiles <<= 4
        new_tiles += tiles & 0b1111
        tiles >>= 4
    return new_tiles


def smart_mini_shift(tiles, reverse=False):
    """ Shift one row or column according to 2048 rules """
    if reverse:
        tiles = reverse_tiles(tiles)
    points = 0
    merged_spots = []
    curr_mask = 0b1111
    for i in range(0, 3):
        curr_mask <<= 4
        curr_tile = tiles & curr_mask
        if curr_tile != 0:
            new_spot = curr_mask >> 4
            slides = 4
            # Slide over to find next action point
            while tiles & new_spot == 0 and (new_spot >> 4) != 0:
                new_spot >>= 4
                slides += 4
            # print(bin(tiles), "new spot", bin(new_spot), "curr", bin(curr_mask), "slides", slides)
            # Check for merging values
            if (curr_tile >> slides) == (tiles & new_spot) \
               and new_spot not in merged_spots:
                # Increment value
                val = tiles & new_spot
                count = 0
                while val >> 4 != 0:
                    val >>= 4
                    count += 4
                val += 1
                points += 2**val
                val <<= count
                tiles &= ~curr_mask
                tiles &= ~new_spot
                tiles |= val
                merged_spots.append(new_spot)
            else:
                if tiles & new_spot != 0:
                    new_spot <<= 4
                    slides -= 4
                if slides > 0:
                    # If found a new empty spot, swap tiles
                    curr_tile >>= slides
                    tiles |= curr_tile
                    tiles &= ~curr_mask
    if reverse:
        tiles = reverse_tiles(tiles)

    monotonicity_left = 0
    monotonicity_right = 0
    temp_tiles = tiles
    for _ in range(0, 3):
        curr_tile = (temp_tiles & 0x000F)
        next_tile = (temp_tiles & 0x00F0) >> 4
        if (next_tile > curr_tile):
            monotonicity_left += curr_tile**MONOTONICITY_POWER - next_tile**MONOTONICITY_POWER
        else:
            monotonicity_right += next_tile**MONOTONICITY_POWER - curr_tile**MONOTONICITY_POWER
        temp_tiles >>= 4

    return (tiles, points, max(monotonicity_left, monotonicity_right))


def build_move_table(tiles=0, depth=0):
    """ Recursively compute all possible moves for one tile line """
    if depth >= 4:
        tiles >>= 4
        move_table_bot_right[tiles] = smart_mini_shift(tiles)
        move_table_top_left[tiles] = smart_mini_shift(tiles, True)
        return
    for j in range(0, MOVE_TABLE_DEPTH+1):
        new_tiles = tiles
        new_tiles += j
        new_tiles <<= 4
        build_move_table(new_tiles, depth+1)


def test_moves():
    fails = 0
    for tiles, expected in MOVE_TESTS.items():
        answer = smart_mini_shift(tiles[0], tiles[1])
        if answer != expected:
            print("Failure: input("+hex(tiles[0])+", "+str(tiles[1])+") output("
                  + hex(answer[0])+", "+str(answer[1])+")")
            print("Expected:", hex(expected[0]), expected[1])
            fails += 1
    if fails == 0:
        print("Movement Table Test Passed!")
    else:
        print("Fail Count:", fails)


def encode_board(board):
    """ Encode the 2D board list to a 64-bit integer """
    new_board = 0
    for row in board.board:
        for tile in row:
            new_board <<= 4
            if tile is not None:
                new_board += tile.val
    return new_board


def smart_shift(board, direction):
    orig_board = board
    points = 0
    monotonicity = 0
    if direction is 'w' or direction is 's':
        for col in range(0, 4):
            board_col = 0
            c_mask = 0xF000 >> (col << 2)
            temp_board = board
            for i in range(0, 4):
                board_col |= ((temp_board & c_mask) >> ((3-col) << 2)) << (i << 2)
                temp_board >>= 16
            if direction is 'w':
                new_tiles, new_points, new_mon = move_table_top_left[board_col]
            else:
                new_tiles, new_points, new_mon = move_table_bot_right[board_col]
            points += new_points
            monotonicity += new_mon

            # Clear and update column in board
            board &= ~(COL_MASK >> (col << 2))
            col_tiles = 0
            new_tiles = reverse_tiles(new_tiles)
            for _ in range(0, 4):
                col_tiles <<= 16
                col_tiles += new_tiles & 0x000F
                new_tiles >>= 4
            board |= (col_tiles << ((3-col) << 2))
    elif direction is 'a' or direction is 'd':
        for row in range(0, 4):
            r_mask = ROW_MASK >> (row << 4)
            offset_from_right = ((3-row) << 4)
            board_row = (board & r_mask) >> offset_from_right
            if direction is 'a':
                new_tiles, new_points, new_mon = move_table_top_left[board_row]
            else:
                new_tiles, new_points, new_mon = move_table_bot_right[board_row]
            points += points
            monotonicity += new_mon

            # Clear and update row in board
            board &= ~r_mask
            board |= new_tiles << offset_from_right
    return (board, orig_board != board, points, monotonicity)


def static_score(board):
    empty_tiles = 0
    sum_tiles = 0
    edge_points = 0
    smooth_points = 0

    for row in range(0, 4):
        for col in range(0, 4):
            tile = (board & (FIRST_MASK >> ((col << 2)+(row << 4)))) >> (((3-col) << 2)+((3-row) << 4))

            if tile == 0:
                empty_tiles += 1
            else:
                sum_tiles += SUM_POWER**tile
                # 8 point for edge tiles and 16 for corners
                if row is 0 or row is 3:
                    edge_points += 1 * (tile / MOVE_TABLE_DEPTH)
                if col is 0 or col is 3:
                    edge_points += 1 * (tile / MOVE_TABLE_DEPTH)

                # Up to 48 points for smoothness
                if col > 0 and board & (FIRST_MASK >> (((col-1) << 2)+(row << 4))) == (tile << 4):
                    smooth_points += 1
                if col < 3 and board & (FIRST_MASK >> (((col+1) << 2)+(row << 4))) == (tile >> 4):
                    smooth_points += 1
                if row > 0 and board & (FIRST_MASK >> ((col << 2)+((row-1) << 4))) == (tile << 16):
                    smooth_points += 1
                if row < 3 and board & (FIRST_MASK >> ((col << 2)+((row+1) << 4))) == (tile >> 16):
                    smooth_points += 1

    return (empty_tiles*EMPTY_WEIGHT) + (sum_tiles*SUM_WEIGHT) + (edge_points * EDGE_WEIGHT) + \
           (smooth_points * SMOOTHNESS_WEIGHT) + (check_loss(board)*LOSS_PENALTY)


def helper(board, depth):
    if depth >= MAX_DEPTH:
        return 0

    tree_score = 0
    for move_dir in 'awsd':
        b = board

        b, moved, points, monotonicity = smart_shift(b, move_dir)
        if not moved:
            continue
        b, full_board = spawn_tile(b)

        tree_score += helper(b, depth+1) * ((MAX_DEPTH + 1 - depth) / MAX_DEPTH)
    return tree_score + static_score(board) - monotonicity * MONOTONICITY_WEIGHT


def check_loss(board):
    for row in range(0, 4):
        for col in range(0, 4):
            tile = board & (FIRST_MASK >> ((col << 2)+(row << 4)))

            if tile == 0 or \
               col > 0 and board & (FIRST_MASK >> (((col-1) << 2)+(row << 4))) == (tile << 4) or \
               col < 3 and board & (FIRST_MASK >> (((col+1) << 2)+(row << 4))) == (tile >> 4) or \
               row > 0 and board & (FIRST_MASK >> ((col << 2)+((row-1) << 4))) == (tile << 16) or \
               row < 3 and board & (FIRST_MASK >> ((col << 2)+((row+1) << 4))) == (tile >> 16):
                return False
    return True


def smoothness(board):
    s = 0
    for row in range(0, 4):
        for col in range(0, 4):
            tile = board & (FIRST_MASK >> ((col << 2)+(row << 4)))

            if tile != 0:
                if col > 0 and board & (FIRST_MASK >> (((col-1) << 2)+(row << 4))) == (tile << 4):
                    s += 1
                if col < 3 and board & (FIRST_MASK >> (((col+1) << 2)+(row << 4))) == (tile >> 4):
                    s += 1
                if row > 0 and board & (FIRST_MASK >> ((col << 2)+((row-1) << 4))) == (tile << 16):
                    s += 1
                if row < 3 and board & (FIRST_MASK >> ((col << 2)+((row+1) << 4))) == (tile >> 16):
                    s += 1
    return s


def get_empty_spots(board):
    empty_spots = []
    for row in range(0, 4):
        for col in range(0, 4):
            if board & FIRST_MASK == 0:
                empty_spots.append((row, col))
            board <<= 4
    return empty_spots


def spawn_tile(board):
    empty_spots = get_empty_spots(board)
    if len(empty_spots) is 0:
        return (board, False)

    spot = random.choice(empty_spots)
    board &= ~(FIRST_MASK >> ((spot[0] << 4)+(spot[1] << 2)))
    if random.random() < 0.90:
        board |= (TWO_MASK >> ((spot[0] << 4)+(spot[1] << 2)))
    else:
        board |= (FOUR_MASK >> ((spot[0] << 4)+(spot[1] << 2)))
    return (board, True)


def show(board):
    for row in range(0, 4):
        for col in range(0, 4):
            print((board & FIRST_MASK) >> (64-4), end=" ")
            board <<= 4
        print()


def smart_move(dt):
    best_score = -sys.maxsize - 1
    best_move = 'a'
    enc_board = encode_board(board)
    for move_dir in 'awsd':
        b, moved, points, monotonicity = smart_shift(enc_board, move_dir)
        print(monotonicity)
        if not moved:
            continue
        b, full_board = spawn_tile(b)

        test_score = helper(b, 0)
        if test_score > best_score:
            best_score = test_score
            best_move = move_dir
    # print("best move:", best_move)
    board.shift(best_move)
    board.computer_move()


def start(graphic=True):
    global board
    board = Board(graphic)
    board.spawn_tile()
    board.spawn_tile()

    if graphic:
        # for _ in range(0, 20):
        #     smart_move(0)
        pyglet.clock.schedule_interval(smart_move, 1/120)
        pyglet.app.run()
    else:
        for i in range(0, 100):
            print(i)
            smart_move(0)
            if board.lost:
                break
        board.show()
        print("Score:", board.score)

build_move_table()
# test_moves()

# board = Board(False)
# board.spawn_tile()
# board.spawn_tile()
# # import cProfile as profile
# # def test():
# #     for _ in range(0, 400):
# #         smart_shift(board, smart_move(0))
# # profile.runctx("test()", globals(), locals())
start()

""" NOTES: monotonacity is only working in the direction you are moving (need the best of up/down and right/left, not just best of up/down OR right/left)