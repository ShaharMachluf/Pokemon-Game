import unittest

from algo import Ash


EPS = 0.0001

class AshTest(unittest.TestCase):
    def set_up(self):
        self.a = Ash('127.0.0.1', 6666)

    def test_start_game(self):
        assert False

    def test_find_pokemons(self):
        assert False

    def test_find_edge(self):
        assert False

    def test_distance(self):
        src = (2, 0)
        dest = (0, 2)
        d = 2.82842
        dest = Ash.distance(src, dest)
        self.assertTrue(dest - d < EPS)
