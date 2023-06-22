from amaranth import *
from amaranth.build import *
from amaranth.vendor.lattice_ice40 import *
from amaranth_boards.icesugar_nano import *

class top(Elaboratable):
    def elaborate(self):
        m = Module()

        half_freq = int(platform.default_clk_frequency // 2)
        led = platform.request("ledarray", 0)

        counter = Signal(range(half_freq +1))

        with m.If(counter == half_freq):
            m.d.sync+= led.eq(led+1)
            m.d.sync+= counter.eq(0)
        with m.Else():
            m.d.sync+= counter.eq(counter+1)
        return m

if __name__ == "__main__":
    platform = ICESugarNanoPlatform()
    platform.add_resources([
        Resource("ledarray", 0,
            Pins("7 8 9 10 1 2 3 4", conn=("pmod",2), invert=True, dir="o"))
    ])

    platform.build(top, do_program=True)