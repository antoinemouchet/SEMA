import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
import angr


class getgid(angr.SimProcedure):
    # pylint: disable=arguments-differ
    def run(self):
        return 1000
