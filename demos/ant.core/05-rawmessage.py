"""
Do a system reset using raw messages.

"""

import time

import ant.core.driver as antdrv
import ant.core.message as antmsg
import ant.core.constants as msgtypes

import config as antcfg

# Initialize
stick = antdrv.DriverFactory.create(antcfg.DRIVER_TYPE, device=antcfg.SERIAL,
                                    log=antcfg.LOG, debug=antcfg.DEBUG)
stick.open()

# Prepare system reset message
msg = antmsg.Message()
msg.setType(msgtypes.MESSAGE_SYSTEM_RESET)
msg.setPayload(b'\x00')

# Send
stick.write(msg.encode())

# Wait for reset to complete
time.sleep(1)

# Alternatively, we could have done this:
msg = antmsg.SystemResetMessage()
stick.write(msg.encode())
time.sleep(1)

# Shutdown
stick.close()
