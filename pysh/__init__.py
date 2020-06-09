from .shell import Shell
import logging

logging.basicConfig(filename="pysh.log", level=logging.DEBUG)
logging.getLogger("pysh").setLevel(logging.DEBUG)
