import json

import networkx as nx


class JsonParser:
    @staticmethod
    def load_graph(s):
        p = json.loads(s)
        g = nx.DiGraph()
        for n in [JsonParser.__parse_pos(x) for x in p["Nodes"]]:
            g.add_node(n['id'], pos=n['pos'])
        for x in p["Edges"]:
            g.add_edge(x['src'], x['dest'], weight=x['w'])
        return g

    @staticmethod
    def __parse_pos(d):  # Dictionary that contains pos as string, converted to tuple.
        d['pos'] = tuple([float(x) for x in d['pos'].split(',')][:2])
        return d

    @staticmethod
    def get_agents(s):
        return {x['Agent']['id']: JsonParser.__parse_pos(x["Agent"]) for x in json.loads(s)["Agents"]}

    @staticmethod
    def get_game_info(s):
        return json.loads(s)["GameServer"]

    @staticmethod
    def get_pokemons(s):
        return [JsonParser.__parse_pos(x["Pokemon"]) for x in json.loads(s)["Pokemons"]]