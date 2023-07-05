from amaranth import *
from amaranth.build import *
from amaranth.vendor.lattice_ice40 import *
from amaranth_boards.icesugar_nano import *

class top(Elaboratable):
    def elaborate(self):
        m = Module()

        pulse_freq = int(platform.default_clk_frequency / 6)
        led = platform.request("ledarray", 0)

        dir = Signal(1,reset=0)
        array = Signal(8,reset=1)
        counter = Signal(range(pulse_freq +1))

        with m.If(counter == pulse_freq):
            with m.Switch(dir):
                with m.Case(0):
                    m.d.sync+= array.eq(array << 1)
                with m.Case(1):
                    m.d.sync+= array.eq(array >> 1)
            
            with m.Switch(array):
                with m.Case(0b01000000):
                    m.d.sync+= dir.eq(1)
                with m.Case(0b00000010):
                    m.d.sync+= dir.eq(0)

            m.d.sync+= counter.eq(0)

        with m.Else():
            m.d.sync+= counter.eq(counter+1)

        m.d.comb+= led.eq(array)
        return m

if __name__ == "__main__":
    platform = ICESugarNanoPlatform()
    platform.add_resources([
        Resource("ledarray", 0,
            Pins("7 8 9 10 1 2 3 4", conn=("pmod",2), invert=True, dir="o"))
    ])

    platform.build(top, do_program=True)