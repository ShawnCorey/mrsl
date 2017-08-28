import socket, threading, traceback
import curses
import curses.textpad
import datetime
from time import sleep
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-p','--port', default=80, type=int, help='Port number to listen on (default is 80)')
args = parser.parse_args()
PORT = args.port

socket.setdefaulttimeout(5)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', PORT))
s.listen(4)
clients = [] #list of clients connected
lock = threading.Lock()
exitScript = False

class gui(threading.Thread):

    def run(self):
        curses.wrapper(self.draw_ui)

    def draw_ui(self, stdscr):
        global clients
        global exitScript
        height, width = stdscr.getmaxyx()
        clientWin = stdscr.subwin(height-3, 17, 0, 0)
        clientWin.scrollok(True)
        bufferWin = stdscr.subwin(height-3, width-18,0, 18)
        bufferWin.scrollok(True)
        inputWin = stdscr.subwin(2, width-1,height-3, 0)
        inputWin.scrollok(True)
        tb = curses.textpad.Textbox(inputWin)
        stdscr.nodelay(1)

        k = 0
        sendCommand = False
        closeActive = False
        oldHeight = 0
        oldWidth = 0

        while k != 276: #276 is keycode for F12
            clientWin.clear()
            if len(clients) == 0:
                bufferWin.clear()
                bufferWin.refresh()
            height, width = stdscr.getmaxyx()
            if oldHeight != height or oldWidth != width:
                clientWin.resize(height-3, 17)
                bufferWin.resize(height-3, width-18)
                inputWin.resize(2, width-1)
            if k == 9: # 9 is keycode for tab
                for idx in range(0,len(clients)):
                    if clients[idx].active:
                        clients[idx].active = False
                        if idx >= len(clients)-1:
                            newIdx = 0
                        else:
                            newIdx = idx+1
                        clients[newIdx].active = True
                        clients[newIdx].updated = True
                        break
            elif k == 10:# 10 is keycode for enter
                sendCommand = True
            elif k == 274:# 274 is keycode for F10
                closeActive = True
            elif k != 0:
                tb.do_command(k)

            lineNum = 0
            for conn in clients:
                if conn.active:
                    if sendCommand:
                        conn.command = tb.gather()
                        sendCommand = False
                        inputWin.clear()
                    if closeActive:
                        conn.toClose = True
                        closeActive = False
                    clientWin.addstr(lineNum,0,"*"+conn.r_ip+"\n")
                    #Update buffer display to show updated log buffer
                    if conn.updated:
                        bufferWin.clear()
                        bufferWin.addstr(0,0,conn.buffer)
                        bufferWin.refresh()
                        conn.updated = False
                else:
                    clientWin.addstr(lineNum,0," "+conn.r_ip+"\n")
                lineNum+=1
            clientWin.refresh()
            inputWin.refresh()
            k = 0
            try:
                k = stdscr.getch()
            except:
                pass
            #sleep(0.1)
        exitScript = True

class remoteConn(threading.Thread):
    active = False
    toClose = False
    updated = False
    buffer = ""
    command = ""

    def __init__(self, sock):
        threading.Thread.__init__(self)
        socket, address = sock
        self.socket = socket
        self.r_ip, self.r_port = address
        logname = self.r_ip+"--"+datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")+".log"
        self.logfile = open(logname, "ab", 0)

    def updateBuffer(self, data):
        self.buffer += data.decode("utf-8")
        self.logfile.write(data)
        self.updated = True

    def run(self):
        global clients
        global exitScript
        global lock
        lock.acquire()
        clients.append(self)
        if len(clients) == 1:
            self.active = True
        lock.release()
        self.socket.settimeout(1)
        while exitScript == False and self.toClose == False:
            try:
                data = self.socket.recv(1024)
                if not data:
                    break
                self.updateBuffer(data)
            except Exception as e:
                pass
            if self.command != "":
                self.socket.send(bytearray(self.command, "utf-8"))
                self.updateBuffer(bytearray(self.command, "utf-8"))
                self.command = ""
        self.socket.close()

        lock.acquire()
        clients.remove(self)
        if self.active and len(clients) >= 1:
            clients[0].active = True
            clients[0].updated = True
        lock.release()
        self.logfile.close()

threads = []
while exitScript == False: # wait for socket to connect
    threads.append(gui().start())
    s.settimeout(1)
    while exitScript == False:
        try:
            threads.append(remoteConn(s.accept()).start())
        except:
            pass
for t in threads:
    try:
        t.join()
    except:
        pass
print("exiting")
