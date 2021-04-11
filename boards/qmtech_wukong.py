import os
import textwrap
import subprocess

from nmigen.build import *
from nmigen.build.run import LocalBuildProducts
from nmigen.cli import main_parser, main_runner
from nmigen.vendor.xilinx_7series import *
from nmigen_boards.resources import *

class Platform(Xilinx7SeriesPlatform):
    device = "xc7a100t"
    package = "fgg676"
    speed = "1"
    default_clk = "clk50"
    default_rst = "rst"
    resources = [
        Resource("clk50", 0, Pins("M22", dir="i"), Clock(50e6), Attrs(IOSTANDARD="LVCMOS33")),
        Resource("rst", 0, PinsN("J8", dir="i"), Attrs(IOSTANDARD="LVCMOS33")),
        UARTResource(0, tx="E3", rx="F3", attrs=Attrs(IOSTANDARD="LVCMOS33")),
        *LEDResources(pins="J6 H6", attrs=Attrs(IOSTANDARD="LVCMOS33")),
        *ButtonResources(pins="H7 J8", invert=True, attrs=Attrs(IOSTANDARD="LVCMOS33")),
        #*SPIFlashResources(0, cs="P18", clk="H13", mosi="R14", miso="R15", wp="P14", hold="N14", attrs=Attrs(IOSTANDARD="LVCMOS33")), #MT25QL128ABA1ESE
        Resource("eth_gmii", 0, #RTL8211EG
            Subsignal("rst",    PinsN("R1",     dir="o")),
            Subsignal("mdio",   Pins("H1",      dir="io")),
            Subsignal("mdc",    Pins("H2",      dir="o")),
            Subsignal("gtx_clk",Pins("U1",      dir="o"), Clock(125e6)),
            Subsignal("tx_clk", Pins("M2",      dir="i")),
            Subsignal("tx_en",  Pins("T2",      dir="o")),
            Subsignal("tx_er",  Pins("J1",      dir="o")),
            Subsignal("tx_data",Pins("R2 P1 N2 N1 M1 L2 K2 K1",  dir="o")),
            Subsignal("rx_clk", Pins("P4",      dir="i")),
            Subsignal("rx_dv",  Pins("L3",      dir="i"), Attrs(PULLDOWN="TRUE")),
            Subsignal("rx_er",  Pins("U5",      dir="i")),
            Subsignal("rx_data",Pins("M4 N3 N4 P3 R3 T3 T4 T5", dir="i")),
            Subsignal("col",    Pins("U4",      dir="i")),
            Subsignal("crs",    Pins("U2",      dir="i")),
            Attrs(IOSTANDARD="LVCMOS33")),
        Resource("eth_rgmii", 0,
            Subsignal("rst",    PinsN("R1",     dir="o")),
            Subsignal("mdio",   Pins("H1",      dir="io")),
            Subsignal("mdc",    Pins("H2",      dir="o")),
            Subsignal("tx_clk", Pins("U1",      dir="o"), Clock(125e6)),
            Subsignal("tx_ctl", Pins("T2",      dir="o")),
            Subsignal("tx_data",Pins("R2 P1 N2 N1",  dir="o")),
            Subsignal("rx_clk", Pins("P4",      dir="i")),
            Subsignal("rx_ctl", Pins("L3",      dir="i"), Attrs(PULLDOWN="TRUE")),
            Subsignal("rx_data",Pins("M4 N3 N4 P3", dir="i")),
            Attrs(IOSTANDARD="LVCMOS33")),
        Resource("eth_mii", 0,
            Subsignal("rst",    PinsN("R1",     dir="o")),
            Subsignal("mdio",   Pins("H1",      dir="io")),
            Subsignal("mdc",    Pins("H2",      dir="o")),
            Subsignal("tx_clk", Pins("M2",      dir="i")),
            Subsignal("tx_en",  Pins("T2",      dir="o")),
            Subsignal("tx_er",  Pins("J1",      dir="o")),
            Subsignal("tx_data",Pins("R2 P1 N2 N1",  dir="o")),
            Subsignal("rx_clk", Pins("P4",      dir="i")),
            Subsignal("rx_dv",  Pins("L3",      dir="i"), Attrs(PULLDOWN="TRUE")),
            Subsignal("rx_er",  Pins("U5",      dir="i")),
            Subsignal("rx_data",Pins("M4 N3 N4 P3", dir="i")),
            Subsignal("col",    Pins("U4",      dir="i")),
            Subsignal("crs",    Pins("U2",      dir="i")),
            Attrs(IOSTANDARD="LVCMOS33")),
        Resource("ddr3", 0, #MT41K128M16JT-125:K
            Subsignal("a", Pins("E17 G17 F17 C17 G16 D16 H16 E16 H14 F15 F20 H15 C18 G15", dir="o")),
            Subsignal("dq", Pins("D21 C21 B22 B21 D19 E20 C19 D20 C23 D23 B24 B25 C24 C26 A25 B26", dir="io"), Attrs(IN_TERM="UNTUNED_SPLIT_40")),
            Subsignal("ba",  Pins("B17 D18 A17", dir="o")),
            Subsignal("clk", DiffPairs("F18", "F19", dir="o"), Attrs(IOSTANDARD="DIFF_SSTL135")),
            Subsignal("clk_en", Pins("E18", dir="o")),
            Subsignal("cs",  PinsN("E22", dir="o")),
            Subsignal("we",  PinsN("A18", dir="o")),
            Subsignal("ras", PinsN("A19", dir="o")),
            Subsignal("cas", PinsN("B19", dir="o")),
            Subsignal("dqs", DiffPairs("B20 A23", "A20 A24", dir="io"), Attrs(IOSTANDARD="DIFF_SSTL135")),
            Subsignal("dm",  Pins("A22 C22", dir="o")),
            Subsignal("odt", Pins("G19",    dir="o")),
            Subsignal("reset", PinsN("H17", dir="o")),
            Attrs(IOSTANDARD="SSTL135", SLEW="FAST")),
        Resource("hdmi_out", 0, #TPD12S016
            Subsignal("scl",     Pins("B2", dir="o"), Attrs(IOSTANDARD="I2C")),
            Subsignal("sda",     Pins("A2", dir="o"), Attrs(IOSTANDARD="I2C")),
            Subsignal("hdp",     PinsN("A3", dir="o"),Attrs(IOSTANDARD="LVCMOS33")),
            Subsignal("cec",     Pins("B1", dir="o"), Attrs(IOSTANDARD="LVCMOS33")),
            Subsignal("clk",     DiffPairs("D4", "C4", dir="o")),
            Subsignal("d",       DiffPairs("E1 F2 G2", "D1 E2 G1", dir="o")),
            Attrs(IOSTANDARD="TMDS_33"),
        ),
    ]

    connectors = [
        Connector("j", 10,
            "H4 F4 A4 A5 - - J4 G4 B4 B5 - -"),
        Connector("j", 11,
            "D5 G5 G7 G8 - - E5 E6 D6 G6 - -"),
        Connector("j", 12,
            "-    -    AB26 AC26 AB24 AC24 AA24 AB25 AA22 AA23 Y25 AA25  W25  Y26  Y22  Y23  W21  Y21 V26  W26"
            "U25  U26  V24  W24  V23  W23  V18  W18  U22  V22  U21  V21  T20  U20  T19  U19  -    -   -    -  "),
        Connector("jp", 2,
            "- - H21 H22 K21 J21 H26 G26 G25 F25 G20 G21 F23 E23 E26 D26 E25 D25"),
        Connector("jp", 3,
            "- - AF7  AE7  AD8  AC8  AF9  AE9  AD12 AC10 - - AA11 AB11"
            "- - AF11 AE11 AD14 AC14 AF13 AE13 AD12 AC12 - -          "),
    ]

    def toolchain_prepare(self, fragment, name, **kwargs):
        overrides = {
            "script_before_bitstream":
                "set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]",
            "script_after_bitstream":
                "write_cfgmem -force -format bin -interface spix4 -size 16 "
                "-loadbit \"up 0x0 {name}.bit\" -file {name}.bin".format(name=name),
            "add_constraints":
                """
                set_property CFGBVS VCCO [current_design]
                set_property CONFIG_VOLTAGE 3.3 [current_design]
                set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets {pin_clk50_0/clk50_0__i}]
                """
        }
        return super().toolchain_prepare(fragment, name, **overrides, **kwargs)

    def toolchain_program(self, product: LocalBuildProducts, name: str):
        vivado = os.environ.get("VIVADO", "vivado")
        with product.extract("{}.bit".format(name)) as bitstream_filename:
            cmd = textwrap.dedent(
                """
                open_hw_manager
                connect_hw_server
                open_hw_target
                current_hw_device [lindex [get_hw_devices] 0]
                set_property PROGRAM.FILE {{{}}} [current_hw_device]
                program_hw_devices
                close_hw_manager
                """
            ).format(bitstream_filename).encode("utf-8")
            subprocess.run([vivado, "-mode", "tcl"], input=cmd, check=True)

if __name__ == '__main__':
    from .test.blinky import *
    Platform().build(Blinky(), do_program=True)
