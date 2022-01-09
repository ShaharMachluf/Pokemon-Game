from setuptools import setup

APP = ["main.py"]
DATA_FILES = ['GUI/media/Pikachu Down.png', 'GUI/media/Pikachu Up.png', 'GUI/media/Pokeball.png']
OPTIONS = {
    'argv_emulation': True,
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requirements=['py2app', 'networkx', 'pygame']
)
