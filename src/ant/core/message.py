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

"""Message Module
"""

import struct

import ant.core.exceptions as antex
import ant.core.constants as msgtypes


class Message():
    '''Represents an ANT message as defined in the ANT Message Protocol Specification.
    '''

    def __init__(self, type_=0x00, payload=b''):
        """Initialises the ANT message with an empty payload.
        """
        self.setType(type_)
        self.setPayload(payload)

    def getPayload(self):
        """Returns the payload associated with the ANT message.
        """
        return b''.join(self.payload)

    def setPayload(self, payload):
        if len(payload) > 9:
            raise antex.MessageError(
                'Could not set payload (payload too long).')

        self.payload = [b'%c' % i for i in payload]

    def getType(self):
        """Returns the type of ANT message.
        """
        return self.type_

    def setType(self, type_):
        if (type_ > 0xFF) or (type_ < 0x00):
            raise antex.MessageError('Could not set type (type out of range).')

        self.type_ = type_

    def getChecksum(self):
        """Computes the checksum for the ANT message.
        """
        data = bytes([len(self.getPayload())])
        data += bytes([self.getType()])
        data += self.getPayload()

        checksum = msgtypes.MESSAGE_TX_SYNC
        for byte in data:
            checksum = (checksum ^ byte) % 0xFF

        return checksum

    def getSize(self):
        """Returns the length of the ANT message.
        """
        return len(self.getPayload()) + 4

    def encode(self):
        """Returns a byte stream representing the ANT message.
        """
        raw = struct.pack('BBB',
                          msgtypes.MESSAGE_TX_SYNC,
                          len(self.getPayload()),
                          self.getType())
        raw += self.getPayload()
        raw += bytes([self.getChecksum()])

        return raw

    def decode(self, raw):
        """Decodes a raw sequence of bytes into an ANT message.
        """
        if len(raw) < 5:
            raise antex.MessageError('Could not decode (message is incomplete).')

        sync, length, type_ = struct.unpack('BBB', raw[:3])

        if sync != msgtypes.MESSAGE_TX_SYNC:
            raise antex.MessageError('Could not decode (expected TX sync).')
        if length > 9:
            raise antex.MessageError('Could not decode (payload too long).')
        if len(raw) < (length + 4):
            raise antex.MessageError('Could not decode (message is incomplete).')

        self.setType(type_)
        self.setPayload(raw[3:length + 3])

        if self.getChecksum() != raw[length + 3]:
            raise antex.MessageError('Could not decode (bad checksum).',
                                     internal='CHECKSUM')

        return self.getSize()

    def getHandler(self, raw=None):
        """Returns an typed object based on the raw payload.
        """
        if raw:
            self.decode(raw)

        msg = None
        if self.type_ == msgtypes.MESSAGE_CHANNEL_UNASSIGN:
            msg = ChannelUnassignMessage()
        elif self.type_ == msgtypes.MESSAGE_CHANNEL_ASSIGN:
            msg = ChannelAssignMessage()
        elif self.type_ == msgtypes.MESSAGE_CHANNEL_ID:
            msg = ChannelIDMessage()
        elif self.type_ == msgtypes.MESSAGE_CHANNEL_PERIOD:
            msg = ChannelPeriodMessage()
        elif self.type_ == msgtypes.MESSAGE_CHANNEL_SEARCH_TIMEOUT:
            msg = ChannelSearchTimeoutMessage()
        elif self.type_ == msgtypes.MESSAGE_CHANNEL_FREQUENCY:
            msg = ChannelFrequencyMessage()
        elif self.type_ == msgtypes.MESSAGE_CHANNEL_TX_POWER:
            msg = ChannelTXPowerMessage()
        elif self.type_ == msgtypes.MESSAGE_NETWORK_KEY:
            msg = NetworkKeyMessage()
        elif self.type_ == msgtypes.MESSAGE_TX_POWER:
            msg = TXPowerMessage()
        elif self.type_ == msgtypes.MESSAGE_STARTUP:
            msg = StartupMessage()
        elif self.type_ == msgtypes.MESSAGE_SYSTEM_RESET:
            msg = SystemResetMessage()
        elif self.type_ == msgtypes.MESSAGE_CHANNEL_OPEN:
            msg = ChannelOpenMessage()
        elif self.type_ == msgtypes.MESSAGE_CHANNEL_CLOSE:
            msg = ChannelCloseMessage()
        elif self.type_ == msgtypes.MESSAGE_CHANNEL_REQUEST:
            msg = ChannelRequestMessage()
        elif self.type_ == msgtypes.MESSAGE_CHANNEL_BROADCAST_DATA:
            msg = ChannelBroadcastDataMessage()
        elif self.type_ == msgtypes.MESSAGE_CHANNEL_ACKNOWLEDGED_DATA:
            msg = ChannelAcknowledgedDataMessage()
        elif self.type_ == msgtypes.MESSAGE_CHANNEL_BURST_DATA:
            msg = ChannelBurstDataMessage()
        elif self.type_ == msgtypes.MESSAGE_CHANNEL_EVENT:
            msg = ChannelEventMessage()
        elif self.type_ == msgtypes.MESSAGE_CHANNEL_STATUS:
            msg = ChannelStatusMessage()
        elif self.type_ == msgtypes.MESSAGE_VERSION:
            msg = VersionMessage()
        elif self.type_ == msgtypes.MESSAGE_CAPABILITIES:
            msg = CapabilitiesMessage()
        elif self.type_ == msgtypes.MESSAGE_SERIAL_NUMBER:
            msg = SerialNumberMessage()
        else:
            raise antex.MessageError('Could not find message handler '
                                     f'(unknown message type - {self.type_}).')

        msg.setPayload(self.getPayload())
        return msg


