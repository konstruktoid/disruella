# Disruella

`disruella` is the disrupting Cebuella, a very small digitalized primate
responsible for randomly preventing something from continuing as usual
or as expected.

Inspired by [Chaos Monkey](https://github.com/netflix/chaosmonkey) and
similar projects, `disruella` is used on a single host to force basic
testing of application redundency and failover logic.

## Usage

```sh
usage: disruella.py [-h] [-r] [-s SERVICE [SERVICE ...]] [-t] [-v]

options:
  -h, --help            show this help message and exit
  -r, --reboot          allow the host to be rebooted
  -s SERVICE [SERVICE ...], --service SERVICE [SERVICE ...]
                        a service disruella should focus on, otherwise a random PID will be chosen
  -t, --test            don't disrupt anything, just test
  -v, --verbose         print messages to console
```

Use systemd timers or the command line to execute `disruella`.

### Logging

The generated logs can be found using
`sudo journalctl SYSLOG_IDENTIFIER=disruella`.

## Example

```sh
$ ./disruella/disruella.py -v -t -s 'cron'
host_fqdn: ubuntu-jammy
reboot: False
test: True
verbose: True
disruella: Resting, rolled a 3
$ ./disruella/disruella.py -v -t -s 'cron'
host_fqdn: ubuntu-jammy
reboot: False
test: True
verbose: True
[psutil.Process(pid=685, name='cron', status='sleeping', started='18:49:42')]
{'cmdline': ['/usr/sbin/cron', '-f', '-P'], 'name': 'cron', 'username': 'root', 'pid': 685, 'status': 'sleeping'}
disruella: Terminating PID '685' (<bound method Process.name of psutil.Process(pid=685, name='cron', status='sleeping', started='18:49:42')>) on ubuntu-jammy - TEST
$ journalctl -r SYSLOG_IDENTIFIER=disruella
Dec 31 00:25:39 ubuntu-jammy disruella[3586]: Terminating PID '685' (<bound method Process.name of psutil.Process(pid=685, name='cron', status='sleeping', started='18:49:42')>) on ubuntu-jammy - TEST
Dec 31 00:25:38 ubuntu-jammy disruella[3585]: Resting, rolled a 3
Dec 31 00:25:04 ubuntu-jammy disruella[3567]: Terminating PID '685' (<bound method Process.name of psutil.Process(pid=685, name='cron', status='sleeping', started='18:49:42')>) on ubuntu-jammy - TEST
Dec 31 00:25:01 ubuntu-jammy disruella[3566]: Resting, rolled a 2
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
