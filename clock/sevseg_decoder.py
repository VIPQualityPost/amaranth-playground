from amaranth import *

class SevSegDecoder(Elaboratable):
    def __init__(self):
        # Ports
        self.i = Signal(4)
        self.o = Signal(7)

        self.en = Signal(1)
        
    def elaborate(self, platform):
        m = Module()

        o = self.o

        #    A
        #    _ 
        # F |_| B
        # E |_| C
        #    D
        # G inside
        
        if(platform == None):
            ta = Signal(1)
            m.d.sync += ta.eq(~ta)

        with m.Switch(self.i):
            with m.Case(0x0):
                m.d.comb += o.eq(0b1111110)
        
            with m.Case(0x1):
                m.d.comb += o.eq(0b0110000)

            with m.Case(0x2):
                m.d.comb += o.eq(0b1101101)

            with m.Case(0x3):
                m.d.comb += o.eq(0b1111001)

            with m.Case(0x4):
                m.d.comb += o.eq(0b0110011)

            with m.Case(0x5):
                m.d.comb += o.eq(0b1011011)

            with m.Case(0x6):
                m.d.comb += o.eq(0b1011111)

            with m.Case(0x7):
                m.d.comb += o.eq(0b1110000)

            with m.Case(0x8):
                m.d.comb += o.eq(0b1111111)

            with m.Case(0x9):
                m.d.comb += o.eq(0b1111011)

            with m.Case(0xA):
                m.d.comb += o.eq(0b1110111)

            with m.Case(0xB):
                m.d.comb += o.eq(0b0011111)

            with m.Case(0xC):
                m.d.comb += o.eq(0b1001110)

            with m.Case(0xD):
                m.d.comb += o.eq(0b0111101)

            with m.Case(0xE):
                m.d.comb += o.eq(0b1001111)

            with m.Case(0xF):
                m.d.comb += o.eq(0b1000111)

        return m

if __name__ == "__main__":
    from amaranth.sim import *

    dut = SevSegDecoder()

    def decoder_ut(decoder, i):
        yield decoder.i.eq(i)
        yield Tick()
        yield Settle()

    def proc():
        for i in range(16):
            yield from decoder_ut(dut, i)

    sim = Simulator(dut)
    sim.add_clock(1e-6)
    sim.add_sync_process(proc)

    with sim.write_vcd("./sim/sevseg_decoder.vcd", 'w'):
        sim.run()
