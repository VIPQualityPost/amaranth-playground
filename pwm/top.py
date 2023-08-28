from amaranth import *
from amaranth.sim import *

class PWM(Elaboratable):
    def elaborate(self, platform):
        m = Module()

        if platform is None:
            ta = Signal(1)
            m.d.sync += ta.eq(~ta)

        self.dutycycle = Signal(8, reset = 0)
        self.counter = Signal(8, reset = 0)
        self.output = Signal(1)

        with m.If(self.counter < self.dutycycle):
            m.d.sync += [
                self.counter.eq(self.counter + 1),
                self.output.eq(1)
                ]
        with m.Else():
            m.d.sync += [
                self.counter.eq(self.counter + 1),
                self.output.eq(0)
                ]
        
        return m

dut = PWM()

def pwm_ut(pwm, duty):
    yield pwm.dutycycle.eq(duty)
    for _ in range(255):
        yield Tick()
        yield Settle()

def proc():
    for duty in range(255):
        yield from pwm_ut(dut, duty)

if __name__ == "__main__":
    sim = Simulator(dut)
    sim.add_clock(1e-6)
    sim.add_sync_process(proc)

    with sim.write_vcd("pwm.vcd", 'w'):
        sim.run()