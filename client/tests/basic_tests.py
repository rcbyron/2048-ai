""" Runs basic tests on the AI script """

# Import relative client package
import os
from os.path import dirname, abspath
parent_dir = dirname(dirname(dirname(abspath(__file__))))
os.sys.path.insert(0, parent_dir)

from client.ai import smart_mini_shift, build_tables, monotonicity # flake8: noqa

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
MONO_TESTS = {
    0x0001: 1,
    0x1111: 16.0,
    0x5500: 1296.0,
    0x1000: 1,
    0xC0C0: 28561.0,
    0x2030: 81.0,
    0x0001: 1,
    0x1111: 16.0,
    0x0088: 6561.0,
    0x1000: 1,
    0x00CC: 28561.0,
}

def test_moves():
    fails = 0
    for case, expected in MOVE_TESTS.items():
        answer = smart_mini_shift(case[0], case[1])
        if answer != expected:
            print("Failure input:", hex(case[0]), case[1])
            print("Output:", hex(answer[0]), answer[1])
            print("Expected:", hex(expected[0]), expected[1])
            fails += 1
    if fails == 0:
        print("Movement Table Test Passed!")
    else:
        print("Fail Count:", fails)

build_tables()
test_moves()
print(monotonicity(0x1111111111111191))

# board = Board(False)
# board.spawn_tile()
# board.spawn_tile()
# # import cProfile as profile
# # def test():
# #     for _ in range(0, 400):
# #         smart_shift(board, smart_move(0))
# # profile.runctx("test()", globals(), locals())
