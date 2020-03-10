"""
Perform basic node initialization and shutdown cleanly.

"""

import sys

import ant.core.driver as antdrv
import ant.core.node as antnode
import config as antcfg

# Initialize and configure our ANT stick's driver
stick = antdrv.USB1Driver(antcfg.SERIAL, log=antcfg.LOG, debug=antcfg.DEBUG)

# Now create an ANT node, and pass it our driver so it can talk to the stick
node = antnode.Node(stick)

# Open driver if closed, start event listener, reset internal settings, and
# send a system reset command to the ANT stick (blocks).
try:
    node.start()
except antdrv.DriverError as e:
    print(e)
    sys.exit()

# At any point in our node's life, we could manually call reset() to re-
# initialize the stick and Node. Like this:
#node.reset()

# Stop the ANT node. This should close all open channels, and do final system
# reset on the stick. However, considering we just did a reset, we explicitly
# tell our node to skip the reset. This call will also automatically release
# the stick by calling close() on the driver.
node.stop(reset=False)
