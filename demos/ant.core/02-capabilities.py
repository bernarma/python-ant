"""
Interrogate stick for supported capabilities.

"""

import ant.core.driver as antdrv
import ant.core.node as antnode
import config as antcfg

# Initialize
stick = antdrv.USB1Driver(antcfg.SERIAL, log=antcfg.LOG, debug=antcfg.DEBUG)
antnode = antnode.Node(stick)
antnode.start()

# Interrogate stick
# Note: This method will return immediately, as the stick's capabilities are
# interrogated on node initialization (node.start()) in order to set proper
# internal Node instance state.
capabilities = antnode.getCapabilities()

print('Maximum channels:', capabilities[0])
print('Maximum network keys:', capabilities[1])
print('Standard options: %X' % capabilities[2][0])
print('Advanced options: %X' % capabilities[2][1])

# Shutdown
antnode.stop()
