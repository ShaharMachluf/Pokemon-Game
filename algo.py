import math
import random
from threading import Thread

import GameGraphics
from GameServerParser import JsonParser
from client import Client

EPS = 0.0001


class Ash:
    def __init__(self, host, port):
        self.client = Client()
        self.client.start_connection(host, port)
        self.pokemons = JsonParser.get_pokemons(self.client.get_pokemons())
        self.g = JsonParser.load_graph(self.client.get_graph())
        self.info = JsonParser.get_game_info(self.client.get_info())
        self.agents = None
        self.graphics = None
        self.start_game()

    def start_game(self):
        positions = self.find_pokemons()
        num = self.info["agents"]
        for i in range(0, num):
            if len(positions) <= i + 1:
                id_ = positions[i][0]
                self.client.add_agent('{"id":' + str(id_) + '}')
            else:
                id_ = random.randrange(0, self.g.number_of_nodes() - 1)
                self.client.add_agent('{"id":' + str(id_) + '}')
        self.agents = JsonParser.get_agents(self.client.get_agents())
        self.graphics = GameGraphics.Graphics(self, GameGraphics.GraphicsConfig())
        Thread(target=self.graphics.display).run()
        self.pokemon_handler()

    def pokemon_handler(self):
        pass

    def find_pokemons(self):
        positions = []
        for d in self.pokemons:
            positions.append(self.find_edge(d["pos"], d["type"]))
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
