import math
import random
import sys

import pygame

from networkx import DiGraph, get_node_attributes

import Agent


class Padding:
    # Simple graph to save padding data and working area screen
    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def get_width(self, width):
        return width - (self.left + self.right)

    def get_height(self, height):
        return height - (self.top + self.bottom)

    def get_top(self):
        return self.top

    def get_right(self):
        return self.right


class GraphicsConfig:
    # Simple class to configure the graph settings
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

    FONT_NAME = 'Arial'
    FONT_SIZE = 20
    FONT_IS_BOLD = True
    AGENT_IMG = './Pokeball.png'
    POKE_UP_IMG = './Pikachu Up.jpg'
    POKE_DOWN_IMG = './Pikachu Down.png'

    node_normal = BLUE
    node_selected = GREEN
    path_normal = BLACK
    path_selected = RED
    bg_color = WHITE
    arrow_angle = 65  # What angle will be the arrow head line compare to the line it's on
    arrow_pos = 0.7  # the arrow head will start at .. of the distance from src to dest
    arrow_scale = 16  # arrow len will be divided by..
    radius_dens = 10  # so radius = (screen_area / (n_of_edges + 1)) / radius_dens


class Button:
    def __init__(self, pos, text, t_color, bg_color, f_size, call_on_click):
        self.pos = pos
        self.render = pygame.font.SysFont("Arial", f_size).render(text, True, t_color)
        self.surface = pygame.Surface(self.render.get_size())
        self.surface.fill(bg_color)
        self.surface.blit(self.render, (0, 0))  # pos relative to the surface
        self.call_on_click = call_on_click[0]
        if self.call_on_click and len(call_on_click) > 1:
            self.call_on_click_args = call_on_click[1:]
        else:
            self.call_on_click_args = None
        self.rect = pygame.Rect(self.pos[0], self.pos[1],
                                self.render.get_size()[0], self.render.get_size()[1])

    def show(self, screen):
        screen.blit(self.surface, self.pos)

    def click_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] and self.rect.collidepoint(*pygame.mouse.get_pos()):
            if self.call_on_click is not None:
                self.call_on_click(*self.call_on_click_args) if self.call_on_click_args is not None else self.call_on_click()


