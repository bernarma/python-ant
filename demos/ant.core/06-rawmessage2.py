"""
Extending on demo 05, request stick capabilities using raw messages.

"""

import time

import ant.core.driver as antdrv
import ant.core.message as antmsg
import ant.core.constants as msgtypes

import config as antcfg

# Initialize
stick = antdrv.USB1Driver(antcfg.SERIAL, log=antcfg.LOG, debug=antcfg.DEBUG)
stick.open()

# Reset stick
msg = antmsg.SystemResetMessage()
stick.write(msg.encode())
time.sleep(1)

# Request stick capabilities
msg = antmsg.ChannelRequestMessage()
msg.setMessageID(msgtypes.MESSAGE_CAPABILITIES)
stick.write(msg.encode())

# Read response
hdlfinder = antmsg.Message()
capmsg = hdlfinder.getHandler(stick.read(8))

print('Std Options:', capmsg.getStdOptions())
print('Adv Options:', capmsg.getAdvOptions())
print('Adv Options 2:', capmsg.getAdvOptions2())
print('Max Channels:', capmsg.getMaxChannels())
print('Max Networks:', capmsg.getMaxNetworks())

# Shutdown
stick.close()
