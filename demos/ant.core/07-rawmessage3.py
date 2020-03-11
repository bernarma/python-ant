"""
Initialize a basic broadcast slave channel for listening to
an ANT+ Bicycle cadence and speed senser, using raw messages
and event handlers.

"""

import sys
import time

import ant.core.driver as antdrv
import ant.core.event as antevt
import ant.core.constants as msgtypes
import ant.core.message as antmsg

import config as antcfg

NETKEY = b'\xB9\xA5\x21\xFB\xBD\x72\xC3\x45'

# Event callback
class MyCallback(antevt.EventCallback):
    def process(self, msg):
        print(msg)

# Initialize driver
stick = antdrv.DriverFactory.create(antcfg.DRIVER_TYPE, device=antcfg.SERIAL,
                                    log=antcfg.LOG, debug=antcfg.DEBUG)
stick.open()

# Initialize event machine
evm = antevt.EventMachine(stick)
evm.registerCallback(MyCallback())
evm.start()

# Reset
msg = antmsg.SystemResetMessage()
stick.write(msg.encode())
time.sleep(1)

# Set network key
msg = antmsg.NetworkKeyMessage(key=NETKEY)
stick.write(msg.encode())
if evm.waitForAck(msg) != msgtypes.RESPONSE_NO_ERROR:
    sys.exit()

# Initialize it as a receiving channel using our network key
msg = antmsg.ChannelAssignMessage()
stick.write(msg.encode())
if evm.waitForAck(msg) != msgtypes.RESPONSE_NO_ERROR:
    sys.exit()

# Now set the channel id for pairing with an ANT+ bike cadence/speed sensor
msg = antmsg.ChannelIDMessage(device_type=121)
stick.write(msg.encode())
if evm.waitForAck(msg) != msgtypes.RESPONSE_NO_ERROR:
    sys.exit()

# Listen forever and ever (not really, but for a long time)
msg = antmsg.ChannelSearchTimeoutMessage(timeout=255)
stick.write(msg.encode())
if evm.waitForAck(msg) != msgtypes.RESPONSE_NO_ERROR:
    sys.exit()

# We want a ~4.05 Hz transmission period
msg = antmsg.ChannelPeriodMessage(period=8085)
stick.write(msg.encode())
if evm.waitForAck(msg) != msgtypes.RESPONSE_NO_ERROR:
    sys.exit()

# And ANT frequency 57, of course
msg = antmsg.ChannelFrequencyMessage(frequency=57)
stick.write(msg.encode())
if evm.waitForAck(msg) != msgtypes.RESPONSE_NO_ERROR:
    sys.exit()

# Time to go live
msg = antmsg.ChannelOpenMessage()
stick.write(msg.encode())
if evm.waitForAck(msg) != msgtypes.RESPONSE_NO_ERROR:
    sys.exit()

print("Listening for ANT events (120 seconds)...")
time.sleep(120)

# Shutdown
msg = antmsg.SystemResetMessage()
stick.write(msg.encode())
time.sleep(1)

evm.stop()
stick.close()
