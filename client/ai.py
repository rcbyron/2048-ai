import random
import sys

# Board masks
COL_MASK = 0xF000F000F000F000
ROW_MASK = 0xFFFF000000000000
FIRST_MASK = 0xF000000000000000
TWO_MASK = 0x2000000000000000
FOUR_MASK = 0x4000000000000000
# Tuning parameters and weights
MAX_DEPTH = 4
SMOOTHNESS_WEIGHT = 700
# EDGE_WEIGHT = 30
LOSS_PENALTY = -20000
MONOTONICITY_POWER = 4.0
MONOTONICITY_WEIGHT = 47.0
SUM_POWER = 3.5
SUM_WEIGHT = 11.0
EMPTY_WEIGHT = 270.0

MOVE_TABLE_DEPTH = 14

move_table_bot_right = {}
move_table_top_left = {}
mono_table = {}


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

    return (tiles, points)


def mini_mono(tiles):
    monotonicity_left = 0
    monotonicity_right = 0
    for _ in range(0, 3):
        curr_tile = (tiles & 0x000F)
        next_tile = (tiles & 0x00F0) >> 4
        if (next_tile > curr_tile):
            monotonicity_left += next_tile**MONOTONICITY_POWER - curr_tile**MONOTONICITY_POWER
        else:
            monotonicity_right += curr_tile**MONOTONICITY_POWER - next_tile**MONOTONICITY_POWER
        tiles >>= 4
    return min(monotonicity_left, monotonicity_right)


def build_tables(tiles=0, depth=0):
    """ Recursively compute all possible moves for one tile line """
    if depth >= 4:
        tiles >>= 4
        move_table_bot_right[tiles] = smart_mini_shift(tiles)
        move_table_top_left[tiles] = smart_mini_shift(tiles, True)
        mono_table[tiles] = mini_mono(tiles)
        return
    for j in range(0, MOVE_TABLE_DEPTH+1):
        new_tiles = tiles
        new_tiles += j
        new_tiles <<= 4
        build_tables(new_tiles, depth+1)


def encode_board(board):
    """ Encode the 2D board list to a 64-bit integer """
    new_board = 0
    for row in board.board:
        for tile in row:
            new_board <<= 4
            if tile is not None:
                new_board += tile.val
    return new_board


def get_row(board, num):
    r_mask = ROW_MASK >> (num << 4)
    offset_from_right = ((3-num) << 4)
    return (board & r_mask) >> offset_from_right


def get_col(board, num):
    board_col = 0
    c_mask = 0xF000 >> (num << 2)
    for i in range(0, 4):
        board_col |= ((board & c_mask) >> ((3-num) << 2)) << (i << 2)
        board >>= 16
    return board_col


def smart_shift(board, direction):
    orig_board = board
    points = 0
    if direction is 'w' or direction is 's':
        for col in range(0, 4):
            board_col = get_col(board, col)
            if direction is 'w':
                new_tiles, new_points = move_table_top_left[board_col]
            else:
                new_tiles, new_points = move_table_bot_right[board_col]
            points += new_points

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
                new_tiles, new_points = move_table_top_left[board_row]
            else:
                new_tiles, new_points = move_table_bot_right[board_row]
            points += points

            # Clear and update row in board
            board &= ~r_mask
            board |= new_tiles << offset_from_right
    return (board, orig_board != board, points)


def static_score(board):
    empty_tiles = 0
    sum_tiles = 0
    edge_points = 0
    smooth_points = 0
    mono_points = monotonicity(board)

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
    return (empty_tiles*EMPTY_WEIGHT) - (mono_points * MONOTONICITY_WEIGHT) + \
           (check_loss(board)*LOSS_PENALTY) + (sum_tiles*SUM_WEIGHT) + (smooth_points * SMOOTHNESS_WEIGHT)
    # return (empty_tiles*EMPTY_WEIGHT) + (sum_tiles*SUM_WEIGHT) + (edge_points * EDGE_WEIGHT) + \
    #        (smooth_points * SMOOTHNESS_WEIGHT) - (mono_points * MONOTONICITY_WEIGHT) + \
    #        (check_loss(board)*LOSS_PENALTY)


def check_loss(board):
    """ Checks if board has lost the game or not """
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


def monotonicity(board):
    """ Returns current monotonicity """
    monotonicity = 0
    for i in range(0, 4):
        monotonicity += mono_table[get_row(board, i)] + mono_table[get_col(board, i)]
    return monotonicity


def get_empty_spots(board):
    """ Returns an array of the empty board spots """
    empty_spots = []
    for row in range(0, 4):
        for col in range(0, 4):
            if board & FIRST_MASK == 0:
                empty_spots.append((row, col))
            board <<= 4
    return empty_spots


def spawn_tile(board):
    """ Attempts to spawn a tile on the board """
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


def show(board, show_best_tile=False):
    """ Prints the board """
    best_tile = 0
    for row in range(0, 4):
        for col in range(0, 4):
            tile = (board & FIRST_MASK) >> (64-4)
            if tile > best_tile:
                best_tile = tile
            print(tile, end=" ")
            board <<= 4
        print()
    if show_best_tile:
        print("Best Tile:", 2**best_tile)


def helper(board, depth):
    if depth >= MAX_DEPTH:
        return 0

    tree_score = 0
    for move_dir in 'awsd':
        b, moved, points = smart_shift(board, move_dir)
        if not moved:
            continue
        b, success = spawn_tile(b)

        tree_score += helper(b, depth+1) * ((MAX_DEPTH + 1 - depth) / MAX_DEPTH)

    return tree_score + static_score(board)


def get_best_move(board):
    best_score = -sys.maxsize - 1
    best_move = 'a'
    for move_dir in 'awsd':
        b, moved, points = smart_shift(board, move_dir)
        if not moved:
            continue
        b, success = spawn_tile(b)

        test_score = helper(b, 0)
        if test_score > best_score:
            best_score = test_score
            best_move = move_dir
    return best_move


def smart_move(dt):
    enc_board = encode_board(actual_board)
    actual_board.shift(get_best_move(enc_board))
    actual_board.computer_move()


def simulate():
    """ Simulates a single game using AI to make moves """
    score = 0
    b, success = spawn_tile(0x000000000000000)
    b, success = spawn_tile(b)
    for i in range(0, 10000):
        b, moved, points = smart_shift(b, get_best_move(b))
        score += points
        b, success = spawn_tile(b)
        if not success or not moved:
            break
        if i > 9998:
            print("Move limit reached! Yay?")
            break
    return (b, score, i)

build_tables()


def set_board(board):
    global actual_board
    actual_board = board
