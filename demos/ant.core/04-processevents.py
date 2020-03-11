'''
Extending on demo-03, implements an event callback we can use to process the
incoming data.
'''

import time

import ant.core.driver as antdrv
import ant.core.message as antmsg
import ant.core.event as antevt
import ant.core.node as antnode
import ant.core.constants as antc
import config as antcfg

NETKEY = b'\xB9\xA5\x21\xFB\xBD\x72\xC3\x45'

class HRMListener(antevt.EventCallback):
    '''Run of the mill event listener. '''
    def process(self, msg):
        if isinstance(msg, antmsg.ChannelBroadcastDataMessage):
            print('Heart Rate:', ord(msg.payload[-1]))

# Initialize
stick = antdrv.DriverFactory.create(antcfg.DRIVER_TYPE, device=antcfg.SERIAL,
                                    log=antcfg.LOG, debug=antcfg.DEBUG)

node = antnode.Node(stick)
node.start()

# Setup channel
key = antnode.NetworkKey('N:ANT+', NETKEY)
node.setNetworkKey(0, key)
channel = node.getFreeChannel()
channel.name = 'C:HRM'
channel.assign('N:ANT+', antc.CHANNEL_TYPE_TWOWAY_RECEIVE)
channel.setID(120, 0, 0)
channel.setSearchTimeout(antc.TIMEOUT_NEVER)
channel.setPeriod(8070)
channel.setFrequency(57)
channel.open()

# Setup callback
# Note: We could also register an event listener for non-channel events by
# calling registerEventListener() on antnode rather than channel.
channel.registerCallback(HRMListener())

# Wait
print("Listening for HR monitor events (120 seconds)...")
time.sleep(120)

# Shutdown
channel.close()
channel.unassign()
node.stop()
