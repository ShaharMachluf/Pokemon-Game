import networkx as nx


class Agent:
    def __init__(self, id, value, src, dest, speed, pos):
        self.id = id
        self.value = value
        self.src = src
        self.dest = dest
        self.speed = speed
        self.pos = pos
        self.allocated = []  # Allocated pokemons
        self.path = []
        self.path_cost = 0

    def add(self, poke_pos, sp):  # poke_pos = (src, dest) node id tuple, sp is shortest path as returned
        self.allocated.append(poke_pos)
        if len(self.path) > 0 and sp[0] == self.path[-1]:
            self.path.extend(sp[1:])
        else:
            self.path.extend(sp)

    def target_est(self, graph, poke_pos):
        if not self.path:
            sp = nx.shortest_path(graph, self.src, poke_pos[0], weight='weight')
        else:
            sp = nx.shortest_path(graph, self.path[-1], poke_pos[0], weight='weight')
        if sp is None or len(sp) == 0:
            return -1, None
        sum = 0
        for i in range(0, len(sp) - 1):
            sum += graph.get_edge_data(sp[i], sp[i + 1])['weight']
        return sum, sp + [poke_pos[1]]

    def deploy_next(self):
        pass  # Move to next target
