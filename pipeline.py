#!/usr/bin/env python

import ConfigParser #renamed to configparser in Python 3
import argparse
import sys, os
from time import strftime
import subprocess
import shlex
import glob

#get configuration options
def get_config(configfile):
    #instantiate a configuration variable and read it in
    config = ConfigParser.SafeConfigParser() 
    config.readfp(configfile)
    return config

#get commandline options
def get_opts():
    parser = argparse.ArgumentParser() 
    #add arguments here
    parser.add_argument('-c','--config', metavar='FILE', action='store', nargs='?',
            type=argparse.FileType('r'), help='Optionally specify an input configuration file',
            dest='configfile',default=configfile)

    parser.add_argument('-v','--verbose', action='store_true', help='Turn on verbose output',
            dest='verbose', default=verbose)

    parser.add_argument('--list-programs', action='store_true', help='List the programs', dest='list_progs', default=False)

    parser.add_argument('--infile','-i', metavar='FILE',action='store', nargs='?',
            help='Specify an input file to read from, in the pipeline format', dest='infile', default=None)

    parser.add_argument('--outdir','-o', metavar='OUTDIR', action='store', nargs='?',
            help='Specify a directory to hold the project files.', dest='outdir',
            default='outdir')

    parser.add_argument('--fastqdir','-f', metavar='FASTQ DIR', action='store', nargs='?',
            help='Specify the directory holding the fastq (or gzipped fastq) files.', dest='fastqdir',
            default='')

     
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(0)

    return parser.parse_args()


def run_metamos(prog):
    outdir = os.path.abspath(opts.outdir)
    fastqdir = os.path.abspath(opts.fastqdir)
    input_line = inputs.pop(0).split()
    pairedness = input_line[4]
    filename = input_line[0] 
    try:
        if pairedness == 'single':
            input_file = glob.glob(fastqdir+'/'+filename+'*')[0]
        else:
            input_file_1 = glob.glob(fastqdir+'/'+filename + '_1*')[0]
            input_file_2 = glob.glob(fastqdir+'/'+filename + '_2*')[0]

    except:
        if verbose: print('File {} does not exist. Skipping.'.format(input_file) )
        logfile.write('File {} does not exist. Skipping.'.format(input_file) )
        sys.exit(1)

    command = shlex.split(config.get(prog,'init_pipeline') + ' ' + config.get(prog,'init_arguments') + ' -d '+outdir +' {}'.format('-1 {}'.format(input_file) if pairedness == 'single'
            else '-1 {} -2 {}'.format(input_file_1,input_file_2) ) ) 

    proc = subprocess.Popen(command, stdout=logfile, stderr=logfile)
    ret = proc.wait()
    logfile.flush()
    if ret != 0:
        print("metamos didn't complete successfully with the command:" \
                + ' '.join(command) + '\n')
        logfile.write("metamos didn't complete successfully with the command:" \
                + ' '.join(command) + '\n')
        return 1 
    
    command = shlex.split(config.get(prog,'run_pipeline') + ' ' + config.get(prog,'run_arguments') \
            + ' -d ' + outdir)

    proc = subprocess.Popen(command, stdout=logfile, stderr=logfile)
    #proc = subprocess.Popen(command)
    ret = proc.wait()
    logfile.flush()
    if ret != 0:
        print("metamos didn't complete successfully with the command: " \
                + ' '.join(command) + '\n')
        logfile.write("metamos didn't complete successfully with the command: " \
                + ' '.join(command) + '\n')
        return 1 
    return 0

    

def run_program(prog):
    bin = config.get(prog,'bin')
    arguments = config.get(prog,'arguments')
    proc = subprocess.Popen(shlex.split(bin+ ' ' +arguments), stdout=logfile, stderr=logfile)

#start execution from 'main'
def main():
    global verbose 
    global opts
    global config
    global inputs

    opts = get_opts() #get commandline options
    verbose = opts.verbose

    if verbose: print('Options used: '+str(opts)+'\n')
    logfile.write('Options used: '+str(opts)+'\n')

    config = get_config(opts.configfile ) #read in configuration options

    #read in config file sections to a tuple
    progs = tuple(config.sections() )
    if opts.list_progs: 
        for prog in progs: print(prog) 
        sys.exit(0)


    #read in the file of fastq names 
    if opts.infile is not None: 
        with open(opts.infile,'r') as infile:
            inputs = infile.readlines()
            logfile.write("Using input file: {}".format(infile))

    met_ret = run_metamos('metamos')
    if met_ret != 0:
       sys.exit(1) 
    

    #test
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

main()
