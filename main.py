import sys
import time

import Agent
from algo import Ash


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print("Client is about to start playing...\nWaiting 3 seconds to let the server start.")
        time.sleep(3)
        print("GAME WILL NOW BEGIN")

        host = '127.0.0.1'
        port = 6666
    else:
        host = args[0]
        port = int(args[1])

    player = Ash(host, port)
    if player:
        print("Game completed")



if __name__ == "__main__":
    main()
