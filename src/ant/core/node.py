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

"""Node Module
"""

import time
import uuid
import _thread

import ant.core.constants as msgtypes
import ant.core.exceptions as antex
import ant.core.message as antmsg
import ant.core.event as antevt


class NetworkKey():
    '''Network Key (ANT+ Doco) '''
    def __init__(self, name=None, key=b'\x00' * 8):
        self._key = key
        if name:
            self._name = name
        else:
            self._name = str(uuid.uuid4())
        self._number = 0

    @property
    def key(self):
        return self._key

    @property
    def name(self):
        return self._name

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, number):
        self._number = number


class Channel(antevt.EventCallback):
    '''A channel is used to connect two nodes together. '''
    cb_lock = _thread.allocate_lock()

    def __init__(self, node):
        self.node = node
        self.is_free = True
        self.name = str(uuid.uuid4())
        self.number = 0
        self.callback = []
        self.node.evm.registerCallback(self)

    def __del__(self):
        self.node.evm.removeCallback(self)

    def assign(self, net_key, ch_type):
        msg = antmsg.ChannelAssignMessage(number=self.number)
        msg.setNetworkNumber(self.node.getNetworkKey(net_key).number)
        msg.setChannelType(ch_type)
        self.node.driver.write(msg.encode())
        if self.node.evm.waitForAck(msg) != msgtypes.RESPONSE_NO_ERROR:
            raise antex.ChannelError('Could not assign channel.')
        self.is_free = False

    def setID(self, dev_type, dev_num, trans_type):
        msg = antmsg.ChannelIDMessage(number=self.number)
        msg.setDeviceType(dev_type)
        msg.setDeviceNumber(dev_num)
        msg.setTransmissionType(trans_type)
        self.node.driver.write(msg.encode())
        if self.node.evm.waitForAck(msg) != msgtypes.RESPONSE_NO_ERROR:
            raise antex.ChannelError('Could not set channel ID.')

    def setSearchTimeout(self, timeout):
        msg = antmsg.ChannelSearchTimeoutMessage(number=self.number)
        msg.setTimeout(timeout)
        self.node.driver.write(msg.encode())
        if self.node.evm.waitForAck(msg) != msgtypes.RESPONSE_NO_ERROR:
            raise antex.ChannelError('Could not set channel search timeout.')

    def setPeriod(self, counts):
        msg = antmsg.ChannelPeriodMessage(number=self.number)
        msg.setChannelPeriod(counts)
        self.node.driver.write(msg.encode())
        if self.node.evm.waitForAck(msg) != msgtypes.RESPONSE_NO_ERROR:
            raise antex.ChannelError('Could not set channel period.')

    def setFrequency(self, frequency):
        msg = antmsg.ChannelFrequencyMessage(number=self.number)
        msg.setFrequency(frequency)
        self.node.driver.write(msg.encode())
        if self.node.evm.waitForAck(msg) != msgtypes.RESPONSE_NO_ERROR:
            raise antex.ChannelError('Could not set channel frequency.')

    def open(self):
        msg = antmsg.ChannelOpenMessage(number=self.number)
        self.node.driver.write(msg.encode())
        if self.node.evm.waitForAck(msg) != msgtypes.RESPONSE_NO_ERROR:
            raise antex.ChannelError('Could not open channel.')

    def close(self):
        msg = antmsg.ChannelCloseMessage(number=self.number)
        self.node.driver.write(msg.encode())
        if self.node.evm.waitForAck(msg) != msgtypes.RESPONSE_NO_ERROR:
            raise antex.ChannelError('Could not close channel.')

        while True:
            msg = self.node.evm.waitForMessage(antmsg.ChannelEventMessage)
            if msg.getMessageCode() == msgtypes.EVENT_CHANNEL_CLOSED:
                break

    def unassign(self):
        msg = antmsg.ChannelUnassignMessage(number=self.number)
        self.node.driver.write(msg.encode())
        if self.node.evm.waitForAck(msg) != msgtypes.RESPONSE_NO_ERROR:
            raise antex.ChannelError('Could not unassign channel.')
        self.is_free = True

    def registerCallback(self, callback):
        self.cb_lock.acquire()
        if callback not in self.callback:
            self.callback.append(callback)
        self.cb_lock.release()

    def process(self, msg):
        self.cb_lock.acquire()
        if isinstance(msg, antmsg.ChannelMessage) and \
           msg.getChannelNumber() == self.number:
            for callback in self.callback:
                try:
                    callback.process(msg)
                except antex.CallbackError:
                    pass  # Who cares?
        self.cb_lock.release()


class Node(antevt.EventCallback):
    '''Represents a node in an ANT network. '''
    node_lock = _thread.allocate_lock()

    def __init__(self, driver):
        self.driver = driver
        self.evm = antevt.EventMachine(self.driver)
        self.evm.registerCallback(self)
        self.networks = []
        self.channels = []
        self.running = False
        self.options = [0x00, 0x00, 0x00]

    def start(self):
        if self.running:
            raise antex.NodeError('Could not start ANT node (already started).')

        if not self.driver.isOpen():
            self.driver.open()

        self.reset()
        self.evm.start()
        self.running = True
        self.init()

    def stop(self, reset=True):
        if not self.running:
            raise antex.NodeError('Could not stop ANT node (not started).')

        if reset:
            self.reset()
        self.evm.stop()
        self.running = False
        self.driver.close()

    def reset(self):
        msg = antmsg.SystemResetMessage()
        self.driver.write(msg.encode())
        time.sleep(1)

    def init(self):
        if not self.running:
            raise antex.NodeError('Could not reset ANT node (not started).')

        msg = antmsg.ChannelRequestMessage()
        msg.setMessageID(msgtypes.MESSAGE_CAPABILITIES)
        self.driver.write(msg.encode())

        caps = self.evm.waitForMessage(antmsg.CapabilitiesMessage)

        self.networks = []
        for i in range(0, caps.getMaxNetworks()):
            self.networks.append(NetworkKey())
            self.setNetworkKey(i)
        self.channels = []
        for i in range(0, caps.getMaxChannels()):
            self.channels.append(Channel(self))
            self.channels[i].number = i
        self.options = (caps.getStdOptions(),
                        caps.getAdvOptions(),
                        caps.getAdvOptions2(),)

    def getCapabilities(self):
        return (len(self.channels),
                len(self.networks),
                self.options,)

    def setNetworkKey(self, number, key=None):
        if key:
            self.networks[number] = key

        msg = antmsg.NetworkKeyMessage()
        msg.setNumber(number)
        msg.setKey(self.networks[number].key)
        self.driver.write(msg.encode())
        self.evm.waitForAck(msg)
        self.networks[number].number = number

    def getNetworkKey(self, name):
        for netkey in self.networks:
            if netkey.name == name:
                return netkey
        raise antex.NodeError('Could not find network key with the '
                              'supplied name.')

    def getFreeChannel(self):
        for channel in self.channels:
            if channel.is_free:
                return channel
        raise antex.NodeError('Could not find free channel.')

    def registerEventListener(self, callback):
        self.evm.registerCallback(callback)

    def process(self, msg):
        pass