class ChannelMessage(Message):
    '''Base class representing messages related to an ANT Channel.
    '''
    def __init__(self, type_, payload=b'', number=0x00):
        Message.__init__(self, type_, b'\x00' + payload)
        self.setChannelNumber(number)

    def getChannelNumber(self):
        return ord(self.payload[0])

    def setChannelNumber(self, number):
        if (number > 0xFF) or (number < 0x00):
            raise antex.MessageError('Could not set channel number (out of range).')

        self.payload[0] = bytes([number])


# Config messages
class ChannelUnassignMessage(ChannelMessage):
    """Configuration: Unassign Channel (0x41)
    """

    def __init__(self, number=0x00):
        ChannelMessage.__init__(self, type_=msgtypes.MESSAGE_CHANNEL_UNASSIGN,
                                number=number)


class ChannelAssignMessage(ChannelMessage):
    """Configuration: Assign Channel (0x42)
    """

    def __init__(self, number=0x00, type_=0x00, network=0x00):
        payload = struct.pack('BB', type_, network)
        ChannelMessage.__init__(self, type_=msgtypes.MESSAGE_CHANNEL_ASSIGN,
                                payload=payload, number=number)

    def getChannelType(self):
        return ord(self.payload[1])

    def setChannelType(self, type_):
        self.payload[1] = bytes([type_])

    def getNetworkNumber(self):
        return ord(self.payload[2])

    def setNetworkNumber(self, number):
        self.payload[2] = bytes([number])


class ChannelIDMessage(ChannelMessage):
    """Configuration: Set Channel ID (0x051)
    """

    def __init__(self, number=0x00, device_number=0x0000, device_type=0x00,
                 trans_type=0x00):
        ChannelMessage.__init__(self, type_=msgtypes.MESSAGE_CHANNEL_ID,
                                payload=b'\x00' * 4, number=number)
        self.setDeviceNumber(device_number)
        self.setDeviceType(device_type)
        self.setTransmissionType(trans_type)

    def getDeviceNumber(self):
        return struct.unpack('<H', b''.join(self.payload[1:3]))[0]

    def setDeviceNumber(self, device_number):
        self.payload[1:3] = [b'%c' % i for i in struct.pack('<H', device_number)]

    def getDeviceType(self):
        return ord(self.payload[3])

    def setDeviceType(self, device_type):
        self.payload[3] = bytes([device_type])

    def getTransmissionType(self):
        return ord(self.payload[4])

    def setTransmissionType(self, trans_type):
        self.payload[4] = bytes([trans_type])


class ChannelPeriodMessage(ChannelMessage):
    """Configuration: Channel Messaging Period (0x43)
    """

    def __init__(self, number=0x00, period=8192):
        ChannelMessage.__init__(self, type_=msgtypes.MESSAGE_CHANNEL_PERIOD,
                                payload=b'\x00' * 2, number=number)
        self.setChannelPeriod(period)

    def getChannelPeriod(self):
        return struct.unpack('<H', b''.join(self.payload[1:3]))[0]

    def setChannelPeriod(self, period):
        self.payload[1:3] = [b'%c' % i for i in struct.pack('<H', period)]


class ChannelSearchTimeoutMessage(ChannelMessage):
    """Configuration: Channel Search Timeout (0x44)
    """

    def __init__(self, number=0x00, timeout=0xFF):
        ChannelMessage.__init__(self, type_=msgtypes.MESSAGE_CHANNEL_SEARCH_TIMEOUT,
                                payload=b'\x00', number=number)
        self.setTimeout(timeout)

    def getTimeout(self):
        return ord(self.payload[1])

    def setTimeout(self, timeout):
        self.payload[1] = bytes([timeout])


