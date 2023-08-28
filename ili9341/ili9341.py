from amaranth import *
from amaranth.sim import *
from amaranth_soc.memory import *
from amaranth_soc.wishbone import *
from math import ceil, log2
import sys

class SPI(Elaboratable, Interface):
    def __init__(self, data):
        self.size = len(data)
        self.data = Memory(width = 16, depth = self.size, init = data)
        self.r = self.data.read_port()

    def elaborate(self, platform):
        m = Module()

        if platform is None:
            # ta = Signal(1)
            # m.d.sync += ta.eq(~ta)
            clockdiv = 1
        else:
            clockdiv = int(platform.default_clk_frequency/5) #200kHz

        self.cs = Signal(1, reset = 0)
        self.dc = Signal(1, reset = 0)
        self.scl = Signal(1, reset = 0)
        self.copi = Signal(1, reset = 0)
        self.buffer = Signal(16, reset = 0)
        self.periphclock = Signal(range(clockdiv +1))
        self.bytecounter = Signal(4, reset = 0x0)

        m.submodules.r = self.r 

        # See if we need to load a new half-word
        with m.If(self.bytecounter ==  0):
            m.d.sync += [
                self.buffer.eq(self.r.data)
            ]

        # When subclock timer is full
        with m.If(self.periphclock == clockdiv):

            # Make new clock edge
            m.d.sync +=[
                self.scl.eq(~self.scl),
                self.periphclock.eq(0)            
                ]

            # Do logic after clock high
            with m.If(self.scl == 1):
                m.d.sync+=[
                    # Write the LSB of buffer.
                    self.copi.eq(self.buffer[:1]),
                    # Stop the DC pulse if happening.
                ]

                m.d.sync += [
                    # Shift out the last bit.
                    self.buffer.eq(self.buffer >> 1),
                    # Increment the half-word counter
                    self.bytecounter.eq(self.bytecounter + 1)
                ]

                with m.Switch(self.bytecounter):
                    with m.Case(0x7):
                        m.d.sync += self.dc.eq(1)

                    with m.Case(0xF):
                        m.d.sync += self.dc.eq(1)

                    with m.Default():
                        m.d.sync += self.dc.eq(0)

            with m.If(self.bytecounter == 0xF):
                with m.If(self.scl == 1):
                    m.d.sync += [
                        self.r.addr.eq(self.r.addr + 1)
                    ]
                        
        with m.Else():
            m.d.sync += self.periphclock.eq(self.periphclock + 1)
            # How to tell if we are done with the data? 
        return m 

## TESTS
p = 0 
f = 0

# Sample data
data = [0xAAAA, 0xFFFF, 0xDEAD, 0xBEEF]
dut = SPI(data)

# Unit test
def spi_ut(rom):
    for _ in range(sys.getsizeof(data)*2):
        yield Tick()
        yield Settle()

# Full test

def proc():
    yield from spi_ut(dut)

if __name__ == "__main__":
    sim = Simulator(dut)
    sim.add_clock(1e-6)
    sim.add_sync_process(proc)

    with sim.write_vcd("ili9341.vcd", 'w'):
        sim.run()