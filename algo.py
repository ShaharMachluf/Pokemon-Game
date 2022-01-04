import math

from GameServerParser import JsonParser
import networkx as nx
from client import Client

EPS = 0.0001


class Ash:
    def __init__(self, host, port):
        self.client = Client()
        self.client.start_connection(host, port)
        self.pokemons = JsonParser.get_pokemons(self.client.get_pokemons())
        self.g = JsonParser.load_graph(self.client.get_graph())
        self.info = JsonParser.get_game_info(self.client.get_info())  # f
        self.start_game()

    def start_game(self):
        positions = self.find_pokemons()
        num = self.info["agents"]
        for i in range(0, num):
            id_ = positions[i][0]
            self.client.add_agent('{"id":' + str(id_) + '}')

    def find_pokemons(self):
        positions = []
        for d in self.pokemons:
            positions.append(self.find_edge(d["pos"], d["type"]))
        print(positions)
        return positions

    def find_edge(self, pos, type_):
        for e in self.g.edges:
            src = self.g.nodes[e[0]]["pos"]
            dest = self.g.nodes[e[1]]["pos"]
            if self.distance(src, pos) + self.distance(dest, pos) - self.distance(src, dest) < EPS:
                if (type_ == 1 and e[0] < e[1]) or (type_ == -1 and e[0] > e[1]):
                    return e

    @staticmethod
    def distance(src, dest):
        return math.sqrt(math.pow(src[0] - dest[0], 2) + math.pow(src[1] - dest[1], 2))

a = Ash("127.0.0.1", 6666)
# [print(e) for e in a.g.edges(data=True)]
# [print(e) for e in a.g.nodes(data=True)]


