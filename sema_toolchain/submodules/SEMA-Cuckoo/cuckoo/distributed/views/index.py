import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
# Copyright (C) 2017 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

from flask import Blueprint, render_template

blueprint = Blueprint("index", __name__)
routes = ["/"]

@blueprint.route("/")
def index():
    return render_template("index.html")
