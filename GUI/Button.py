import pygame


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