from pysh import Shell
import os
from subprocess import Popen
import shlex


def execute(cmd):
    args = shlex.split(cmd)
    args0 = args[0]
    if os.path.exists(args0):
        pass
    elif os.path.exists("/bin/" + args0):
        args0 = "/bin/" + args0
    elif os.path.exists("/usr/bin/" + args0):
        args0 = "/usr/bin/" + args0
    elif os.path.exists("/usr/local/bin/" + args0):
        args0 = "/usr/local/bin/" + args0
    else:
        print("pysh: command not found: " + cmd)
        return None
    p = Popen([args0] + args[1:])
    return p


if __name__ == '__main__':
    s = Shell(command_handler=execute)
    s.start()
    try:
        s.join()
    except KeyboardInterrupt:
        pass
