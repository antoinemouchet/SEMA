import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
import angr
import logging
import claripy

import os

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

# class memset(angr.SimProcedure):
#     #pylint:disable=arguments-differ

#     def run(self, dest, val, length):
#         if length.symbolic:
#             ptr = claripy.BVV(0x0, self.state.solver.eval(0x100)*8)
#             self.state.memory.store(self.state.solver.eval(dest), ptr)
#             return dest
#         else:
#             value = 0x0
#             if val.symbolic:
#                 value = 0x0
#             else:
#                 value = 0x0 # self.state.solver.eval(val) # TODO make loop -> SHITTY solution of SERENA (pair programming)
#             #ptr = claripy.BVV(value,length*8)
#             # ptr = claripy.BVV(0x0,length*8)
#             # self.state.memory.store(dest, ptr)
#             ptr = claripy.BVV(0x0, self.state.solver.eval(length)*8)
#             self.state.memory.store(self.state.solver.eval(dest), ptr)
#             return dest

class memset(angr.SimProcedure):
    # pylint:disable=arguments-differ

    @staticmethod
    def _repeat_bytes(byt, rep):
        """
        Get a long number for a byte being repeated for many times. This is part of the effort of optimizing
        performance of angr's memory operations.

        :param int byt: the byte to repeat
        :param int rep: times to repeat the byte
        :return: a long integer representing the repeating bytes
        ;rtype: int
        """

        if rep == 1:
            return byt

        remainder = rep % 2
        quotient = rep // 2

        r_ = memset._repeat_bytes(byt, quotient)
        if remainder == 1:
            r = r_ << ((quotient + 1) * 8)
            r |= (r_ << 8) + byt
        else:
            r = r_ << (quotient * 8)
            r |= r_
        return r

    def run(self, dst_addr, char, num):
        if char.size() != self.state.arch.byte_width:  # sizeof(char)
            char = self.state.solver.Extract(self.state.arch.byte_width - 1, 0, char)

        if self.state.solver.symbolic(num):
            lw.debug("symbolic length")
            max_size = self.state.solver.min_int(num) + self.state.libc.max_buffer_size
            write_bytes = self.state.solver.Concat(*([char] * max_size))
            self.state.memory.store(dst_addr, write_bytes, size=num)
        else:
            max_size = self.state.solver.eval(num)
            lw.debug("memset writing %d bytes", max_size)

            offset = 0
            while offset < max_size:
                chunksize = min(max_size - offset, 0x1000)

                if self.state.solver.symbolic(char):
                    lw.debug("symbolic char")
                    write_bytes = self.state.solver.Concat(*([char] * chunksize))
                else:
                    # Concatenating many bytes is slow, so some sort of optimization is required
                    if char._model_concrete.value == 0:
                        write_bytes = self.state.solver.BVV(0, chunksize * 8)
                    else:
                        rb = memset._repeat_bytes(char._model_concrete.value, chunksize)
                        write_bytes = self.state.solver.BVV(rb, chunksize * 8)

                self.state.memory.store(dst_addr + offset, write_bytes)
                offset += chunksize

        return dst_addr
