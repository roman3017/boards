import os
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
       Resource("clk25", 0, Pins("T14", dir="i"), Clock(25e6), Attrs(IOSTANDARD="LVCMOS33"))
    ]
    connectors = []

    def toolchain_prepare(self, fragment, name, **kwargs):
        overrides = {
            "script_before_bitstream":
                """
		set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]
		set_property BITSTREAM.CONFIG.CONFIGRATE 66 [current_design]
		""",
            "add_constraints":
                """
                set_property CFGBVS VCCO [current_design]
                set_property CONFIG_VOLTAGE 3.3 [current_design]
                """
        }
        return super().toolchain_prepare(fragment, name, **overrides, **kwargs)

    def toolchain_program(self, product, name, **kwargs):
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
