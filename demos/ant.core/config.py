# -*- coding: utf-8 -*-

'''Configuration for Demos. '''

import ant.core.log as antl

# Type of Driver to use - USB1 or USB2
DRIVER_TYPE = 'USB2'

# USB1 ANT stick interface. Running `dmesg | tail -n 25` after plugging the
# stick on a USB port should tell you the exact interface.
SERIAL = '/dev/ttyUSB0'

# If set to True, the stick's driver will dump everything it reads/writes
# from/to the stick.
# Some demos depend on this setting being True, so unless you know what you
# are doing, leave it as is.
DEBUG = True

# Set to None to disable logging
#LOG = None
LOG = antl.LogWriter()

# ========== DO NOT CHANGE ANYTHING BELOW THIS LINE ==========
print("Using log file:", LOG.filename)
print("")
