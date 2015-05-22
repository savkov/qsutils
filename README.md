# qsutils
A utility library and a collection of scripts to process and filter the output 
of SGE's qstat command

### Installation

`qtutils` currently only supports Python 2 (Python3 support is in the works). Install it from sources:
    
    git clone https://github.com/savkov/qsutils.git
    cd qsutils
    python setup.py install


### Usage

* Count jobs in all states, including running at the moment.


```shell
$ qsutils jobs
r: 347
t: 15
qw: 4

# You can also specify a user name, e.g.
$ qsutils --user mmb28 jobs
```

* Set the queues of all queued jobs to a predefined queue 
string (strings are stored in cfg file, see note below).


```shell
$ qsutils queues serial
```

* Set the throttle limit of all array jobs to the value of 
the provided command line argument.


```shell
$ qsutils throttle 10
```

##### Configuration file

In order for `setqueues.py` to work you need to have a `ConfigParser` style 
config file named `queues.cfg` with a section called `[queues]` in the current 
working path when running the script. Example:

    [queues]
    serial=serial.q,serial_lowmem.q
    parallel=parallel.q