class ChannelFrequencyMessage(ChannelMessage):
    """Configuration: Channel RF Frequency (0x45)

    """

    def __init__(self, number=0x00, frequency=66):
        ChannelMessage.__init__(self, type_=msgtypes.MESSAGE_CHANNEL_FREQUENCY,
                                payload=b'\x00', number=number)
        self.setFrequency(frequency)

    def getFrequency(self):
        return ord(self.payload[1])

    def setFrequency(self, frequency):
        self.payload[1] = bytes([frequency])


class ChannelTXPowerMessage(ChannelMessage):
    '''Configuration: Set Channel Tx Power (0x60) '''
    def __init__(self, number=0x00, power=0x00):
        ChannelMessage.__init__(self, type_=msgtypes.MESSAGE_CHANNEL_TX_POWER,
                                payload=b'\x00', number=number)
        self.setPower(power)

    def getPower(self):
        return ord(self.payload[1])

    def setPower(self, power):
        self.payload[1] = bytes([power])


class NetworkKeyMessage(Message):
    '''Configuration: Set Network Key (0x46) '''
    def __init__(self, number=0x00, key=b'\x00' * 8):
        Message.__init__(self, type_=msgtypes.MESSAGE_NETWORK_KEY, payload=b'\x00' * 9)
        self.setNumber(number)
        self.setKey(key)

    def getNumber(self):
        return ord(self.payload[0])

    def setNumber(self, number):
        self.payload[0] = bytes([number])

    def getKey(self):
        return self.getPayload()[1:]

    def setKey(self, key):
        self.payload[1:] = [b'%c' % i for i in key]


class TXPowerMessage(Message):
    '''Configuration: Transmit Power (0x47) '''
    def __init__(self, power=0x00):
        Message.__init__(self, type_=msgtypes.MESSAGE_TX_POWER, payload=b'\x00\x00')
        self.setPower(power)

    def getPower(self):
        return ord(self.payload[1])

    def setPower(self, power):
        self.payload[1] = bytes([power])


# Control messages
class SystemResetMessage(Message):
    '''Control Message: Reset System (0x4A) '''
    def __init__(self):
        Message.__init__(self, type_=msgtypes.MESSAGE_SYSTEM_RESET, payload=b'\x00')


class StartupMessage(Message):
    '''Notification: Start-up Message(0x6F) '''
    def __init__(self):
        Message.__init__(self, type_=msgtypes.MESSAGE_STARTUP, payload=b'\x00')


class ChannelOpenMessage(ChannelMessage):
    ''' Control: Open Channel (0x4B)'''
    def __init__(self, number=0x00):
        ChannelMessage.__init__(self, type_=msgtypes.MESSAGE_CHANNEL_OPEN,
                                number=number)


class ChannelCloseMessage(ChannelMessage):
    ''' Control: Close Channel (0x4C) '''
    def __init__(self, number=0x00):
        ChannelMessage.__init__(self, type_=msgtypes.MESSAGE_CHANNEL_CLOSE,
                                number=number)


class ChannelRequestMessage(ChannelMessage):
    def __init__(self, number=0x00, message_id=msgtypes.MESSAGE_CHANNEL_STATUS):
        ChannelMessage.__init__(self, type_=msgtypes.MESSAGE_CHANNEL_REQUEST,
                                number=number, payload=b'\x00')
        self.setMessageID(message_id)

    def getMessageID(self):
        return ord(self.payload[1])

    def setMessageID(self, message_id):
        if (message_id > 0xFF) or (message_id < 0x00):
            raise antex.MessageError('Could not set message ID (out of range).')

        self.payload[1] = bytes([message_id])


class RequestMessage(ChannelRequestMessage):
    pass


# Data messages
class ChannelBroadcastDataMessage(ChannelMessage):
    '''Data: Broadcast Data (0x4E) '''
    def __init__(self, number=0x00, data='\x00' * 7):
        ChannelMessage.__init__(self, type_=msgtypes.MESSAGE_CHANNEL_BROADCAST_DATA,
                                payload=data, number=number)


class ChannelAcknowledgedDataMessage(ChannelMessage):
    '''Data: Acknowledged Data (0x4F) '''
    def __init__(self, number=0x00, data='\x00' * 7):
        ChannelMessage.__init__(self,
                                type_=msgtypes.MESSAGE_CHANNEL_ACKNOWLEDGED_DATA,
                                payload=data, number=number)


class ChannelBurstDataMessage(ChannelMessage):
    '''Data: Burst Data (0x50) '''
    def __init__(self, number=0x00, data='\x00' * 7):
        ChannelMessage.__init__(self, type_=msgtypes.MESSAGE_CHANNEL_BURST_DATA,
                                payload=data, number=number)


