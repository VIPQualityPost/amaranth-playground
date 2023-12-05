from amaranth import *
from amaranth.lib import data

class DoubleDabble(Elaboratable):
    def __init__(self):
        # Ports
        self.i = Signal(6)
        self.outLo = Signal(4)
        self.outHi = Signal(4)

        # State
        self.done = Signal(1, reset = 0)

    def elaborate(self, platform):
        m = Module()

        scratchpad_layout = data.StructLayout({
            "base": 6, 
            "low": 4, 
            "high": 4
        })

        scratchpad_bits = Signal(scratchpad_layout)
        scratchpad = data.View(scratchpad_layout, scratchpad_bits)

        prevInput = Signal(6)
        shifts = Signal(3)

        addOnes = Signal(1)
        addTens = Signal(1)

        with m.If(self.done == 0):

            with m.If(prevInput != self.i):
                m.d.sync += [
                    shifts.eq(0),
                    prevInput.eq(self.i),
                    scratchpad.eq(self.i)]

            with m.Else():
                with m.If(shifts < 6):
                    with m.If(addOnes == 0):
                        with m.If(scratchpad.low > 4):
                            m.d.sync += [
                                addOnes.eq(1),
                                scratchpad.eq(scratchpad.as_value() + (3 << 6))]
                        with m.Else():
                            m.d.sync += addOnes.eq(1)
                            
                    with m.Elif(addTens == 0):
                        with m.If(scratchpad.high > 4):
                            m.d.sync += [
                                addTens.eq(1),
                                scratchpad.eq(scratchpad.as_value() + (3 << 10))]
                        with m.Else():
                            m.d.sync += addTens.eq(1)
                            
                    with m.Else():
                        m.d.sync += [
                            addOnes.eq(0),
                            addTens.eq(0),
                            shifts.eq(shifts + 1),
                            scratchpad.eq(scratchpad.as_value() << 1)]

                with m.Else():
                    m.d.sync +=[
                        shifts.eq(0),
                        self.done.eq(1),
                        self.outLo.eq(scratchpad.low),
                        self.outHi.eq(scratchpad.high)]

        with m.Else():
            with m.If(prevInput != self.i):
                m.d.sync += [
                    self.done.eq(0)]

        return m

if __name__ == "__main__":
    from amaranth.sim import *

    dut = DoubleDabble()

    def dd_ut(bcd, bin):
        convDone = 0
        yield bcd.i.eq(bin)

        while convDone == 0:
            yield Tick()
            yield Settle()
            convDone = yield bcd.done

        yield Tick()
        yield Settle()

        tens = yield bcd.outHi
        ones = yield bcd.outLo

        if ((tens * 10) + ones) != bin: 
            print("BCD conversion failed with input %s: output %s%s" %(bin, tens, ones))

    def proc():
        for _ in range(60):
            yield from dd_ut(dut, _)

    sim = Simulator(dut)
    sim.add_clock(1e-6)
    sim.add_sync_process(proc)

    with sim.write_vcd("../sim/doubledabble.vcd", 'w'):
        sim.run()


