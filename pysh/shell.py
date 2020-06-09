from multiprocessing import Process
import sys
import os
import tty
import termios
from threading import Thread
import logging
from dataclasses import dataclass


@dataclass
class State:
    line: str = ""
    i: int = 0
    esc_i: int = 0


class Shell:
    def __init__(self, command_handler):
        logger_name = ".".join(__name__.split(".")[:-1] + [self.__class__.__name__])
        self.logger = logging.getLogger(logger_name)
        self.process = Process(target=self.run)
        self.cols = None
        self.lines = None
        self.command_handler = command_handler
        self.job_process = None

    def on_sigwinch(self, sig, frame):
        self.update_size()

    def update_size(self):
        # print(os.popen('tput cols', 'r').readline())
        # print(os.popen('tput lines', 'r').readline())
        size = os.popen('stty size', 'r').readline().strip()
        lines, cols = size.split()
        self.lines = int(lines)
        self.cols = int(cols)

    def wait_process(self, p):
        if isinstance(p, Process):
            p.join()
        else:
            p.wait()
        self.job_process = None
        print("> ", end="")
        sys.stdout.flush()

    def execute(self, cmd):
        p = self.command_handler(cmd)
        if not p:
            print("> ", end="")
            sys.stdout.flush()
            return
        if isinstance(p, Process):
            p.start()
        self.job_process = p
        t = Thread(target=self.wait_process, args=(p,))
        t.start()

    def process_data(self, data: bytes, state: State, fileobj):
        for b in data:
            self.parse(b, state, fileobj)

    def parse(self, data: int, state: State, fileobj):
        if self.job_process:
            if data == 3:
                print("^C")
                self.job_process.kill()
            return

        if state.esc_i > 0:
            if state.esc_i == 1:
                if data == ord('['):
                    state.esc_i = 2
                    return
                else:
                    state.esc_i = 0
            if state.esc_i == 2:
                if data == ord('A'):
                    state.esc_i = 0
                    return
                elif data == ord('B'):
                    state.esc_i = 0
                    return
                elif data == ord('C'):
                    if state.i < len(state.line):
                        state.i = state.i + 1
                        print("\x1b[C", end="")
                        sys.stdout.flush()
                    state.esc_i = 0
                    return
                elif data == ord('D'):
                    if state.i > 0:
                        state.i = state.i - 1
                        print("\x1b[D", end="")
                        sys.stdout.flush()
                    state.esc_i = 0
                    return
                else:
                    state.esc_i = 0

        if data == 0x1b:
            state.esc_i = 1
        elif data == ord('\n') or data == ord('\r'):  # \n = 10, \r = 13
            state.line = state.line.strip()
            if state.line == "exit":
                raise SystemExit
            print("\r")
            if len(state.line) > 0:
                self.execute(state.line)
            else:
                print("> ", end="")
                sys.stdout.flush()
            state.line = ""
            state.i = 0
        elif data == 0x7f:
            if state.i > 0:
                if state.i == len(state.line):
                    print("\b\x1b[K", end="")
                    state.line = state.line[:state.i - 1]
                    state.i = state.i - 1
                else:
                    head = state.line[:state.i - 1]
                    tail = state.line[state.i:]
                    print("\b" + tail + "\x1b[K\x1b[%dD" % len(tail), end="")
                    sys.stdout.flush()
                    state.line = head + tail
                    state.i = state.i - 1
        elif 32 <= data < 127:
            if state.i == len(state.line):
                print(chr(data), end="")
                sys.stdout.flush()
                state.line = state.line + chr(data)
            else:
                head = state.line[:state.i]
                tail = state.line[state.i:]
                print(chr(data) + tail + "\x1b[%dD" % len(tail), end="")
                sys.stdout.flush()
                state.line = head + chr(data) + tail
            state.i = state.i + 1
        elif data == 3:
            print("^C")
            sys.stdout.flush()
            state.line = ""
            state.i = 0
        else:
            print("^%s(%d)" % (chr(ord('A') + data - 1), data), end="")
            sys.stdout.flush()

    def run(self):
        print("Welcome to PySh!")
        print("> ", end="")
        sys.stdout.flush()
        # fileobj = open(0, "br")
        fileobj = open(0)
        sys.stdin = fileobj
        old_attr = tty.tcgetattr(fileobj)
        try:
            tty.setraw(fileobj)
            attr = tty.tcgetattr(fileobj)
            attr[tty.OFLAG] |= termios.OPOST
            tty.tcsetattr(fileobj, tty.TCSANOW, attr)

            state = State()
            while True:
                data = os.read(fileobj.fileno(), 1)
                self.logger.debug("data=%r, state=%r", data, state)
                if not data:
                    continue
                self.process_data(data, state, fileobj)
        except KeyboardInterrupt:
            pass
        finally:
            tty.tcsetattr(fileobj, tty.TCSADRAIN, old_attr)

    def start(self):
        self.process.start()

    def join(self):
        self.process.join()