# Channel event messages
class ChannelEventMessage(ChannelMessage):
    '''Channel Response / Event Messages: Channel Response / Event (0x40)'''
    def __init__(self, number=0x00, message_id=0x00, message_code=0x00):
        ChannelMessage.__init__(self, type_=msgtypes.MESSAGE_CHANNEL_EVENT,
                                number=number, payload=b'\x00\x00')
        self.setMessageID(message_id)
        self.setMessageCode(message_code)

    def getMessageID(self):
        return ord(self.payload[1])

    def setMessageID(self, message_id):
        if (message_id > 0xFF) or (message_id < 0x00):
            raise antex.MessageError('Could not set message ID '
                                     '(out of range).')

        self.payload[1] = bytes([message_id])

    def getMessageCode(self):
        return ord(self.payload[2])

    def setMessageCode(self, message_code):
        if (message_code > 0xFF) or (message_code < 0x00):
            raise antex.MessageError('Could not set message code '
                                     '(out of range).')

        self.payload[2] = bytes([message_code])


# Requested response messages
class ChannelStatusMessage(ChannelMessage):
    '''Requested Response: Channel Status (0x52)'''
    def __init__(self, number=0x00, status=0x00):
        ChannelMessage.__init__(self, type_=msgtypes.MESSAGE_CHANNEL_STATUS,
                                payload=b'\x00', number=number)
        self.setStatus(status)

    def getStatus(self):
        return ord(self.payload[1])

    def setStatus(self, status):
        if (status > 0xFF) or (status < 0x00):
            raise antex.MessageError('Could not set channel status '
                                     '(out of range).')

        self.payload[1] = bytes([status])


class VersionMessage(Message):
    ''' Requested Response: ANT Version (0x3E) '''
    def __init__(self, version=b'\x00' * 9):
        Message.__init__(self, type_=msgtypes.MESSAGE_VERSION,
                         payload=b'\x00' * 9)
        self.setVersion(version)

    def getVersion(self):
        return self.getPayload()

    def setVersion(self, version):
        if len(version) != 9:
            raise antex.MessageError('Could not set ANT version '
                                     '(expected 9 bytes).')

        self.setPayload(version)


class CapabilitiesMessage(Message):
    ''' Requested Response: Capabilities (0x54) '''
    def __init__(self, max_channels=0x00, max_nets=0x00, std_opts=0x00,
                 adv_opts=0x00, adv_opts2=0x00):
        Message.__init__(self, type_=msgtypes.MESSAGE_CAPABILITIES,
                         payload=b'\x00' * 4)

        self.setMaxChannels(max_channels)
        self.setMaxNetworks(max_nets)
        self.setStdOptions(std_opts)
        self.setAdvOptions(adv_opts)

        if adv_opts2 is not None:
            self.setAdvOptions2(adv_opts2)

    def getMaxChannels(self):
        return ord(self.payload[0])

    def getMaxNetworks(self):
        return ord(self.payload[1])

    def getStdOptions(self):
        return ord(self.payload[2])

    def getAdvOptions(self):
        return ord(self.payload[3])

    def getAdvOptions2(self):
        return ord(self.payload[4]) if len(self.payload) == 5 else 0x00

    def setMaxChannels(self, num):
        if (num > 0xFF) or (num < 0x00):
            raise antex.MessageError('Could not set max channels '
                                     '(out of range).')

        self.payload[0] = bytes([num])

    def setMaxNetworks(self, num):
        if (num > 0xFF) or (num < 0x00):
            raise antex.MessageError('Could not set max networks '
                                     '(out of range).')

        self.payload[1] = bytes([num])

    def setStdOptions(self, num):
        if (num > 0xFF) or (num < 0x00):
            raise antex.MessageError('Could not set std options '
                                     '(out of range).')

        self.payload[2] = bytes([num])

    def setAdvOptions(self, num):
        if (num > 0xFF) or (num < 0x00):
            raise antex.MessageError('Could not set adv options '
                                     '(out of range).')

        self.payload[3] = bytes([num])

    def setAdvOptions2(self, num):
        if (num > 0xFF) or (num < 0x00):
            raise antex.MessageError('Could not set adv options 2 '
                                     '(out of range).')

        if len(self.payload) == 4:
            self.payload.append(b'\x00')
        self.payload[4] = bytes([num])


class SerialNumberMessage(Message):
    ''' Requested Response: Device Serial Number (0x61) '''
    def __init__(self, serial=b'\x00' * 4):
        Message.__init__(self, type_=msgtypes.MESSAGE_SERIAL_NUMBER)
        self.setSerialNumber(serial)

    def getSerialNumber(self):
        return self.getPayload()

    def setSerialNumber(self, serial):
        if len(serial) != 4:
            raise antex.MessageError('Could not set serial number '
                                     '(expected 4 bytes).')

        self.setPayload(serial)
