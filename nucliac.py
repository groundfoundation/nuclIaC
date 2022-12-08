#!/usr/bin/env python3
# NuclIaC 
# Scripting tool for managing IaC 

from optparse import OptionParser
import nucliMod as nucli

#parse options

def parseOpts():
    parser = OptionParser("usage: %prog [options] {action}")
    parser.add_option("-n", "--no-prompt", dest="prompt", action="store_false",
                      default=True, help="do not prompt for confirmation")
    parser.add_option("-e", "--environment", dest="environment", action="store", 
                        type="string", help="environemnt name to administer")
    parser.add_option("-s", "--service", dest="service", action="store", 
                        type="string", help="service name to administer")
    parser.add_option("-d", "--deployment", dest="deployment", action="store", 
                        type="string", help="deployment name to administer")
    return parser.parse_args()

(options, args) = parseOpts()
#print(f"Options: {options}\nArgs:{args}")
env = nucli.init(options.service, options.environment, options.deployment, args) 
env.runArgs()

