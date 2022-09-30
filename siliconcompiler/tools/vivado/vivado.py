import os
import importlib
import re
import shutil
import sys
import siliconcompiler


####################################################################
# Make Docs
####################################################################

def make_docs():
    '''
    Vivado is an FPGA programming tool suite from Xilinx used to
    program Xilinx devices.

    Documentation: https://www.xilinx.com/products/design-tools/vivado.html

    '''

    chip = siliconcompiler.Chip('<design>')
    chip.set('arg','step', 'compile')
    chip.set('arg','index', '<index>')
    setup(chip)
    return chip

################################
# Setup Tool (pre executable)
################################

def setup(chip, mode='batch'):
    '''
    '''

    # default tool settings, note, not additive!
    tool = 'vivado'
    vendor = 'xilinx'
    refdir = 'tools/'+tool
    script = 'compile.tcl'
    step = chip.get('arg','step')
    index = chip.get('arg','index')

    clobber = True

    if mode == 'batch':
        clobber = True
        script = '/compile.tcl'
        option = "-mode batch -source"

    # General settings
    chip.set('tool', tool, 'exe', tool, clobber=clobber)
    chip.set('tool', tool, 'vendor', vendor, clobber=clobber)
    chip.set('tool', tool, 'vswitch', '-version', clobber=clobber)
    chip.set('tool', tool, 'refdir', step, index, refdir, clobber=clobber)
    chip.set('tool', tool, 'script', step, index, script, clobber=clobber)
    chip.set('tool', tool, 'threads', step, index, os.cpu_count(), clobber=clobber)
    chip.set('tool', tool, 'option', step, index, option, clobber=clobber)

################################
# Version Check
################################

def parse_version(stdout):
    # Vivado v2021.1 (64-bit)
    # SW Build 3247384 on Thu Jun 10 19:36:07 MDT 2021
    # IP Build 3246043 on Fri Jun 11 00:30:35 MDT 2021
    # Copyright 1986-2021 Xilinx, Inc. All Rights Reserved.

    # strip off the "1" prefix if it's there
    version = stdout.split(' ')

    return(version[1])
