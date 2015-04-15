#!/usr/bin/env python
#hard code in the python interpreter in the metamos python virtual environment
import ConfigParser #renamed to configparser in Python 3
import argparse
import sys, os
from time import strftime
import subprocess

#get configuration options
def getConfig(configfile):
    #instantiate a configuration variable and read it in
    config = ConfigParser.SafeConfigParser() 
    config.readfp(configfile)
    return config

#get commandline options
def getOpts():
    parser = argparse.ArgumentParser() 
    #add arguments here
    parser.add_argument('-f','--file', metavar='FILE', action='store', nargs='?', \
            type=argparse.FileType('r'), help='Optionally specify an input configuration file',\
            dest='configfile',default=configfile)

    parser.add_argument('-v','--verbose', action='store_true', help='Turn on verbose output', \
            dest='verbose', default=verbose)

    parser.add_argument('--list-programs', action='store_true', help='List the programs', dest='list_progs', default=False)


    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(0)

    return parser.parse_args()

#start execution from 'main'
def main():
    global verbose 
    opts = getOpts() #get commandline options
    verbose = opts.verbose

    if verbose: print('Options used: '+str(opts)+'\n')
    logfile.write('Options used: '+str(opts)+'\n')

    global config
    config = getConfig(opts.configfile ) #read in configuration options

    if opts.list_progs: 
        for prog in config.sections(): print(prog) 



    
    #test()
    logfile.close()
    sys.exit(0)

#function to test things with
def test():
    #print verbose
    print
    init = config.get('metamos','init_pipeline')
    init_opts = config.get('metamos','init_arguments')
    #print config.get('metamos','run_arguments') 
    subprocess.Popen([init,init_opts], stdout=logfile)
    print
    return

#define all global variables needed here, then run main()
configfile = 'pipeline.config'
verbose = False 
currTime = strftime('%Y-%m-%d_%H:%M:%S')
logfile = open(str(currTime) +'.log','a')
errfile = open(str(currTime) +'.err','a')

main()
