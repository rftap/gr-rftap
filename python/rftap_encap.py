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

import array
import struct
import numpy
import pmt
from gnuradio import gr

class rftap_encap(gr.basic_block):
    """
    add a rftap header to PDUs, see https://rftap.github.io/
    """

    PMT_IN = pmt.intern('in')
    PMT_OUT = pmt.intern('out')

    def __init__(self, encapsulation_from, custom_dlt, custom_dissector_name):
        gr.basic_block.__init__(self,
            name="rftap_encap",
            in_sig=[],
            out_sig=[])

        self.encapsulation_from = encapsulation_from
        self.custom_dlt = custom_dlt
        self.custom_dissector_name = custom_dissector_name

        self.message_port_register_in(self.PMT_IN)
        self.set_msg_handler(self.PMT_IN, self.handle_msg)

        self.message_port_register_out(self.PMT_OUT)

    def handle_msg(self, pdu):
        if not pmt.is_pair(pdu):
            print("rftap_encap: error: received invalid message type (not pair)", pdu)
            return

        d = pmt.to_python(pmt.car(pdu))  # metadata (dict)
        vec = pmt.to_python(pmt.cdr(pdu))  # data (u8 vector (numpy))

        if not d: d = {}  # fix for pmt.to_python(pmt.to_pmt({})) returning None...

        if not isinstance(d, dict):
            print("rftap_encap: error: unexpected metadata type (not dict)", pdu, repr(d))
            return

        if not isinstance(vec, numpy.ndarray) or not vec.dtype==numpy.dtype('uint8'):
            print("rftap_encap: error: unexpected PDU data type (not ndarray uint8)", pdu, repr(v))
            return

        vec = vec.tostring()  # aka tobytes() (numpy1.9+)

        flags = 0

        b = array.array('B')
        hdr = struct.pack('<4sHH', b'RFta', 0, 0)  # len, flags written below
        b.fromstring(hdr)

        # this should be done in order of the bitfield:

        # dlt from PDU
        if self.encapsulation_from == 0:
            if 'dlt' not in d:
                print("[ERROR] dlt is expected in PDU, but it is missing")
            else:
                val = d.get('dlt')
                if not isinstance(val, int):
                    print("[ERROR] dlt in PDU is not an integer:", repr(val))
                else:
                    b.fromstring(struct.pack('<I', val))
                    flags |= 1
        # custom dlt
        elif self.encapsulation_from == 2:
            val = self.custom_dlt
            if not isinstance(val, int):
                print("[ERROR] custom dlt is not an integer:", repr(val))
            else:
                b.fromstring(struct.pack('<I', val))
                flags |= 1

        if 'freq' in d:
            val = d.get('freq')
            if not isinstance(val, (float,int)):
                print("[ERROR] freq is not a number:", repr(val))
            else:
                b.fromstring(struct.pack('<d', val))
                flags |= (1<<1)

        if 'nomfreq' in d:
            val = d.get('nomfreq')
            if not isinstance(val, (float,int)):
                print("[ERROR] nomfreq is not a number:", repr(val))
            else:
                b.fromstring(struct.pack('<d', val))
                flags |= (1<<2)

        if 'freqofs' in d:
            val = d.get('freqofs')
            if not isinstance(val, (float,int)):
                print("[ERROR] freqofs is not a number:", repr(val))
            else:
                b.fromstring(struct.pack('<d', val))
                flags |= (1<<3)

        if 'power' in d:
            val = d.get('power')
            if not isinstance(val, (float,int)):
                print("[ERROR] power is not a number:", repr(val))
            else:
                b.fromstring(struct.pack('<f', val))
                flags |= (1<<5)

        if 'noise' in d:
            val = d.get('noise')
            if not isinstance(val, (float,int)):
                print("[ERROR] noise is not a number:", repr(val))
            else:
                b.fromstring(struct.pack('<f', val))
                flags |= (1<<6)

        if 'snr' in d:
            val = d.get('snr')
            if not isinstance(val, (float,int)):
                print("[ERROR] snr is not a number:", repr(val))
            else:
                b.fromstring(struct.pack('<f', val))
                flags |= (1<<7)

        if 'qual' in d:
            val = d.get('qual')
            if not isinstance(val, (float,int)):
                print("[ERROR] qual is not a number:", repr(val))
            else:
                b.fromstring(struct.pack('<f', val))
                flags |= (1<<8)

        # tagged parameters:

        # dissector name from PDU
        if self.encapsulation_from == 1:
            if 'dissector' not in d:
                print("[ERROR] dissector name is expected in PDU, but it is missing")
            else:
                val = d.get('dissector')
                if not isinstance(val, str):
                    print("[ERROR] dissector name in PDU is not a string:", repr(val))
                else:
                    val = val.encode()
                    b.fromstring(struct.pack('<HBB', 16, len(val), 255))
                    b.fromstring(val)
                    padlen = 3 - ((len(val)+3)&3)
                    b.fromstring(b'\0'*padlen)
        # custom dissector name
        elif self.encapsulation_from == 3:
            val = self.custom_dissector_name
            if not isinstance(val, str):
                print("[ERROR] custom dissector name is not a string:", repr(val))
            else:
                val = val.encode()
                b.fromstring(struct.pack('<HBB', 16, len(val), 255))
                b.fromstring(val)
                padlen = 3 - ((len(val)+3)&3)
                b.fromstring(b'\0'*padlen)

        if len(b) % 4 != 0:
            print("[ERROR] wrong padding!!!")

        struct.pack_into('<H', b, 4, len(b)//4)
        struct.pack_into('<H', b, 6, flags)

        b.fromstring(vec)

        pmt_v = pmt.init_u8vector(len(b), b)
        outpdu = pmt.cons(pmt.car(pdu), pmt_v)
        self.message_port_pub(self.PMT_OUT, outpdu)
