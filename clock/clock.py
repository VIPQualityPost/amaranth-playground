from amaranth import *

from doubledabble import DoubleDabble
from sevseg_decoder import SevSegDecoder

class SixDigitClock(Elaboratable):
    def __init__(self):
        # Ports
        self.hours = Signal(4)
        self.minutes = Signal(4)
        self.seconds = Signal(4)
        self.hzclk = Signal()

        self.h1 = SevSegDecoder()
        self.h2 = SevSegDecoder()

        self.m1 = SevSegDecoder()
        self.m2 = SevSegDecoder()
    
        self.s1 = SevSegDecoder()
        self.s2 = SevSegDecoder()

        # State
        self.rst = Signal()
        self.en = Signal()

    def elaborate(self, platform):
        m = Module()

        hours = self.hours
        minutes = self.minutes
        seconds = self.seconds
        lastclk = Signal()

        m.submodules.h_bcd = h_bcd = DoubleDabble()
        m.submodules.m_bcd = m_bcd = DoubleDabble()
        m.submodules.s_bcd = s_bcd =  DoubleDabble()

        m.submodules.h1 = h1 = self.h1 
        m.submodules.h2 = h2 = self.h2 
        m.submodules.m1 = m1 = self.m1
        m.submodules.m2 = m2 = self.m2
        m.submodules.s1 = s1 = self.s1
        m.submodules.s2 = s2 = self.s2

        with m.If(self.hzclk != lastclk):
            m.d.comb += lastclk.eq(self.hzclk)
            m.d.sync += seconds.eq(seconds + 1)

            with m.If(seconds > 59):
                m.d.sync += [
                    seconds.eq(0),
                    minutes.eq(minutes + 1)]

                with m.If(minutes > 59):
                    m.d.sync += [
                        minutes.eq(0), 
                        hours.eq(hours + 1)]

                    with m.If(hours > 11):
                        m.d.sync += [
                            hours.eq(0)]

        m.d.sync += [
            h_bcd.i.eq(hours + 1),
            m_bcd.i.eq(minutes),
            s_bcd.i.eq(seconds),
            h1.i.eq(h_bcd.outHi),
            h2.i.eq(h_bcd.outLo),
            m1.i.eq(m_bcd.outHi),
            m2.i.eq(m_bcd.outLo),
            s1.i.eq(s_bcd.outHi),
            s1.i.eq(s_bcd.outLo)]

        return m