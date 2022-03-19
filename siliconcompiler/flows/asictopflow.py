import siliconcompiler

def make_docs():
    '''A flow for stitching together hardened blocks without doing any automated
    place-and-route.

    This flow generates a GDS and a netlist for passing to a
    verification/signoff flow.
    '''
    chip = siliconcompiler.Chip()
    chip.set('flow', 'asictopflow')
    setup(chip)
    return chip

def setup(chip):
    flow = 'asictopflow'
    chip.node(flow, 'import', 'surelog')
    chip.node(flow, 'syn', 'yosys')
    chip.node(flow, 'export', 'klayout')
    chip.node(flow, 'merge', 'join')

    chip.edge(flow, 'import', 'export')
    chip.edge(flow, 'import', 'syn')

    chip.edge(flow, 'export', 'merge')
    chip.edge(flow, 'syn', 'merge')

    chip.set('mode', 'asic')

    chip.set('showtool', 'def', 'klayout')
    chip.set('showtool', 'gds', 'klayout')

    # Set default goal
    for step in chip.getkeys('flowgraph', flow):
        chip.set('metric', step, '0', 'errors', 'goal', 0)