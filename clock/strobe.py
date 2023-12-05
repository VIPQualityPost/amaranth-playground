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
        ch = self.ch
        sw = self.sw 
        
        if platform is None:
            freq = int(1e-6) // self.speed
        else:
            freq = int(platform.default_clk_frequency // self.speed) # 200Hz

        counter = Signal(range(freq + 1))

        m.submodules.onehot = onehot = Decoder(4)
        ocnt = Signal(2, reset=0)

        with m.If(counter == freq):
            m.d.comb += onehot.i.eq(ocnt)

            m.d.sync +=[
                counter.eq(0),
                ocnt.eq(ocnt + 1),
                sw.eq(onehot.o),
                ch.eq(data >> self.width*ocnt)]

        with m.Else():
            m.d.sync += counter.eq(counter + 1)

        return m

if __name__ == "__main__":
    from amaranth.sim import *

    dut = Strobe(Signal(8), Signal(4), 8, 10)

    def strobe_ut(strobe):
        yield strobe.i0.eq(0x11)
        yield strobe.i1.eq(0x22)
        yield strobe.i2.eq(0x33)
        yield strobe.i3.eq(0x44)

        for _ in range(100):
            yield Tick()
            yield Settle()

        yield strobe.i0.eq(0x66)
        yield strobe.i1.eq(0x77)
        yield strobe.i2.eq(0x88)
        yield strobe.i3.eq(0x99)

        for _ in range(100):
            yield Tick()
            yield Settle()

    def proc():
        yield from strobe_ut(dut)

    sim = Simulator(dut)
    sim.add_clock(1e-6)
    sim.add_sync_process(proc)

    with sim.write_vcd("../sim/strobe.vcd", 'w'):
        sim.run()


