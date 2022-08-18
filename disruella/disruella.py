#!/usr/bin/env python3
"""disruella randomly disrupts system processes."""
from subprocess import PIPE, Popen  # nosec B404

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

ACTION = None
ARGS = None
COMMAND = None
FQDN = None
PID = None
PROC_DIR = "/proc"
SERVICE = None
STR_PID = None


def arguments():
    """Command line arguments and help information."""
    global ARGS

    parser = argparse.ArgumentParser(
        description="disruella randomly disrupts system processes."
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

    ARGS = parser.parse_args()


def network_settings():
    """Returns FQDN."""
    global FQDN

    FQDN = socket.getfqdn()


def exec_check():
    """Returns systemctl command actions."""
    global ACTION, COMMAND, SERVICE

    exec_check_random = random.SystemRandom()
    systemctl_command = shutil.which("systemctl")

    try:
        args_services = ARGS.services

        if "all" in args_services:
            SERVICE = 0

        else:
            SERVICE = exec_check_random.choice(args_services)

            if ARGS.verbose:
                print(args_services)

            if os.path.isfile(systemctl_command):
                systemctl_actions = [
                    "kill",
                    "reload-or-restart",
                    "restart",
                    "stop",
                    "try-reload-or-restart",
                ]

                ACTION = exec_check_random.choice(systemctl_actions)
                COMMAND = [systemctl_command, ACTION, SERVICE]

            else:
                if ARGS.verbose:
                    print("No suitable service manager found.")
                sys.exit(1)

            if ARGS.verbose:
                print(COMMAND)

        if ARGS.verbose:
            if SERVICE == 0:
                print("All services.")
            else:
                print(SERVICE)

    except UnboundLocalError:
        print("Disruella UnboundLocalError: ", sys.exc_info()[0])


def get_pid():
    """Returns PID and PID COMMAND line."""
    global PID, STR_PID

    proc_random = random.SystemRandom()
    system_pids = [PID for PID in os.listdir(PROC_DIR) if PID.isdigit()]
    PID = int(proc_random.choice(system_pids))

    while PID <= 500:
        if ARGS.verbose:
            print(PID)
        get_pid()

    STR_PID = str(PID)
    cmdline = open(os.path.join(PROC_DIR, STR_PID, "cmdline"), "rb").read()

    if not cmdline:
        get_pid()


def disruella():
    """Merge all and execute ACTION."""
    disruella_random = random.SystemRandom()
    handler = logging.handlers.SysLogHandler(address="/dev/log")
    disruella_log = logging.getLogger(FQDN)
    disruella_log.addHandler(handler)
    disruella_log.setLevel(logging.DEBUG)

    try:
        rhinehart_influence = disruella_random.randint(1, 6)
        host_reboot = 0

        if (rhinehart_influence == 6) and ARGS.reboot:
            disruella_message = "disruella: Rebooting '%s'." % (FQDN)
            host_reboot = 1

        elif (rhinehart_influence >= 4) and (SERVICE == 0):
            try:
                get_pid()

                pstatus = open(os.path.join(PROC_DIR, STR_PID, "status"), "rb").read()
                pcompile = str(pstatus.decode(sys.stdout.encoding))

                for line in re.findall("^Name.*", pcompile, re.MULTILINE):
                    process_name = " ".join(line.split()).replace("Name: ", "")

                disruella_message = (
                    "disruella: Performing SIGTERM on PID '%s' (%s) on %s."
                    % (PID, process_name, FQDN)
                )

                os.kill(PID, signal.SIGTERM)

            except UnboundLocalError:
                disruella_exc = "Disruella UnboundLocalError: %s." % (sys.exc_info())
                disruella_log.info(disruella_exc)

        elif rhinehart_influence >= 4:
            disruella_message = (
                "disruella: Performing '%s' on service '%s' on '%s'."
                % (
                    ACTION,
                    SERVICE,
                    FQDN,
                )
            )

            process = Popen(COMMAND, stdout=PIPE, stderr=PIPE, shell=False)  # nosec
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

        if ARGS.test:
            disruella_message = ("%s Test run.") % (disruella_message)

        disruella_log.info(disruella_message)

        if ARGS.verbose:
            disruella_verbose = ("%s [%s]") % (disruella_message, rhinehart_influence)
            print(disruella_verbose)

        if host_reboot == 1 and not ARGS.test:
            process = Popen("/sbin/reboot", shell=False)  # nosec B404,B603

    except UnboundLocalError:
        disruella_exc = "Disruella UnboundLocalError: %s." % (sys.exc_info())
        disruella_log.info(disruella_exc)


if __name__ == "__main__":
    arguments()
    exec_check()
    network_settings()
    disruella()
