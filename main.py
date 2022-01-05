import sys
import time

from algo import Ash


def main():
    args = sys.argv[1:]
    print("GAME IS ABOUT TO START... SLEEPING FOR 3 SEC")
    time.sleep(3)
    print("GAME WILL NOW BEGIN")
    if len(args) < 2:
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
