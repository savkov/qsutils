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
from __future__ import print_function
import argparse
import os
import re
import sys
import subprocess as sub
import pwd

if sys.version_info.major == 2:
    import ConfigParser
    from ConfigParser import NoOptionError
else:
    from configparser import ConfigParser, NoOptionError

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
    :rtype: dict
    """
    qss = re.sub('[-]+\n', '', qs)
    qss = re.sub(' at', '_at', qss)
    header = qss.split('\n')[0]
    it = re.finditer('([^ ]+ +)', header)
    splits = [x.start() for x in it][1:]

    # scan header
    names = [x.strip() for x in re.sub(r' +', ' ', header).split(' ') if x.strip()]

    # initialise the table
    table = {x: [] for x in names}

    # scan the rest of the rows
    for line in qss.split('\n')[1:]:
        if line.replace(' ', '') == '':
            continue
        start = 0
        for col_n, end in zip(names, splits):
            table[col_n].append(line[start:end].strip())
            start = end
        table[names[-1]].append(line[start:].strip())

    return table


def get_ajs(qs):
    """Returns all array job entries.

    :param qs: qstat table
    :return: array job entries
    :rtype: list
    """
    ids = [i for i, x in enumerate(qs['ja-task-ID']) if '-' in x]
    return _slice_table(qs, ids)


def get_jids(qs):
    """Returns all job IDs.

    :param qs: qstat table
    :return: job IDs
    :rtype: list
    """
    return qs['job-ID']


def get_queued_jobs(qs):
    """Returns all queued job entries.

    :param qs: qstat table
    :return: queued job entries
    :rtype: list
    """
    ids = [i for i, x in enumerate(qs['state']) if x == 'qw']
    return _slice_table(qs, ids)


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


def _slice_table(table, ids):
    keys = table.keys()
    new_table = {k: [] for k in keys}
    for id in ids:
        for k in keys:
            new_table[k].append(table[k][id])
    return new_table


def _parse_cfg_file():
    """
    You will need to create a config file with queue strings as passed to SGE.
    Example:

    [user]
        name=mmb28

    [queues]
        serial=serial.q,serial_lowmem.q
        parallel=parallel.q

    Note: only commas between queue names
    """
    cfg = ConfigParser()
    try:
        with open('queues.cfg') as infile:
            cfg.read_file(infile)
        return cfg
    except IOError:
        print('Cannot find \'queues.cfg\'.')
        sys.exit(1)


def _get_user_name():
    return pwd.getpwuid(os.getuid()).pw_name


def _print_running_jobs(user=None, **kwargs):
    if not user:
        user = _get_user_name()
    print('Jobs of user', user)
    qs = get_qs(user)
    counts = count_jstats(qs)
    for k in counts.keys():
        print('{}: {}'.format(k, counts[k]))


def _set_queues(alias=None, **kwargs):
    print('Setting queues of to', alias)
    cfg = _parse_cfg_file()
    try:
        q = cfg.get('queues', alias)
    except NoOptionError:
        raise ValueError('Unknown queue alias \'%s\'' % alias)

    qs = get_qs(_get_user_name())
    qjs = get_queued_jobs(qs)
    for id in list(get_jids(qjs)):
        cmd = 'qalter -q %s %s' % (q, id)
        print('Running \'%s\'' % cmd)
        os.system(cmd)


def _throttle_jobs(limit=0, **kwargs):
    print('Limiting array jobs of to', limit)
    qs = get_qs(_get_user_name())
    ajs = get_ajs(qs)
    for job_id in list(get_jids(ajs)):
        cmd = 'qalter -tc %s %s' % (limit, job_id)
        print('Running \'%s\'' % cmd)
        os.system(cmd)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_jobs = subparsers.add_parser('jobs', help='List your current jobs')
    parser_jobs.set_defaults(func=_print_running_jobs)
    parser_jobs.add_argument('--user', '-u', default=None)

    parser_throttle = subparsers.add_parser('throttle', help='Throttle your current jobs')
    parser_throttle.add_argument('limit', type=int, help='Maximum jobs in job array')
    parser_throttle.set_defaults(func=_throttle_jobs)

    parser_queues = subparsers.add_parser('queues', help='Change queues your job is running on')
    parser_queues.add_argument('alias', type=str, help='Alias of queues list')
    parser_queues.set_defaults(func=_set_queues)

    args = parser.parse_args()
    args.func(**args.__dict__)
