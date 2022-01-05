import unittest

from algo import Ash
EPS = 0.0001


class AshTest(unittest.TestCase):  # test relevent to case 0

    def test_find_pokemons(self):
        a = Ash('127.0.0.1', 6666)
        exp = [(9, 8)]
        ans = a.find_pokemons()
        self.assertEqual(exp, ans)

    def test_find_edge(self):
        a = Ash('127.0.0.1', 6666)
        exp = (9, 8)
        pos = a.pokemons[0]["pos"]
        type_ = a.pokemons[0]["type"]
        ans = a.find_edge(pos, type_)
        self.assertEqual(exp, ans)


    def test_distance(self):
        src = (2, 0)
        dest = (0, 2)
        d = 2.82842
        dest = Ash.distance(src, dest)
        self.assertTrue(dest - d < EPS)
