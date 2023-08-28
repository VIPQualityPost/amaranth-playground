from amaranth import *
from amaranth.sim import *
from .alchitry_cu import *

class SevenSegCounter(Elaboratable):
    def __init__(self, number, ):
        self.data

    def elaborate(self, platform):
        m = module()


        return m

# Unit test
def spi_ut(rom):
    yield Tick()
    yield Settle()

# Full test
def proc():
    for _ in range(150):
        yield from spi_ut(dut)

if __name__ == "__main__":
    sim = Simulator(dut)
    sim.add_clock(1e-6)
    sim.add_sync_process(proc)

    with sim.write_vcd("spi.vcd", 'w'):
        sim.run()