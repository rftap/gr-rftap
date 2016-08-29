#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2016 Jonathan Brucker <jonathan.brucke@gmail.com>
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

import time
import pmt
from gnuradio import gr, gr_unittest
from gnuradio import blocks
from rftap_encap import rftap_encap

class qa_rftap_encap (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        # set up data
        srcdata = (1L, 2L, 3L)
        meta = pmt.to_pmt({'dissector': 'rds'})
        srcpdu = pmt.cons(meta, pmt.init_u8vector(len(srcdata), srcdata))
        outdata = (82L, 70L, 116L, 97L, 4L, 0L, 0L, 0L, 16L, 0L, 3L, 255L, 114L, 100L, 115L, 0L) + srcdata
        outpdu = pmt.cons(meta, pmt.init_u8vector(len(outdata), outdata))

        # set up flowgraph
        encap = rftap_encap(1, -1, "")
        sink = blocks.message_debug()
        tb = gr.top_block()
        tb.msg_connect(encap, "out", sink, "store")

        # run flowgraph
        tb.start()
        t = time.time();
        encap.to_basic_block()._post(pmt.intern("in"), srcpdu)
        while time.time()-t < 2:  # timeout
            if sink.num_messages() > 0: break  # got msg
            time.sleep(0.1)
        tb.stop()
        tb.wait()

        # check data
        recpdu = sink.get_message(0)
        #print 'expected:', pmt.u8vector_elements(pmt.cdr(outpdu))
        #print 'actual  :', pmt.u8vector_elements(pmt.cdr(recpdu))
        self.assertTrue(pmt.equal(recpdu, outpdu))

if __name__ == '__main__':
    gr_unittest.run(qa_rftap_encap, "qa_rftap_encap.xml")  # runs test twice :(
    #gr_unittest.run(qa_rftap_encap)
