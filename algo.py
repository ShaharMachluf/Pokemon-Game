import math
import random
import time
from json import JSONDecodeError
from threading import Thread

import networkx as nx

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
        self.running = False
        self.time_left = 0

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
        self.running = True
        Thread(target=self.pokemon_handler).start()

    def pokemon_handler(self):  # main function of the game
        self.client.start()
        try:
            while self.client.is_running() == 'true':
                self.time_left = self.client.time_to_end()
                self.info = JsonParser.get_game_info(self.client.get_info())
                flag = self.next_edge()  # for all the agents that are on nodes
                if flag is True:
                    self.update_agents()
                flag = self.catch_pokemon()  # for all the agents that are on edges
                if flag is not True:  # None or False
                    self.update_agents()
                if flag is True:
                    self.allocate_pokemons()
        except(TypeError, JSONDecodeError, ConnectionResetError, BrokenPipeError):
            pass
        try:
            self.client.stop()
        except(ConnectionResetError, BrokenPipeError):
            pass
        self.running = False
        print(self.info)
        exit()

    def next_edge(self):
        flag = False
        for a in self.agents.values():
            self.agents_dict[a["id"]].change_path(self.g)
            # if the agent needs to move to the next node
            if a["dest"] == -1 and len(self.agents_dict[a["id"]].path) > 1:
                curr = self.agents_dict[a["id"]]
                self.client.choose_next_edge(
                    '{"agent_id":' + str(curr.id) + ', "next_node_id":' + str(curr.path[1]) + '}')
                curr.path.pop(0)
                flag = True
        return flag

    def update_agents(self):  # update agent_dict according to the current state of the agents
        self.agents = JsonParser.get_agents(self.client.get_agents())
        for i in range(len(self.agents)):
            self.agents_dict[i] = Agent.get_updated(self.agents[i], self.agents_dict[i])

    def catch_pokemon(self):
        flag = False
        for a in self.agents_dict.values():
            src = a.src
            dest = a.dest
            if len(a.allocated) > 0 and a.allocated[0] == (src, dest):  # the agent is on an edge with a pokemon
                while self.agents[a.id]["src"] != dest:
                    self.client.move()
                    self.agents = JsonParser.get_agents(self.client.get_agents())
                    time.sleep(0.07)
                flag = True
                a.allocated.pop(0)

                # # check if the agent caught more then one pokemon in order to remove the allocation
                for edge in a.allocated:
                    if edge == (a.src, a.dest):  # the current edge
                        a.allocated.remove(edge)
                        a.path_cost -= (nx.shortest_path_length(self.g, src, dest, weight='weight'))/a.speed
        if flag is False:
            # We moved all agents from edges with pokemons, all edges either have no dest or need to pass empty edges
            # agents that are just passing on empty edges.
            for a in self.agents_dict.values():
                flag = self.passing_agent(a)
        return flag

    def passing_agent(self, agent):
        if agent.dest == -1:  # agent is not set to be moved
            return False
        time.sleep(self.time_to_move(agent))
        self.client.move()

    def time_to_move(self, agent):
        # est. time to move from node to node with weight as comp. parameter.
        dist_left = Ash.distance(agent.pos, self.g.nodes[agent.dest]['pos'])
        total_dist = Ash.distance(self.g.nodes[agent.src]['pos'], self.g.nodes[agent.dest]['pos'])
        weight = self.g.get_edge_data(agent.src, agent.dest)['weight']
        return (weight * (dist_left / total_dist)) / agent.speed

    def allocate_pokemons(self):
        self.pokemons = JsonParser.get_pokemons(self.client.get_pokemons())
        positions = self.find_pokemons()
        for pos in positions:
            min_agent = self.agents_dict[0]
            if any(pos in a1.allocated for a1 in self.agents_dict.values()):
                continue
            min_dist = float("inf")
            min_path = []
            for a in self.agents_dict.values():  # if pokemon not allocated already, allocate it
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
