import os
import textwrap
import subprocess

from nmigen.build import *
from nmigen.vendor.xilinx_7series import *
from nmigen_boards.resources import *

class TE0714(Xilinx7SeriesPlatform):
    device = "xc7a35t"
    package = "csg325"
    speed = "2"
    default_clk = "clk25"
    resources = [
        *LEDResources(pins="K18", attrs=Attrs(IOSTANDARD="LVCMOS33", PULLUP="true", drive="8")), 
        Resource("clk25", 0, Pins("T14", dir="i"), Clock(25e6), Attrs(IOSTANDARD="LVCMOS33")),

        # These are the pins that go into the XMOD programmer
        Resource("uart_rx", 0, Pins("L14", dir="i"), Attrs(IOSTANDARD="LVCMOS33")),
        Resource("uart_tx", 0, Pins("U10", dir="o"), Attrs(IOSTANDARD="LVCMOS33")),
    ]
    connectors = []

    def toolchain_prepare(self, fragment, name, **kwargs):
        overrides = {
            # The below error/warning allows us to use an internal clock as the
            # reference for the SERDES blocks
            "script_after_synth":
            """
            set_property SEVERITY WARNING [get_drc_checks REQP-49] 
            """,
            "script_before_bitstream":
                """
		set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]
		set_property BITSTREAM.CONFIG.CONFIGRATE 66 [current_design]
		""",
            "add_constraints":
                """
                set_property CFGBVS VCCO [current_design]
                set_property CONFIG_VOLTAGE 3.3 [current_design]
                create_clock -period 4.0 [get_pins -filter {REF_PIN_NAME=~*RXOUTCLK} -of_objects [get_cells -hierarchical -filter {NAME =~ *gtp*}]]
                """
        }
        return super().toolchain_prepare(fragment, name, **overrides, **kwargs)

    def toolchain_program(self, product, name,  programmer="vivado", **kwargs):
        if programmer == 'vivado':
            with product.extract("{}.bit".format(name)) as bitstream_filename:
                cmd = textwrap.dedent("""
                    open_hw_manager
                    connect_hw_server
                    open_hw_target
                    current_hw_device [lindex [get_hw_devices] 0]
                    set_property PROGRAM.FILE {{{}}} [current_hw_device]
                    program_hw_devices
                    close_hw_manager
                """).format(bitstream_filename).encode("utf-8")
                subprocess.run(["vivado", "-nolog", "-nojournal", "-mode", "tcl"], input=cmd, shell=True, check=True)
        else:
            openocd = os.environ.get("OPENOCD", "openocd")
            with product.extract("{}.bit".format(name)) as bitstream_filename:
                subprocess.check_call([
                    'openocd',
                    '-f', 'interface/jlink.cfg',
                    '-f', 'cpld/xilinx-xc7.cfg',
                    '-c', 'adapter speed 4000',
                    '-c', 'init',
                    '-c', 'xc7_program xc7.tap',
                    '-c', 'pld load 0 {}'.format(bitstream_filename.replace("\\", "\\\\")),
                    '-c', 'exit'
                ])

if __name__ == '__main__':
    from nmigen_boards.test.blinky import *
    TE0714().build(Blinky(), do_program=True)
