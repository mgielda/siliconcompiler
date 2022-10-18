import os
import sys
import shutil

import siliconcompiler

####################################################################
# Make Docs
####################################################################
def make_docs():
    '''
    Surelog is a SystemVerilog pre-processor, parser, elaborator,
    and UHDM compiler that provdes IEEE design and testbench
    C/C++ VPI and a Python AST API.

    Documentation: https://github.com/chipsalliance/Surelog

    Sources: https://github.com/chipsalliance/Surelog

    Installation: https://github.com/chipsalliance/Surelog

    '''

    chip = siliconcompiler.Chip('<design>')
    chip.set('arg','step','import')
    chip.set('arg','index','0')
    setup(chip)
    return chip

################################
# Setup Tool (pre executable)
################################

def setup(chip):
    ''' Sets up default settings on a per step basis
    '''

    tool = 'surelog'
    step = chip.get('arg','step')
    index = chip.get('arg','index')

    exe = tool
    # Although Windows will find the binary even if the .exe suffix is omitted,
    # Surelog won't find the relative builtin.sv file unless we add it.
    if sys.platform.startswith('win32'):
        exe = f'{tool}.exe'

    # Standard Setup
    chip.set('tool', tool, 'exe', exe)
    chip.set('tool', tool, 'vswitch', '--version')
    chip.set('tool', tool, 'version', '>=1.13', clobber=False)
    chip.set('tool', tool, 'threads', step, index,  os.cpu_count(), clobber=False)

    # -parse is slow but ensures the SV code is valid
    # we might want an option to control when to enable this
    # or replace surelog with a SV linter for the validate step
    options = []
    options.append('-parse')

    # With newer versions of Surelog (at least 1.35 and up), this option is
    # necessary to make bundled versions work.
    # TODO: why?
    options.append('-nocache')

    # Wite back options to cfg
    chip.add('tool', tool, 'option', step, index, options)

    # Input/Output requirements
    chip.add('tool', tool, 'output', step, index, chip.top() + '.v')

    # Schema requirements
    chip.add('tool', tool, 'require', step, index, ",".join(['input', 'verilog']))

    # We package SC wheels with a precompiled copy of Surelog installed to
    # tools/surelog/bin. If the user doesn't have Surelog installed on their
    # system path, set the path to the bundled copy in the schema.
    if shutil.which('surelog') is None:
        surelog_path = os.path.join(os.path.dirname(__file__), 'bin')
        chip.set('tool', tool, 'path', surelog_path, clobber=False)

    # Log file parsing
    chip.set('tool', tool, 'regex', step, index, 'warnings', r'^\[WRN:', clobber=False)
    chip.set('tool', tool, 'regex', step, index, 'errors', r'^\[(ERR|FTL|SNT):', clobber=False)

def parse_version(stdout):
    # Surelog --version output looks like:
    # VERSION: 1.13
    # BUILT  : Nov 10 2021

    # grab version # by splitting on whitespace
    return stdout.split()[1]

################################
#  Custom runtime options
################################

def runtime_options(chip):

    ''' Custom runtime options, returnst list of command line options.
    '''

    cmdlist = []

    # Deduplicated source files
    # Library directories.
    ydir_files = chip.find_files('option', 'ydir')
    if len(ydir_files) != len(set(ydir_files)):
        chip.logger.warning(f"Removing duplicate 'ydir' inputs from: {ydir_files}")
    for value in set(ydir_files):
        cmdlist.append('-y ' + value)

    # Library files.
    vlib_files = chip.find_files('option', 'vlib')
    if len(vlib_files) != len(set(vlib_files)):
        chip.logger.warning(f"Removing duplicate 'vlib' inputs from: {vlib_files}")
    for value in set(vlib_files):
        cmdlist.append('-v ' + value)

    # Include paths.
    idir_files = chip.find_files('option', 'idir')
    if len(idir_files) != len(set(idir_files)):
        chip.logger.warning(f"Removing duplicate 'idir' inputs from: {idir_files}")
    for value in set(idir_files):
        cmdlist.append('-I' + value)

    # Extra environment variable defines (don't need deduplicating)
    for value in chip.get('option', 'define'):
        cmdlist.append('-D' + value)

    # Command-line argument file(s).
    cmdfiles = chip.find_files('option', 'cmdfile')
    if len(cmdfiles) != len(set(cmdfiles)):
        chip.logger.warning(f"Removing duplicate 'cmdfile' inputs from: {cmdfiles}")
    for value in set(cmdfiles):
        cmdlist.append('-f ' + value)

    # Source files.
    src_files = chip.find_files('input', 'verilog')
    if len(src_files) != len(set(src_files)):
        chip.logger.warning(f"Removing duplicate source file inputs from: {src_files}")
    for value in set(src_files):
        cmdlist.append(value)

    cmdlist.append('-top ' + chip.top())
    # make sure we can find .sv files in ydirs
    # TODO: need to add libext
    cmdlist.append('+libext+.sv+.v+.vh')

    # Set up user-provided parameters to ensure we elaborate the correct modules
    for param in chip.getkeys('option', 'param'):
        value = chip.get('option', 'param', param)
        cmdlist.append(f'-P{param}={value}')

    return cmdlist

################################
# Post_process (post executable)
################################

def post_process(chip):
    ''' Tool specific function to run after step execution
    '''
    step = chip.get('arg', 'step')

    if step != 'import':
        return 0

    # Look in slpp_all/file_elab.lst for list of Verilog files included in
    # design, read these and concatenate them into one pickled output file.
    with open('slpp_all/file_elab.lst', 'r') as filelist, \
            open(f'outputs/{chip.top()}.v', 'w') as outfile:
        for path in filelist.read().split('\n'):
            path = path.strip('"')
            if not path:
                # skip empty lines
                continue
            with open(path, 'r') as infile:
                outfile.write(infile.read())
            # in case end of file is missing a newline
            outfile.write('\n')

##################################################
if __name__ == "__main__":

    chip = make_docs()
    chip.write_manifest("surelog.json")
