class DefaultConfig:
    # Simple class to configure the graph settings
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

    FONT_NAME = 'Arial'
    FONT_SIZE = 20
    FONT_IS_BOLD = True
    AGENT_IMG = './GUI/media/Pokeball.png'
    agent_size = 30
    POKE_UP_IMG = './GUI/media/Pikachu Up.png'
    POKE_DOWN_IMG = './GUI/media/Pikachu Down.png'
    poke_width = 70
    poke_height = 50

    node_normal = BLUE
    node_selected = GREEN
    path_normal = BLACK
    path_selected = RED
    bg_color = WHITE
    arrow_angle = 65  # What angle will be the arrow head line compare to the line it's on
    arrow_pos = 0.7  # the arrow head will start at .. of the distance from src to dest
    arrow_scale = 16  # arrow len will be divided by..
    radius_dens = 10  # so radius = (screen_area / (n_of_edges + 1)) / radius_dens