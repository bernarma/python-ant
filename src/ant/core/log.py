# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2020, Martín Raúl Villalba
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
##############################################################################

import time
import datetime
import msgpack

EVENT_OPEN = 0x01
EVENT_CLOSE = 0x02
EVENT_READ = 0x03
EVENT_WRITE = 0x04


class LogReader():
    '''Log Reader. '''
    def __init__(self, filename):
        self.is_open = False
        self.open(filename)

    def __del__(self):
        if self.is_open:
            self.fd.close()

    def open(self, filename):
        if self.is_open is True:
            self.close()

        self.fd = open(filename, 'rb')
        self.is_open = True
        self.unpacker = msgpack.Unpacker()

        self.unpacker.feed(self.fd.read())
        self.fd.close()

        header = self.unpacker.unpack()
        if len(header) != 2 or header[0] != b'ANT-LOG' or header[1] != 0x01:
            raise IOError('Could not open log file (unknown format).')

    def close(self):
        if self.is_open:
            self.fd.close()
            self.is_open = False

    def read(self):
        try:
            return self.unpacker.unpack()
        except msgpack.exceptions.UnpackException:
            return None


class LogWriter():
    '''Log Writer. '''
    def __init__(self, filename=''):
        self.packer = msgpack.Packer()
        self.is_open = False
        self.open(filename)

    def __del__(self):
        if self.is_open:
            self.fd.close()

    def open(self, filename=''):
        if filename == '':
            filename = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.ant'
        self.filename = filename

        if self.is_open is True:
            self.close()

        self.fd = open(filename, 'wb')
        self.is_open = True
        self.packer = msgpack.Packer()

        header = [b'ANT-LOG', 0x01]  # [MAGIC, VERSION]
        self.fd.write(self.packer.pack(header))

    def close(self):
        if self.is_open:
            self.fd.close()
            self.is_open = False

    def _logEvent(self, event, data=None):
        ev = [event, int(time.time()), data]

        if data is None:
            ev = ev[0:-1]
        elif len(data) == 0:
            return

        self.fd.write(self.packer.pack(ev))

    def logOpen(self):
        self._logEvent(EVENT_OPEN)

    def logClose(self):
        self._logEvent(EVENT_CLOSE)

    def logRead(self, data):
        self._logEvent(EVENT_READ, data)

    def logWrite(self, data):
        self._logEvent(EVENT_WRITE, data)
