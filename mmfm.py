#!/usr/bin/env python3

import sys

sys.path.append("lib/pyMattermost/src")

from src.Application import Application

app = Application(sys.argv)
app.run()
