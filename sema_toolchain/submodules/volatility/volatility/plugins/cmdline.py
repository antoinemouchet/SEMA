import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
# Volatility
# Copyright (C) 2007-2013 Volatility Foundation
#
# This file is part of Volatility.
#
# Volatility is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Volatility is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Volatility.  If not, see <http://www.gnu.org/licenses/>.
#

import volatility.plugins.taskmods as taskmods
from volatility.renderers import TreeGrid

class Cmdline(taskmods.DllList):
    """Display process command-line arguments"""
    def __init__(self, config, *args, **kwargs):
        taskmods.DllList.__init__(self, config, *args, **kwargs)
        config.add_option("VERBOSE", short_option = 'v',
                          default = False, cache_invalidator = False,
                          help = "Display full path of executable",
                          action = "store_true")

    def unified_output(self, data):
        # blank header in case there is no shimcache data
        return TreeGrid([("Process", str),
                       ("PID", int),
                       ("CommandLine", str),
                       ], self.generator(data))

    def generator(self, data):
        for task in data:
            cmdline = ""
            name = str(task.ImageFileName)
            try:
                if self._config.VERBOSE and task.SeAuditProcessCreationInfo.ImageFileName.Name != None:
                    name = str(task.SeAuditProcessCreationInfo.ImageFileName.Name)
            except AttributeError:
                pass
            if task.Peb:
                cmdline = "{0}".format(str(task.Peb.ProcessParameters.CommandLine or '')).strip()
            yield (0, [name, int(task.UniqueProcessId), str(cmdline)])

    def render_text(self, outfd, data):
        for task in data:
            pid = task.UniqueProcessId
            name = str(task.ImageFileName)
            try:
                if self._config.VERBOSE and task.SeAuditProcessCreationInfo.ImageFileName.Name != None:
                    name = str(task.SeAuditProcessCreationInfo.ImageFileName.Name)
            except AttributeError:
                pass

            outfd.write("*" * 72 + "\n")
            outfd.write("{0} pid: {1:6}\n".format(name, pid))

            if task.Peb:
                outfd.write("Command line : {0}\n".format(str(task.Peb.ProcessParameters.CommandLine or '')))
