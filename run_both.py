import time
from threading import Thread
import os

PYTHON = 'python3'
SCRIPT = "./main.py"
SERVER = './Ex4_Server_v0.0.jar'
ip, port = ("127.0.0.1", 6666)

case = '0'


server = " ".join(["Java", "-jar", SERVER, str(case)])
client = " ".join([PYTHON, SCRIPT, ip, str(port), 'sleep'])
os.system(server + " & " + client)

# a = Popen(["Java", "-jar", SERVER, CASE], stdin=PIPE, stderr=PIPE, stdout=PIPE)
# b = Popen([PYTHON, SCRIPT], stdin=PIPE, stderr=PIPE, stdout=PIPE)
