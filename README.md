# qsutils
A utility library and a collection of scripts to process and filter the output 
of SGE's qstat command

### Install

You should be able to install it as any python package.

    python setup.py install

### Scripts

* runningjobs.py -- counts the jobs in all states, including running at the 
moment.


```shell
$ python runningjobs.py
r: 347
t: 15
qw: 4
```

* setqueues.py -- sets the queues of all queued jobs to a predefined queue 
string (strings are stored in cfg file, see note below).


```shell
$ python setqueues.py serial    
```

* setthrottle.py -- sets the throttle limit of all array jobs to the value of 
the provided command line argument.


```shell
$ python setthrottle.py 10
```

##### Note

In order for `setqueues.py` to work you need to have a `ConfigParser` style 
config file named `queues.cfg` with a section called `[queues]` in the current 
working path when running the script. Example:

    [queues]
    serial=serial.q,serial_lowmem.q
    parallel=parallel.q
