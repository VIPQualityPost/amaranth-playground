from amaranth import *
from amaranth.sim import *
from .rom import *

class Dummy_LED():
    def __init__(self,name):
        self.o = Signal(1, reset = 0b0, name = '%s_o'%name)
    
class Memory_Test(Elaboratable):
    def __init(self,memory):
        self.mem = memory
        self.pc = Signal(self.mem.addr_width, reset = 0)
        self.dc = Signal(28, reset = 0)

    def elaborate(self, platform):
        m = Module()
        m.submodules.mem = self.mem

        if platform is None:
            rled = Dummy_LED('rled')
            gled = Dummy_LED('gled')
            bled = Dummy_LED('bled')
        else:
            rled = platform.request('led_r',0)
            gled = platform.request('led_g',0)
            bled = platform.request('led_b',0)
        
        m.d.comb += self.mem.adr.eq(self.pc)

        with m.FSM():
            with m.State('FETCH'):
                m.d.sync += [
                    self.mem.stb.eq(1),
                    self.mem.cyc.eq(1)]
                with m.If(self.mem.ack == 1):
                    m.d.sync +=[
                        self.mem.stb.eq(0),
                        self.mem.cyc.eq(0),
                        self.dc.eq(0)
                    ]
                    m.next('PROCESS')
            
            with m.State('PROCESS'):
                m.d.sync += self.pc.eq(self.pc + 1)
                m.next('FETCH')

                with m.If(self.mem.dat_r == 0x00000000 | self.mem.dat_r == 0xFFFFFFFF):
                    m.d.sync += self.pc.eq(0)

                with m.Elif(self.mem.dat_r[:4] == 4):
                    with m.If(self.dc != (self.mem.dat_r >> 4)):
                        m.d.sync += [
                            self.pc.eq(self.pc)
                            self.dc.eq(self.dc +1)
                        ]
                        m.next('PROCESS')
                    
                    with m.Elif(self.mem.dat_r[:3] == 3):
                        m.d.sync += bled.o.eq(self.mem.dat_r[3])
                    with m.Elif(self.mem.dat_r[:3] == 2):
                        m.d.sync += gled.o.eq(self.mem.dat_r[3])
                    with m.Elif(self.mem.dat_r[:3] == 1):
                        m.d.sync += rled.o.eq(self.mem.dat_r[3])
        return m 

## TESTS ##

dut = Memory_Test()

def mem_ut():

def mem_test():

def proc:
    yield from mem_test(dut)

# Run test if module run independently
if __name__ == "__main__":
    sim = Simulator(dut)
    sim.add_clock(1e-6)
    sim.add_sync_process(proc)
    
    with sim.write_vcd("mem.vcd",'w'):
        sim.run()