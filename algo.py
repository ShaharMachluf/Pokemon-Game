import math
import random

import GameGraphics
from Agent import Agent
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
        self.agents_dict = {}
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
        i = 0
        for a in self.agents.values():
            self.agents_dict[a["id"]] = Agent(a["id"], a["value"], a["src"], a["dest"], a["speed"], a["pos"])
            if i + 1 >= len(positions):
                pos = positions[i]
                self.agents_dict[a["id"]].add(pos, list(pos), self.g.get_edge_data(pos[0], pos[1])['weight'])
            else:
                self.agents_dict[a["id"]].path.append(a["src"])
            i += 1
        self.graphics = GameGraphics.Graphics(self, GameGraphics.GraphicsConfig())

    def pokemon_handler(self):  # main function of the game
        self.client.start()
        while True:
            flag = 0
            for a in self.agents.values():
                if a["dest"] == -1 and len(self.agents_dict[a["id"]].path) > 1:
                    curr = self.agents_dict[a["id"]]
                    self.client.choose_next_edge('{"agent_id":' + str(curr.id) + ', "next_node_id":' + str(curr.path[1]) + '}')
                    curr.path.pop(0)
                    flag = 1
            if flag == 1:
                self.client.move()
                print(JsonParser.get_agents(self.client.get_agents()))


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
