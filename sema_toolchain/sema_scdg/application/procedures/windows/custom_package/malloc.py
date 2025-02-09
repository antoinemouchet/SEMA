import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
import angr
import itertools

######################################
# malloc
######################################

malloc_mem_counter = itertools.count()


class malloc(angr.SimProcedure):
    # pylint:disable=arguments-differ
    def run(self, sim_size):
        #print("malloc")
        return self.state.heap._malloc(sim_size)
