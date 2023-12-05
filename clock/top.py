from amaranth import *
from amaranth.build import *
from amaranth.lib.coding import Decoder 
from amaranth_boards.resources import *

from sevseg_decoder import SevSegDecoder
from doubledabble import DoubleDabble
from strobe import Strobe
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
                        disp.e, disp.f, disp.g])

        anodes = platform.request("anodes")

        freq = int(platform.default_clk_frequency)
        counter = Signal(range(freq + 1))

        hrCounter = Signal(4)                           # Up to 12
        minCounter = Signal(6)                          # Up to 60
        secCounter = Signal(6)                          # Up to 60

        m.submodules.hour = hour = DoubleDabble()       # Binary to BCD
        m.submodules.minute = minute = DoubleDabble() 
        m.submodules.second = second = DoubleDabble() 

        m.submodules.digit0 = digit0 = SevSegDecoder()  # BCD to 7-segment
        m.submodules.digit1 = digit1 = SevSegDecoder()
        m.submodules.digit2 = digit2 = SevSegDecoder()
        m.submodules.digit3 = digit3 = SevSegDecoder()
        
        m.submodules.strobe = strobe = Strobe(sevseg, anodes.o, 7, 200)

        with m.If(counter == freq):
            with m.If(secCounter == 59):
                m.d.sync += secCounter.eq(0)

                with m.If(minCounter == 59):
                    m.d.sync += minCounter.eq(0)

                    with m.If(hrCounter == 12):
                        m.d.sync += hrCounter.eq(0)

                    with m.Else():
                        m.d.sync += hrCounter.eq(hrCounter + 1)

                with m.Else():
                    m.d.sync += minCounter.eq(minCounter + 1)

            with m.Else():
                m.d.sync += secCounter.eq(secCounter + 1)

            m.d.sync += [
                counter.eq(0),
                second.i.eq(secCounter),
                minute.i.eq(minCounter),
                hour.i.eq(hrCounter)]

        with m.Else():
            m.d.sync += counter.eq(counter + 1)

        m.d.sync +=[
            digit0.i.eq(minute.outHi),
            digit1.i.eq(minute.outLo),
            digit2.i.eq(second.outHi),
            digit3.i.eq(second.outLo),
            strobe.i0.eq(digit0.o),
            strobe.i1.eq(digit1.o),
            strobe.i2.eq(digit2.o),
            strobe.i3.eq(digit3.o)]

        return m

if __name__ == "__main__":
    platform.build(top, do_program=True)
