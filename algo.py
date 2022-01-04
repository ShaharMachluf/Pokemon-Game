from GameServerParser import JsonParser
import networkx as nx
from client import Client

class Ash:
    def __init__(self, host, port):
        self.client = Client()
        self.client.start_connection(host, port)
        self.pokemons = JsonParser.get_pokemons(self.client.get_pokemons())
        self.g = JsonParser.load_graph(self.client.get_graph())
        self.agents = JsonParser.get_agents(self.client.get_agents())
        self.info = JsonParser.get_game_info(self.client.get_info())


    def start_game(self):
        pass


a = Ash("127.0.0.1", 6666)


