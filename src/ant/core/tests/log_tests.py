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

import os
import tempfile
import unittest
import ant.core.log as log

LOG_LOCATION = ''.join([tempfile.gettempdir(), os.path.sep,
                        'python-ant.logtest.ant'])


class LogReaderTest(unittest.TestCase):
    def setUp(self):
        lw = log.LogWriter(LOG_LOCATION)
        lw.logOpen()
        lw.logRead(b'\x01')
        lw.logWrite(b'\x00')
        lw.logRead(b'TEST')
        lw.logClose()
        lw.close()

        self.log = log.LogReader(LOG_LOCATION)

    def test_open_close(self):
        self.assertTrue(self.log.is_open)
        self.log.close()
        self.assertFalse(self.log.is_open)
        self.log.open(LOG_LOCATION)
        self.assertTrue(self.log.is_open)

    def test_read(self):
        t1 = self.log.read()
        t2 = self.log.read()
        t3 = self.log.read()
        t4 = self.log.read()
        t5 = self.log.read()

        self.assertEqual(self.log.read(), None)

        self.assertEqual(t1[0], log.EVENT_OPEN)
        self.assertTrue(isinstance(t1[1], int))
        self.assertEqual(len(t1), 2)

        self.assertEqual(t2[0], log.EVENT_READ)
        self.assertTrue(isinstance(t1[1], int))
        self.assertEqual(len(t2), 3)
        self.assertEqual(t2[2], b'\x01')

        self.assertEqual(t3[0], log.EVENT_WRITE)
        self.assertTrue(isinstance(t1[1], int))
        self.assertEqual(len(t3), 3)
        self.assertEqual(t3[2], b'\x00')

        self.assertEqual(t4[0], log.EVENT_READ)
        self.assertEqual(t4[2], b'TEST')

        self.assertEqual(t5[0], log.EVENT_CLOSE)
        self.assertTrue(isinstance(t1[1], int))
        self.assertEqual(len(t5), 2)


class LogWriterTest(unittest.TestCase):
    def setUp(self):
        self.log = log.LogWriter(LOG_LOCATION)

    def test_open_close(self):
        self.assertTrue(self.log.is_open)
        self.log.close()
        self.assertFalse(self.log.is_open)
        self.log.open(LOG_LOCATION)
        self.assertTrue(self.log.is_open)

    def test_log(self):
        # Redundant, any error in log* methods will cause the LogReader test
        # suite to fail.
        pass
