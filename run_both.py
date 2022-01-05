from threading import Thread
import os

PYTHON = 'python3'
SCRIPT = "./main.py"
SERVER = './Ex4_Server_v0.0.jar'
CASE = '0'

server = " ".join(["Java", "-jar", SERVER, CASE])
client = " ".join([PYTHON, SCRIPT])
os.system(server + " & " + client)
# a = Popen(["Java", "-jar", SERVER, CASE], stdin=PIPE, stderr=PIPE, stdout=PIPE)
# b = Popen([PYTHON, SCRIPT], stdin=PIPE, stderr=PIPE, stdout=PIPE)
