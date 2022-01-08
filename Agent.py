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

    def add(self, poke_pos, sp, sum):  # poke_pos = (src, dest) node id tuple, sp is shortest path as returned
        self.allocated.append(poke_pos)
        self.path_cost += sum

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
        return sum/self.speed, sp + [poke_pos[1]]

    def change_path(self, graph):  # path to nearest pokemon
        if len(self.allocated) > 0:
            min_dist = float("inf")
            min_index = 0
            for i in range(len(self.allocated)):
                spl = nx.shortest_path_length(graph, self.src, self.allocated[i][0], weight='weight')
                if spl < min_dist:
                    min_index = i
                    min_dist = spl
            if min_index != 0:
                self.swap(0, min_index)
            self.path = nx.shortest_path(graph, self.src, self.allocated[0][0], weight='weight')
            self.path.append(self.allocated[0][1])

    def swap(self, i, j):
        temp = self.allocated[i]
        self.allocated[i] = self.allocated[j]
        self.allocated[j] = temp