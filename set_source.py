#!/usr/bin/python
# encoding: utf-8

import sys
import os
from subprocess import Popen, PIPE
from workflow import Workflow

def main(wf):
    out, err = Popen(["mdfind","-name",".cbxml"], stdout=PIPE, stderr=PIPE).communicate()
    out = out.split("\n")
    wf.add_item("To ensure your file is found, make sure it ends in '.cbxml'", icon="info.png")
    for i in out:
        wf.add_item(os.path.split(i)[1],i, arg=i, valid=True)

    wf.send_feedback()

if __name__ == '__main__':
    wf = Workflow()
    # Assign Workflow logger to a global variable, so all module
    # functions can access it without having to pass the Workflow
    # instance around
    log = wf.logger
    sys.exit(wf.run(main))
