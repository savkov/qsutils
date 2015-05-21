#!<python_path>
# This file is part of qsutils.
#
# The MIT License (MIT)
#
# Copyright (c) 2015 Aleksandar Savkov
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
__author__ = 'Aleksandar Savkov'

import os, sys
import qsutils as qt
import ConfigParser
from ConfigParser import NoOptionError

# You will need to create a config file with queue strings as passed to SGE.
# Example:
#
# [queues]
# serial=serial.q,serial_lowmem.q
# parallel=parallel.q

# Note: only commas between queue names

cfg = ConfigParser.ConfigParser()
try:
    cfg.readfp(open('queues.cfg'))
except IOError:
    print 'Cannot find \'queues.cfg\'.'
    sys.exit(1)

try:
    key = sys.argv[1]
except Exception:
    print 'No queue group key provided.'
    sys.exit(1)

try:
    q = cfg.get('queues', key)
except NoOptionError:
    print 'Unknown option %s' % key
    sys.exit(1)

qs = qt.get_qs('as714')
qjs = qt.get_queued_jobs(qs)
for id in list(qt.get_jids(qjs)):
    os.system('qalter -q %s %s' % (q, id))
