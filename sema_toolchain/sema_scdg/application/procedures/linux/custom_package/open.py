import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
import angr


class open(angr.SimProcedure):  # pylint:disable=W0622
    # pylint:disable=arguments-differ,unused-argument

    def run(self, p_addr, flags, mode):
        strlen = angr.SIM_PROCEDURES["libc"]["strlen"]

        p_strlen = self.inline_call(strlen, p_addr)
        p_expr = self.state.memory.load(
            p_addr, p_strlen.max_null_index, endness="Iend_BE"
        )
        path = self.state.solver.eval(p_expr, cast_to=bytes)
        # import pdb; pdb.set_trace()
        fd = self.state.posix.open(path, flags)
        if fd is None:
            return -1
        return fd
