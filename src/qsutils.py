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

import re
import io
import pandas as pd
import subprocess as sub

from collections import Counter


def get_qs(user):
    """Returns the output of qstat -u <user>

    :param user: SGE user
    :return: qstat table
    :rtype: DataFrame
    """
    qs_str = sub.check_output('qstat -u {}'.format(user), shell=True)
    return parse_qs(qs_str)


def parse_qs(qs):
    """Parses the output of SGE command 'qstat -u <user>' into a pandas
    DataFrame.

    Known bug: interactive queue entries messes it up. Haven't had the time
    to fix it.

    :param qs: qstat output
    :return: parsed qstat table
    :rtype: DataFrame
    """
    qss = re.sub('[-]+\n', '', qs)
    qss = re.sub(' at', '_at', qss)
    header = qss.split('\n')[0]
    it = re.finditer('([^ ]+ +)', header)
    splits = [x.start() for x in it][1:]
    rows = []
    for line in qss.split('\n'):
        if line.replace(' ', '') == '':
            continue
        start = 0
        cols = []
        for end in splits:
            cols.append(line[start:end].strip())
            start = end
        cols.append(line[start:].strip())
        rows.append(','.join(cols))
    sio = io.StringIO(unicode('\n'.join(rows)))
    return pd.io.parsers.read_csv(sio, dtype='object')


def get_ajs(qs):
    """Returns a DataFrame with all array job entries.

    :param qs: qstat table
    :return: array job entries
    :rtype: DataFrame
    """
    return qs[qs['ja-task-ID'].str.contains('-')]


def get_jids(qs):
    """Returns a DataFrame with all job IDs.

    :param qs: qstat table
    :return: job IDs
    :rtype: DataFrame
    """
    return qs['job-ID']


def get_queued_jobs(qs):
    """Returns all queued job entries.

    :param qs: qstat table
    :return: queued job entries
    :rtype: DataFrame
    """
    return qs[qs['state'] == 'qw']


def count_jstats(qs):
    """Returns a Counter with all job status counts.

    :param qs: qstat table
    :return: dictionary of job status counts
    :rtype: Counter
    """
    return Counter(qs['state'])


def count_remaining_jobs(qs):
    """Returns the number of active queuing jobs, remaining array jobs
    included.

    :param qs: qstat table
    :type qs: DataFrame
    :return: number of all queued jobs
    """
    ajs = get_ajs(qs)
    queued = count_jstats(qs)['qw']
    queued_aj = []
    for aj in ajs['ja-task-ID']:
        m = re.match('(\d+)-(\d+):(\d+)', aj)
        queued_aj.append(int(m.group(2)) - int(m.group(1)))
    return sum(queued_aj) + queued - len(ajs)