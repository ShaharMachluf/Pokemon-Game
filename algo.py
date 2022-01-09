import math
import random
import sys
import time

import networkx as nx

import GameGraphics
from Agent import Agent
from GameServerParser import JsonParser
from client import Client

EPS = 0.00001


class Ash:
    def __init__(self, host, port):
        self.client = Client()
        self.client.start_connection(host, port)
        self.pokemons = JsonParser.get_pokemons(self.client.get_pokemons())
        self.g = JsonParser.load_graph(self.client.get_graph())
        self.info = JsonParser.get_game_info(self.client.get_info())
        self.agents = None
        self.agents_dict = {}  # contain 'Agent' objects
        self.graphics = None
        self.start_game()

    def start_game(self):
        positions = self.find_pokemons()
        num = self.info["agents"]
        for i in range(0, num):  # add agents
            if len(positions) >= i + 1:
                id_ = positions[i][0]
                self.client.add_agent('{"id":' + str(id_) + '}')
            else:
                id_ = random.randrange(0, self.g.number_of_nodes() - 1)
                self.client.add_agent('{"id":' + str(id_) + '}')
        self.agents = JsonParser.get_agents(self.client.get_agents())
        i = 0
        for a in self.agents.values():  # init agent_dict
            self.agents_dict[a["id"]] = Agent(a["id"], a["value"], a["src"], a["dest"], a["speed"], a["pos"])
            if i + 1 <= len(positions):
                pos = positions[i]
                self.agents_dict[a["id"]].add(pos, list(pos), self.g.get_edge_data(pos[0], pos[1])['weight'])
                self.agents_dict[a["id"]].change_path(self.g)
            else:
                self.agents_dict[a["id"]].path.append(a["src"])
            i += 1
        self.graphics = GameGraphics.Graphics(self, GameGraphics.GraphicsConfig())

    def pokemon_handler(self):  # main function of the game
        self.client.start()
        while self.client.is_running() == 'true':
            print(self.client.time_to_end())
            self.info = JsonParser.get_game_info(self.client.get_info())
            flag = self.next_edge()  # for all the agents that are on nodes
            if flag == 1:
                self.update_agents()
            flag = self.catch_pokemon()  # for all the agents that are on edges
            if flag != 0:
                self.update_agents()
            if flag == 1:
                self.allocate_pokemons()
        self.client.stop()
        sys.exit()

    def next_edge(self):
        flag = 0
        for a in self.agents.values():
            self.agents_dict[a["id"]].change_path(self.g)
            if a["dest"] == -1 and len(self.agents_dict[a["id"]].path) > 1:  # if the agent needs to move to the next node
                curr = self.agents_dict[a["id"]]
                self.client.choose_next_edge(
                    '{"agent_id":' + str(curr.id) + ', "next_node_id":' + str(curr.path[1]) + '}')
                curr.path.pop(0)
                flag = 1
        return flag

    def update_agents(self):  # update agent_dict according to the current state of the agents
        self.agents = JsonParser.get_agents(self.client.get_agents())
        for i in range(len(self.agents)):
            a = self.agents_dict[i]
            a.value = self.agents[i]["value"]
            a.src = self.agents[i]["src"]
            a.dest = self.agents[i]["dest"]
            a.speed = self.agents[i]["speed"]
            a.pos = self.agents[i]["pos"]

    def catch_pokemon(self):
        flag = 0
        for a in self.agents_dict.values():
            src = a.src
            dest = a.dest
            if len(a.allocated) > 0 and a.allocated[0] == (src, dest):  # the agent is on an edge with a pokemon
                while self.agents[a.id]["src"] != dest:
                    self.client.move()
                    self.agents = JsonParser.get_agents(self.client.get_agents())
                    time.sleep(0.07)
                flag = 1
                a.allocated.pop(0)
                for i in range(len(a.allocated)):  # check if the agent caught more then one pokemon
                    if a.allocated[i] == (a.src, a.dest):
                        a.allocated.pop(i)
                        a.path_cost -= (nx.shortest_path_length(self.g, src, dest, weight='weight'))/a.speed
        if flag == 0:
            for a in self.agents_dict.values():
                if a.dest != -1:  # the agent is on an edge without pokemon
                    self.client.move()
                    dist_left = Ash.distance(a.pos, self.g.nodes[a.dest]['pos'])
                    total_dist = Ash.distance(self.g.nodes[a.src]['pos'], self.g.nodes[a.dest]['pos'])
                    weight = self.g.get_edge_data(a.src, a.dest)['weight']
                    time_to_move = (weight*(dist_left/total_dist))/a.speed
                    time.sleep(time_to_move)
                    self.client.move()
                    flag = 2
        return flag

    def allocate_pokemons(self):
        self.pokemons = JsonParser.get_pokemons(self.client.get_pokemons())
        positions = self.find_pokemons()
        for pos in positions:
            flag = 0
            min_agent = self.agents_dict[0]
            for a1 in self.agents_dict.values():  # check if pokemon was already allocated
                for al in a1.allocated:
                    if pos == al:
                        flag = 1
                        break
                if flag == 1:
                    break
            if flag == 1:
                continue
            min_dist = float("inf")
            min_path = []
            for a in self.agents_dict.values():
                target = a.target_est(self.g, pos)
                if target[0] < min_dist:
                    min_dist = target[0]
                    min_path = target[1]
                    min_agent = a
            min_agent.add(pos, min_path, min_dist)
            min_agent.change_path(self.g)

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
