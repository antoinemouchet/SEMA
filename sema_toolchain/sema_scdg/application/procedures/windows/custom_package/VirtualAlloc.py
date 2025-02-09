import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
import angr
import logging

import os

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

def convert_prot(prot):
    """
    Convert from a windows memory protection constant to an angr bitmask
    """
    # https://msdn.microsoft.com/en-us/library/windows/desktop/aa366786(v=vs.85).aspx
    if prot & 0x10:
        return 4
    if prot & 0x20:
        return 5
    if prot & 0x40:
        return 7
    if prot & 0x80:
        return 7
    if prot & 0x01:
        return 0
    if prot & 0x02:
        return 1
    if prot & 0x04:
        return 3
    if prot & 0x08:
        return 3
    raise angr.errors.SimValueError("Unknown windows memory protection constant: %#x" % prot)

def deconvert_prot(prot):
    """
    Convert from a angr bitmask to a windows memory protection constant
    """
    if prot in (2, 6):
        raise angr.errors.SimValueError("Invalid memory protection for windows process")
    return [0x01, 0x02, None, 0x04, 0x10, 0x20, None, 0x40][prot]

# https://msdn.microsoft.com/en-us/library/windows/desktop/aa366890(v=vs.85).aspx
class VirtualAlloc(angr.SimProcedure):
    def run(self, lpAddress, dwSize, flAllocationType, flProtect):
        addrs = self.state.solver.eval_upto(lpAddress, 2)
        if len(addrs) != 1:
            raise angr.errors.SimValueError("VirtualAlloc can't handle symbolic lpAddress")
        addr = addrs[0]
        addr &= ~0xfff


        size = self.state.solver.max_int(dwSize)
        if dwSize.symbolic and size > self.state.libc.max_variable_size:
            lw.warning('symbolic VirtualAlloc dwSize %s has maximum %#x, greater than state.libc.max_variable_size %#x',
                      dwSize, size, self.state.libc.max_variable_size)
            size = self.state.libc.max_variable_size
            #raise Exception("Symbolic VirtualAlloc dwSize is too big")

        flagss = self.state.solver.eval_upto(flAllocationType, 2)
        if len(flagss) != 1:
            raise angr.errors.SimValueError("VirtualAlloc can't handle symbolic flAllocationType")
        flags = flagss[0]

        prots = self.state.solver.eval_upto(flProtect, 2)
        if len(prots) != 1:
            raise angr.errors.SimValueError("VirtualAlloc can't handle symbolic flProtect")
        prot = prots[0]
        angr_prot = convert_prot(prot)

        if flags & 0x00080000 or flags & 0x1000000:
            lw.warning("VirtualAlloc with MEM_RESET and MEM_RESET_UNDO are not supported")
            return addr

        ft = True if flags & 0x00100000 else False

        # if size == 0x7fff0000:
        #    return 0

        if flags & 0x00002000 or addr == 0: # MEM_RESERVE
            if addr == 0:
                while True:
                    addr = self.allocate_memory(size,from_top=ft)
                    try:
                        self.state.memory.map_region(addr, size, angr_prot, init_zero=True)
                    except angr.errors.SimMemoryError:
                        continue
                    else:
                        break
            else:
                try:
                    self.state.memory.map_region(addr, size, angr_prot, init_zero=True)
                except angr.errors.SimMemoryError:
                    lw.warning("...failed, bad address")
                    return 0

        if flags & 0x00001000: # MEM_COMMIT
            # we don't really emulate commit. we just check to see if the region was allocated.
            try:
                self.state.memory.permissions(addr)
            except angr.errors.SimMemoryError:
                lw.warning("...not reserved")
                return 0

        # if we got all the way to the end, nothing failed! success!
        return addr

    def allocate_memory(self,size,from_top=False):
        #if not from_top:
        addr = self.state.heap.mmap_base
        new_base = addr + size
        # else:
        #     addr = self.state.heap.max_addr
        #     new_base = addr - size

        if new_base & 0xfff:
            new_base = (new_base & ~0xfff) + 0x1000

        #if not from_top:
        self.state.heap.mmap_base = new_base
        # else:
        #     self.state.heap.max_addr = new_base
        return addr
