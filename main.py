import sys
import time
from threading import Thread

from GUI import Graphics
from GUI.GraphicsConfig import DefaultConfig
from algo import Ash


def main():
    args = sys.argv[1:]
    wait = False
    if len(args) < 2:
        print("Client is about to start playing...")

        host = '127.0.0.1'
        port = 6666
    else:
        host = args[0]
        port = int(args[1])
        wait = len(args) > 2

    try:
        player = Ash(host, port)
        if wait:
            print("Waiting 3 seconds for the server to start..")
            time.sleep(3)
        print("Starting new game..")
        player.start_game()
        graphics = Graphics.Graphics(player, DefaultConfig)
        graphics.display()
        print("Game Over")
    except (ConnectionRefusedError, ConnectionResetError, ConnectionAbortedError):
        print("Please make sure you're connected to the internet and the server is up.")
        exit(-1)


if __name__ == "__main__":
    main()
