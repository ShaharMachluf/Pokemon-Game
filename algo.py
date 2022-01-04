from GameServerParser import JsonParser
import networkx as nx
from client import Client

class Ash:
    def __init__(self, host, port):
        self.client = Client()
        self.client.start_connection(host, port)
        self.pokemons = JsonParser.get_pokemons(self.client.get_pokemons())
        self.g = JsonParser.load_graph(self.client.get_graph())
        self.info = JsonParser.get_game_info(self.client.get_info())  # f


    def start_game(self):
        # self.find_pokemon()
        # num = self.info["agents"]
        # for i in range [num]:
        pass

    def find_pokemons(self):
        positions = []
        for d in self.pokemons:
            find_edge(d["pos"])

    def find_edge(self, pos):
        for e in self.g.edges:
            self.g.



a = Ash("127.0.0.1", 6666)
[print(e) for e in a.g.edges(data=True)]
[print(e) for e in a.g.nodes(data=True)]