class Graphics:
    DEFAULT_SIZE = 500
    DEFAULT_PADDING = Padding(40, 60, 40, 40)

    def __init__(self, player, config, padding: Padding = None):
        pygame.init()
        self.player = player

        self.ui_event = pygame.USEREVENT + 1

        # Screen size & settings
        self.w = self.DEFAULT_SIZE
        self.h = self.DEFAULT_SIZE

        self.set_working_area()
        self.screen = pygame.display.set_mode((self.w, self.h), pygame.RESIZABLE)
        pygame.display.set_caption("Graph")

        self.clock = pygame.time.Clock()

        # Graph variables:
        self.graph = player.g if player.g is not None else DiGraph()
        self.padding = padding if padding is not None else self.DEFAULT_PADDING
        self.config = config
        self.font = pygame.font.SysFont(self.config.FONT_NAME, self.config.FONT_SIZE,
                                          bold=self.config.FONT_IS_BOLD)

        self.agent_img = pygame.image.load(self.config.AGENT_IMG)
        self.poke_up_img = pygame.image.load(self.config.POKE_UP_IMG)
        self.poke_down_img = pygame.image.load(self.config.POKE_DOWN_IMG)

        self.no_pos = {}
        self.selected_nodes = []
        self.selected_edges = []
        # Just random start point to create vars
        self.minX, self.minY, self.maxX, self.maxY = 0, 0, 0, 0
        self.xD, self.xS, self.yD, self.yS = 1, 1, 1, 1
        self.xButton = Button((0, 0), " Stop Game", self.config.WHITE, self.config.RED, 20, [self.close_clicked])
        pygame.event.post(pygame.event.Event(self.ui_event, message="UI Created"))

    def close_clicked(self):
        self.player.client.stop()
        self.player.client.stop_connection()
        exit(0)

    def set_special_by_path(self, path):
        if len(path) == 0:
            return
        elif len(path) == 1:
            self.selected_nodes = [path[0]]
        self.selected_nodes = []
        for prev, current in zip(path, path[1:]):
            self.selected_nodes.append(prev)
            self.selected_edges.append((prev, current))

    def scale_as_window(self):
        self.minX = 0
        self.minY = 0
        self.xD = self.padding.get_width(self.w)
        self.yD = self.padding.get_height(self.h)
        self.xS = 1
        self.yS = 1

    def scale_by_nodes(self):
        self.minX = sys.maxsize
        self.minY = sys.maxsize
        self.maxX = -sys.maxsize
        self.maxY = -sys.maxsize

        for n in self.graph.nodes:
            x, y = self.get_pos((n, self.graph.nodes[n]))[:2]
            self.minX = min(self.minX, x)
            self.minY = min(self.minY, y)
            self.maxX = max(self.maxX, x)
            self.maxY = max(self.maxY, y)

        if self.minX == self.maxX and self.minY == self.maxY:
            if self.maxX == 0:
                self.maxX = self.padding.get_width(self.w)
            if self.maxY == 0:
                self.maxY = self.padding.get_height(self.h)
            self.minY = 0
            self.minX = 0

        self.xD = abs(self.maxX - self.minX)
        self.yD = abs(self.maxY - self.minY)
        self.set_scale()

    def set_scale(self):
        w = self.padding.get_width(self.w)
        h = self.padding.get_height(self.h)
        self.xS = w / self.xD
        self.yS = h / self.yD

    def set_working_area(self):
        di = pygame.display.Info()  # display info
        self.w = di.current_w
        self.h = di.current_h

    def display(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit(0)
                elif event.type == pygame.WINDOWSIZECHANGED:
                    # We re-render on window size changed
                    self.w = self.screen.get_width()
                    self.h = self.screen.get_height()
                else:
                    self.xButton.click_event(event)
            self.screen.fill(self.config.bg_color)
            self.draw_all()
            pygame.display.update()
            self.clock.tick(30)

    def get_pos(self, node):
        if node[1]['pos'] is None or node[1]['pos'] == ():
            if node[0] not in self.no_pos:
                self.no_pos[node[0]] = (random.uniform(0, self.padding.get_width(self.w)),
                                        random.uniform(0, self.padding.get_height(self.h)))
            return self.no_pos[node[0]]
        else:
            return node[1]['pos']

    def get_all_positioned(self):
        for n in self.graph.nodes:
            yield self.get_positioned((n, self.graph.nodes[n]))

    def get_agents_positioned(self):
        for a in self.player.agents.values():
            yield self.get_positioned(a, 'agent')

    def get_poke_positioned(self):
        for p in self.player.pokemons:
            yield self.get_positioned(p, 'pokemons')

    def get_positioned(self, element, elem_type='node'):
        if elem_type == 'node':
            x, y = self.get_pos(element)  # element is node
            id_ = element[0]
        elif elem_type == 'agent':  # Element is agent
            x, y = element['pos'][0], element['pos'][1]
            id_ = element['id']
        else:  # Pokemon
            x, y = element['pos'][0], element['pos'][1]
            id_ = element['type']  # ID represents type

        x = self.padding.get_right() + ((x - self.minX) * self.xS)
        y = self.padding.get_top() + ((y - self.minY) * self.yS)
        return id_, {'pos': (x, y)}

    def draw_all(self):
        nodes = {}
        if len(self.graph.nodes) == 0:
            self.scale_as_window()
            return
        self.scale_by_nodes()
        # Draw cities (nodes)
        for n in self.get_all_positioned():
            nodes[n[0]] = n
            for e in self.graph.edges(n[0], data=True):
                if e[1] not in nodes:
                    nodes[e[1]] = self.get_positioned((e[1], self.graph.nodes[e[1]]))
                self.draw_edge(n, nodes[e[1]])  # n is e[0] thus we want point to node id e[1]
            self.draw_node(n)
        # Draw agents
        for agent in self.get_agents_positioned():
            self.draw_agent(agent)
        # Draw pokemons
        for poke in self.get_poke_positioned():
            self.draw_poke(poke)
        # Draw stats
        self.draw_stats()
        self.xButton.show(self.screen)

    def draw_stats(self):
        moves = self.player.info["moves"]
        grade = self.player.info["grade"]
        title = "Grade: " + str(grade) + "          " + str("Moves: ") + str(moves)
        rend = self.font.render(title, True, self.config.BLACK)
        rect = rend.get_rect(center=(self.padding.get_width(self.w) / 2,
                                     self.padding.get_top() / 2 - self.config.FONT_SIZE / 2))
        self.screen.blit(rend, rect)

    def draw_node(self, n):
        # The radius of each node is now determined by the density of the graph,
        # added 1 so it won't divide by 0 if none.
        # good ratio too: min(self.w, self.h) / 150
        radius = ((self.w * self.h) / (self.graph.number_of_edges() + 1)) / self.config.radius_dens
        radius = min(radius, 20)
        pygame.draw.circle(self.screen,
                           self.config.node_selected if n[0] in self.selected_nodes else self.config.node_normal,
                           n[1]['pos'], radius)
        # draw the node id
        id_srf = self.font.render(str(n[0]), True, self.config.WHITE)
        rect = id_srf.get_rect(center=(n[1]['pos'][0], n[1]['pos'][1]))
        self.screen.blit(id_srf, rect)

    def draw_agent(self, agent):
        AGENT_SIZE = 30
        self.screen.blit(pygame.transform.scale(self.agent_img, (AGENT_SIZE, AGENT_SIZE)), agent[1]['pos'])
        id_srf = self.font.render(str(agent[0]), True, self.config.BLACK)
        rect = id_srf.get_rect(center=(agent[1]['pos'][0], agent[1]['pos'][1] + AGENT_SIZE + 5))
        self.screen.blit(id_srf, rect)

    def draw_poke(self, poke):
        POKE_SIZE = 50
        if poke[0] > 0:  # UP
            img = self.poke_up_img
        else:  # DOWN
            img = self.poke_down_img
        self.screen.blit(pygame.transform.scale(img, (POKE_SIZE + 20, POKE_SIZE)), poke[1]['pos'])

    def draw_edge(self, n1, n2):
        color = self.config.path_selected if (n1[0], n2[0]) in self.selected_edges else self.config.path_normal
        pygame.draw.line(self.screen, color, n1[1]['pos'], n2[1]['pos'])
        self.draw_arrow_head(n1, n2, color)

    def draw_arrow_head(self, src, dest, color):
        leng = self.distance(src[1]['pos'], dest[1]['pos'])
        if leng == 0:
            return
        arw_len = leng / self.config.arrow_scale
        scale = arw_len / leng
        angle = self.config.arrow_angle
        pos_ratio = self.config.arrow_pos
        src_pos = src[1]['pos']
        dest_pos = dest[1]['pos']
        head = (src_pos[0] + pos_ratio * (dest_pos[0] - src_pos[0]),
                src_pos[1] + pos_ratio * (dest_pos[1] - src_pos[1]))
        d_x = src_pos[0] - head[0]
        d_y = src_pos[1] - head[1]
        sin_a = math.sin(angle)
        cos_a = math.cos(angle)
        g1 = (head[0] - scale * (d_x * cos_a + d_y * sin_a), head[1] - scale * (d_y * cos_a - d_x * sin_a))
        g2 = (head[0] - scale * (d_x * cos_a - d_y * sin_a), head[1] - scale * (d_y * cos_a + d_x * sin_a))
        pygame.draw.line(self.screen, color, g1, head)
        pygame.draw.line(self.screen, color, g2, head)

    def add_node(self, node):
        self.graph.add_node(node.id, pos=node.pos)
        pygame.event.post(pygame.event.Event(self.ui_event, message="Node added"))

    def remove_node(self, node):
        self.graph.remove_node(node.id)
        if node.id in self.selected_nodes:
            self.selected_nodes.remove(node.id)
        pygame.event.post(pygame.event.Event(self.ui_event, message="Node removed"))

    def add_edge(self, n1, n2, weight):
        self.graph.add_edge(n1.id, n2.id, weight=weight)
        pygame.event.post(pygame.event.Event(self.ui_event, message="Edge added"))

    def remove_edge(self, n1, n2):
        self.graph.remove_edge(n1.id, n2.id)
        if (n1, n2) in self.selected_edges:
            self.selected_edges.remove((n1, n2))
        pygame.event.post(pygame.event.Event(self.ui_event, message="Edge removed"))

    @staticmethod
    def distance(src, dest):
        return math.sqrt(math.pow(src[0] - dest[0], 2) + math.pow(src[1] - dest[1], 2))
