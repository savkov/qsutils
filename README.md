# qsutils
A utility library and a collection of scripts to process and filter the output 
of SGE's qstat command

### Installation

You should be able to install it as any python package.
    
    git clone https://github.com/savkov/qsutils.git
    cd qsutils
    python setup.py install

or straight from github:

    pip install git+ssh://git@github.com/savkov/qsutils.git


### Usage

* Count jobs in all states, including running at the moment.


```shell
$ qsutils jobs
r: 347
t: 15
qw: 4
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

All commands above take an optional user name, e.g.

```shell
$ qsutils --user mmb28 jobs
r: 347
t: 15
qw: 4
```

Note in standard SGE environments you will not be able to modify other users' jobs.

##### Configuration file

In order for `setqueues.py` to work you need to have a `ConfigParser` style 
config file named `queues.cfg` with a section called `[queues]` in the current 
working path when running the script. Example:

    [queues]
    serial=serial.q,serial_lowmem.q
    parallel=parallel.q

