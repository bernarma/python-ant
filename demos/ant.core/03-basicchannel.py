'''
Initialize a basic broadcast slave channel for listening to
an ANT+ HR monitor.
'''

import time

import ant.core.driver as antdrv
import ant.core.node as antnode
import ant.core.constants as msgtypes
import config as antcfg

NETKEY = b'\xB9\xA5\x21\xFB\xBD\x72\xC3\x45'

# Initialize
stick = antdrv.DriverFactory.create(antcfg.DRIVER_TYPE, device=antcfg.SERIAL,
                                    log=antcfg.LOG, debug=antcfg.DEBUG)

node = antnode.Node(stick)
node.start()

# Set network key
key = antnode.NetworkKey('N:ANT+', NETKEY)
node.setNetworkKey(0, key)

# Get the first unused channel. Returns an instance of the node.Channel class.
channel = node.getFreeChannel()

# Let's give our channel a nickname
channel.name = 'C:HRM'

# Initialize it as a receiving channel using our network key
channel.assign('N:ANT+', msgtypes.CHANNEL_TYPE_TWOWAY_RECEIVE)

# Now set the channel id for pairing with an ANT+ HR monitor
channel.setID(120, 0, 0)

# Listen forever and ever (not really, but for a long time)
channel.setSearchTimeout(msgtypes.TIMEOUT_NEVER)

# We want a ~4.06 Hz transmission period
channel.setPeriod(8070)

# And ANT frequency 57
channel.setFrequency(57)

# Time to go live
channel.open()

print("Listening for HR monitor events (120 seconds)...")
time.sleep(120)

# Shutdown channel
channel.close()
channel.unassign()

# Shutdown
node.stop()
