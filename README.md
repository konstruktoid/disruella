# Disruella

THIS IS CURRENTLY INACCURATE, REFACTOR IN PROGRESS

`disruella` is the disrupting Cebuella, a very small digitalized primate
responsible for randomly preventing something from continuing as usual
or as expected.

Inspired by [Chaos Monkey](https://github.com/netflix/chaosmonkey) and
similar projects, `disruella` is used on a single host to force basic
testing of application redundency and failover logic.

## Usage

```sh
usage: disruella.py [-h] -s SERVICES [SERVICES ...] [-r] [-t] [-v]

disruella randomly disrupts system processes.

optional arguments:
  -h, --help            show this help message and exit
  -s SERVICES [SERVICES ...], --services SERVICES [SERVICES ...]
                        Services disruella should focus on, if 'all' a random
                        PID will be chosen
  -r, --reboot          Allow rebooting
  -t, --test            Don't disrupt anything, just test
  -v, --verbose         Verbose output
```

Use systemd timers or the command line to execute `disruella`.

## Workflow

1. Find `systemctl` and register available actions.
1. Roll a six sided dice.
    1. If the roll is six and the `reboot` argument is used, reboot the host.
    1. If the roll is equal or higher than four and `--services all`, then get a
      PID higher than 500 with a valid `cmdline`, and send a `SIGTERM` to that
      process.
    1. If the roll is equal or higher than four and one or more services are
      specified, then perform a random `systemctl` action on one of the
      services.
    1. If the roll is lower than four, `disruella` won't do anything.

### systemctl actions

```python
actions = [
    "kill",
    "reload-or-restart",
    "restart",
    "stop",
    "try-reload-or-restart",
]
```

See [https://www.freedesktop.org/software/systemd/man/systemctl.html](https://www.freedesktop.org/software/systemd/man/systemctl.html)
for details on each action.

### Logging

The generated logs can be found using
`sudo journalctl SYSLOG_IDENTIFIER=disruella`.

## Example

```sh
~$ sudo /vagrant/disruella/disruella.py -v -s test
['test']
['/usr/bin/systemctl', 'stop', 'test']
test
disruella: performing 'stop' on service 'test' on 'ubuntu-focal'. [6]
~$ sudo /vagrant/disruella/disruella.py -v -s atd
['atd']
['/usr/bin/systemctl', 'try-reload-or-restart', 'atd']
atd
disruella: performing 'try-reload-or-restart' on service 'atd' on 'ubuntu-focal'. [4]
~$ sudo /vagrant/disruella/disruella.py -v -s atd -t
['atd']
['/usr/bin/systemctl', 'try-reload-or-restart', 'atd']
atd
disruella: resting, rolled a 2. Test. [2]
~$ sudo /vagrant/disruella/disruella.py -v -s atd -t
['atd']
['/usr/bin/systemctl', 'stop', 'atd']
atd
disruella: performing 'stop' on service 'atd' on 'ubuntu-focal'. Test. [6]
~$ sudo /vagrant/disruella/disruella.py -s atd -t
~$ sudo /vagrant/disruella/disruella.py -s atd
~$ sudo journalctl SYSLOG_IDENTIFIER=disruella
[...]
Oct 12 21:32:29 ubuntu-focal disruella[28571]: Failed to stop test.service: Unit test.service not loaded.
Oct 12 21:32:29 ubuntu-focal disruella[28571]: performing 'stop' on service 'test' on 'ubuntu-focal'.
Oct 12 21:33:46 ubuntu-focal disruella[28642]: Failed to restart test.service: Unit test.service not found.
Oct 12 21:33:46 ubuntu-focal disruella[28642]: performing 'restart' on service 'test' on 'ubuntu-focal'.
Oct 12 21:34:30 ubuntu-focal disruella[28689]: Failed to stop test.service: Unit test.service not loaded.
Oct 12 21:34:30 ubuntu-focal disruella[28689]: performing 'stop' on service 'test' on 'ubuntu-focal'.
Oct 12 21:34:32 ubuntu-focal disruella[28695]: resting, rolled a 1.
Oct 12 21:34:36 ubuntu-focal disruella[28699]: Failed to stop test.service: Unit test.service not loaded.
Oct 12 21:34:36 ubuntu-focal disruella[28699]: performing 'stop' on service 'test' on 'ubuntu-focal'.
Oct 12 21:34:43 ubuntu-focal disruella[28709]: performing 'try-reload-or-restart' on service 'atd' on 'ubuntu-focal'.
Oct 12 21:34:50 ubuntu-focal disruella[28717]: resting, rolled a 2. Test.
Oct 12 21:34:52 ubuntu-focal disruella[28723]: performing 'stop' on service 'atd' on 'ubuntu-focal'. Test.
Oct 12 21:35:25 ubuntu-focal disruella[28752]: resting, rolled a 1. Test.
Oct 12 21:35:26 ubuntu-focal disruella[28758]: performing 'restart' on service 'atd' on 'ubuntu-focal'.
```

## Contributing

Do you want to contribute? Great! Contributions are always welcome,
no matter how large or small. If you found something odd, feel free to submit a
issue, improve the code by creating a pull request, or by
[sponsoring this project](https://github.com/sponsors/konstruktoid).

## License

Apache License Version 2.0

## Author Information

[https://github.com/konstruktoid](https://github.com/konstruktoid "github.com/konstruktoid")
