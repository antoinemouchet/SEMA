import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
import angr


class setsid(angr.SimProcedure):
    # pylint: disable=arguments-differ
    def run(self):
        """
        if self.state.globals['is_leader_group'] :
            return -1
        else :
            self.state.globals['is_leader_group'] = True
            return self.state.posix.pid
        """
        return self.state.solver.Unconstrained(
            "unconstrained_ret_%s" % self.display_name,
            self.state.arch.bits,
            key=("api", "?", self.display_name),
        )
