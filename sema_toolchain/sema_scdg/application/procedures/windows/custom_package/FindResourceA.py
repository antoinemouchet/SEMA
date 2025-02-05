import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
import logging
import sys
import angr
import archinfo

import os

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class FindResourceA(angr.SimProcedure):
    def run(self, hModule, lpName, lpType):
        if not self.state.has_plugin("plugin_ressources"):
            lw.warning("The procedure FindRessourceA is using the plugin plugin_ressources which is not activated")
        minaddr = self.state.project.loader.min_addr
        name = self.state.mem[lpName].string.concrete
        rsrc = self.state.globals["rsrc"]
        offset = 0x10
        rsrctype =  self.state.solver.eval(self.state.memory.load(rsrc+offset,1))
        while rsrctype != self.state.solver.eval(lpType):
            offset += 8
            rsrctype =  self.state.solver.eval(self.state.memory.load(rsrc+offset,1))
        offset = self.state.solver.eval(self.state.memory.load(rsrc+offset+0x4,2,endness=archinfo.Endness.LE))
        nbnames = self.state.solver.eval(self.state.memory.load(rsrc+offset+0xc,2,endness=archinfo.Endness.LE))
        offset += 0x10
        tablefind = self.state.solver.eval(self.state.memory.load(rsrc+offset,2,endness=archinfo.Endness.LE))
        size = self.state.solver.eval(self.state.memory.load(rsrc+tablefind,2,endness=archinfo.Endness.LE))
        rsrcname = self.state.solver.eval(self.state.memory.load(rsrc+tablefind+2,2*size))
        rsrcname = rsrcname.to_bytes(2*size, 'big')
        rsrcname = rsrcname.decode('utf-16le')
        rsrcname = rsrcname.encode()
        while name != rsrcname and nbnames > 0:
            nbnames = nbnames - 1
            offset += 8
            tablefind = self.state.solver.eval(self.state.memory.load(rsrc+offset,2,endness=archinfo.Endness.LE))
            size = self.state.solver.eval(self.state.memory.load(rsrc+tablefind,2,endness=archinfo.Endness.LE))
            rsrcname = self.state.solver.eval(self.state.memory.load(rsrc+tablefind+2,2*size))
            rsrcname = rsrcname.to_bytes(2*size, 'big')
            rsrcname = rsrcname.decode('utf-16le')
            rsrcname = rsrcname.encode()
        if name != rsrcname and nbnames == 0:
            return 0x0
        offset = self.state.solver.eval(self.state.memory.load(rsrc+offset+0x4,2,endness=archinfo.Endness.LE))
        offset += 0x10
        offset = self.state.solver.eval(self.state.memory.load(rsrc+offset+0x4,2,endness=archinfo.Endness.LE))
        finaloffset = self.state.solver.eval(self.state.memory.load(rsrc+offset,4,endness=archinfo.Endness.LE))
        size = self.state.solver.eval(self.state.memory.load(rsrc+offset+0x4,4,endness=archinfo.Endness.LE))
        resource = self.state.solver.eval(self.state.memory.load(minaddr+finaloffset,size,endness=archinfo.Endness.LE))
        if self.state.has_plugin("plugin_ressources"):
            self.state.plugin_resources.resources[finaloffset+minaddr] = {"size": size, "name": name, "data": resource, "rsrcname": rsrcname}
        x = finaloffset+minaddr
        return finaloffset+minaddr
