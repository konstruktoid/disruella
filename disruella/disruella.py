#!/usr/bin/env python3

from subprocess import PIPE, Popen

import argparse
import logging
import logging.handlers
import os
import random
import re
import shutil
import signal
import socket
import sys


PROC_DIR = "/proc"


def arguments():
    global args

    parser = argparse.ArgumentParser(
        description="disruella randomly disrupts system processess."
    )
    parser.add_argument(
        "-s",
        "--services",
        help="Services disruella should focus on, if 'all' a random PID will be chosen",
        required=True,
        nargs="+",
    )
    parser.add_argument("-r", "--reboot", help="Allow rebooting", action="store_true")
    parser.add_argument(
        "-t", "--test", help="Don't disrupt anything, just test", action="store_true"
    )
    parser.add_argument("-v", "--verbose", help="Verbose output", action="store_true")

    args = parser.parse_args()


def network_settings():
    global fqdn

    fqdn = socket.getfqdn()


def exec_check():
    global action, command, service

    exec_check_random = random.SystemRandom()
    systemctl_command = shutil.which("systemctl")

    try:
        services = args.services

        if "all" in services:
            service = 0

        else:
            service = exec_check_random.choice(services)

            if args.verbose:
                print(services)

            if os.path.isfile(systemctl_command):
                actions = [
                    "kill",
                    "reload-or-restart",
                    "restart",
                    "stop",
                    "try-reload-or-restart",
                ]

                action = exec_check_random.choice(actions)
                command = [systemctl_command, action, service]

            else:
                if args.verbose:
                    print("No suitable service manager found.")
                sys.exit(1)

            if args.verbose:
                print(command)

        if args.verbose:
            if service == 0:
                print("All services.")
            else:
                print(service)

    except Exception:
        print("exec_check ERROR: ", sys.exc_info()[0])


def get_pid():
    global pid, str_pid

    proc_random = random.SystemRandom()
    pids = [pid for pid in os.listdir(PROC_DIR) if pid.isdigit()]
    pid = int(proc_random.choice(pids))

    while pid <= 500:
        if args.verbose:
            print(pid)
        get_pid()

    str_pid = str(pid)
    cmdline = open(os.path.join(PROC_DIR, str_pid, "cmdline"), "rb").read()

    if not cmdline:
        get_pid()


def disruella():
    disruella_random = random.SystemRandom()
    handler = logging.handlers.SysLogHandler(address="/dev/log")
    disruella_log = logging.getLogger(fqdn)
    disruella_log.addHandler(handler)
    disruella_log.setLevel(logging.DEBUG)

    try:
        rhinehart_influence = disruella_random.randint(1, 6)
        host_reboot = 0

        if (rhinehart_influence == 6) and args.reboot:
            disruella_message = "disruella: Rebooting '%s'." % (fqdn)
            host_reboot = 1

        elif (rhinehart_influence >= 4) and (service == 0):
            try:
                get_pid()

                pstatus = open(os.path.join(PROC_DIR, str_pid, "status"), "rb").read()
                pcompile = str(pstatus.decode(sys.stdout.encoding))

                for line in re.findall("^Name.*", pcompile, re.MULTILINE):
                    process_name = " ".join(line.split()).replace("Name: ", "")

                disruella_message = (
                    "disruella: Performing SIGTERM on PID '%s' (%s) on %s."
                    % (pid, process_name, fqdn)
                )

                os.kill(pid, signal.SIGTERM)

            except Exception:
                disruella_exc = "DISRUELLA ERROR: %s." % (sys.exc_info())
                disruella_log.info(disruella_exc)

        elif rhinehart_influence >= 4:
            disruella_message = (
                "disruella: Performing '%s' on service '%s' on '%s'."
                % (
                    action,
                    service,
                    fqdn,
                )
            )

            process = Popen(command, stdout=PIPE, stderr=PIPE, shell=False)
            stdout, stderr = process.communicate()

            if stderr:
                disruella_stderr = "disruella: %s" % (
                    stderr.decode(sys.stdout.encoding)
                )
                disruella_log.info(disruella_stderr)

            if stdout:
                disruella_stdout = "disruella: %s" % (
                    stdout.decode(sys.stdout.encoding)
                )
                disruella_log.info(disruella_stdout)

        else:
            disruella_message = "disruella: Resting, rolled a %s." % (
                rhinehart_influence
            )

        if args.test:
            disruella_message = ("%s Test.") % (disruella_message)

        disruella_log.info(disruella_message)

        if args.verbose:
            disruella_verbose = ("%s [%s]") % (disruella_message, rhinehart_influence)
            print(disruella_verbose)

        if host_reboot == 1:
            process = Popen("/sbin/reboot", shell=False)

    except Exception:
        disruella_exc = "DISRUELLA ERROR: %s." % (sys.exc_info())
        disruella_log.info(disruella_exc)


if __name__ == "__main__":
    arguments()
    exec_check()
    network_settings()
    disruella()
