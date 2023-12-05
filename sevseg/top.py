from amaranth import *
from amaranth.build import *
from amaranth.lib.coding import Decoder 
from amaranth_boards.resources import *

from strobe import Strobe
from sevseg_decoder import SevSegDecoder
from alchitry_cu import AlchitryCuPlatform

platform = AlchitryCuPlatform()
platform.add_resources([
    Display7SegResource("seven_segment", 0, 
        a="1", b="2", c="20", d="19",
        e="18", f="4", g="3", dp="17", 
        conn=("bank",0), invert = True,
        attrs = Attrs(IO_STANDARD = "SB_LVCMOS") 
        ),

    Resource("anodes",0,
        Pins("21 22 5 6", conn=("bank", 0), 
        dir="o", invert = True,) # Need invert because p-ch
        ),
])

class top(Elaboratable):
    def __init__(self):
        self.rst = Signal(1)
        self.en = Signal(1)

    def elaborate(self):
        m = Module()

        disp = platform.request("seven_segment")
        sevseg = Cat([disp.a, disp.b, disp.c, disp.d,
                        disp.e, disp.f, disp.g, disp.dp])

        anodes = platform.request("anodes")

        freq = int(platform.default_clk_frequency // 4)
        counter = Signal(range(freq + 1))

        number = Signal(4)
        m.submodules.digit0 = d0 = SevSegDecoder()
        m.submodules.digit1 = d1 = SevSegDecoder()
        m.submodules.digit2 = d2 = SevSegDecoder()
        m.submodules.digit3 = d3 = SevSegDecoder()
        m.submodules.strobe = strobe = Strobe(sevseg, anodes, 8, 200)

        with m.If(counter == freq):
            m.d.comb += [
                d0.i.eq(number),
                d1.i.eq(number+1),
                d2.i.eq(number+2),
                d3.i.eq(number+3)]

            m.d.sync += [
                counter.eq(0),
                number.eq(number+1),
                strobe.i0.eq(d0.o),
                strobe.i1.eq(d1.o),
                strobe.i2.eq(d2.o),
                strobe.i3.eq(d3.o)]

        with m.Else():
            m.d.sync += counter.eq(counter + 1)

        return m

if __name__ == "__main__":
    platform.build(top, do_program=True)
