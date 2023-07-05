from amaranth import *
from amaranth.sim import *
from amaranth_soc.memory import *
from amaranth_soc.wishbone import *
from math import ceil, log2

class ROM(Elaboratable, Interface):
    def __init__(self, data):
        #ROM interface
        self.size = len(data)
        self.data = Memory(width = 32, depth = self.size, init = data)
        self.r = self.data.read_port()

        # Wishbone interface
        Interface.__init__( self, 
                            data_width = 32, 
                            addr_width = ceil(log2(self.size+1)))
        
        self.memory_map = MemoryMap(    data_width = self.data_width,
                                        addr_width = self.addr_width,
                                        alignment = 0)

    def elaborate(self, platform):
        m = Module()

        if platform is None:
            ta = Signal()
            m.d.sync += ta.eq(~ta)

        # Register the read port submodule
        m.submodules.r = self.r

        # Ack rest low
        m.d.sync += self.ack.eq(0)

        # Once cyc & stb asserted, then we acknowledge read.
        with m.If(self.cyc):
            m.d.sync += self.ack.eq(self.stb)

        # Actually read the data.
        m.d.comb+=[
            self.r.addr.eq(self.adr),
            self.dat_r.eq(self.r.data)
        ]

        return m

## TESTS ##
p = 0
f = 0

# Sample data
dut = ROM([ 0x01234567, 
            0x89ABCDEF, 
            0xCC00FFEE, 
            0xDEADBEEF, 
            0xDECAFC0F])

# Unit test
def rom_ut(rom, address, expected):
    global p, f
    yield rom.adr.eq(address)
    yield Tick()    # This advances the clock
    yield Settle()  # This waits for the read comb logic to settle.

    actual = yield rom.dat_r 

    if(actual == expected):
        print("PASS: Memory[0x%04X] = 0x%08X" %(expected, actual))
        p += 1
    else:
        print("FAIL: Memory[0x%04X] = 0x%08X" %(expected, actual))
        f += 1
    
# Full test
def rom_test(rom):
    yield from rom_ut(rom, 0, 0x01234567)
    yield from rom_ut(rom, 1, 0x89ABCDEF)
    yield from rom_ut(rom, 2, 0xCC00FFEE)
    yield from rom_ut(rom, 3, 0xDEADBEEF)
    yield from rom_ut(rom, 4, 0xDECAFC0F)
    print("Passes: %d, Fails: %d" %(p, f))

def proc():
    yield from rom_test(dut)

# Run test if module run independently
if __name__ == "__main__":
    sim = Simulator(dut)
    sim.add_clock(1e-6)
    sim.add_sync_process(proc)
    
    with sim.write_vcd("rom.vcd",'w'):
        sim.run()



