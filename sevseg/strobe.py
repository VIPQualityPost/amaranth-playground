from amaranth import *
from amaranth.build import *
from amaranth.lib.coding import Decoder

from amaranth_boards.resources import *
from alchitry_cu import AlchitryCuPlatform

class Strobe(Elaboratable):
    def __init__(self, channels, switch, width, speed):
        self.i0 = Signal(width)
        self.i1 = Signal(width)
        self.i2 = Signal(width)
        self.i3 = Signal(width)
        self.ch = channels
        self.sw = switch
        self.speed = speed
        self.width = width

    def elaborate(self, platform):
        m = Module()

        data = Cat([self.i0, self.i1, self.i2, self.i3])

        freq = int(platform.default_clk_frequency // self.speed) # 200Hz
        counter = Signal(range(freq + 1))

        m.submodules.onehot = onehot = Decoder(4)
        ocnt = Signal(2, reset=0)

        with m.If(counter == freq):
            m.d.comb += onehot.i.eq(ocnt)

            m.d.sync +=[
                counter.eq(0),
                ocnt.eq(ocnt + 1),
                self.sw.o.eq(onehot.o),
                self.ch.eq(data >> self.width*ocnt)]

        with m.Else():
            m.d.sync += counter.eq(counter + 1)

        return m


