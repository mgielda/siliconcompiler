###############################################################################
# Created by write_sdc
# Thu May  6 14:51:07 2021
###############################################################################
current_design jpeg_encoder
###############################################################################
# Timing Constraints
###############################################################################
create_clock -name clk -period 1.9775 -waveform {0.0000 0.9887} [get_ports {clk}]
###############################################################################
# Environment
###############################################################################
###############################################################################
# Design Rules
###############################################################################