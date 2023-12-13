#!/usr/bin/env python3
"""disruella randomly disrupts system processes."""

import argparse
import logging
import logging.handlers
import random
import shutil
import socket
import subprocess  # nosec B404,S404
import sys

import psutil


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-r",
        "--reboot",
        action="store_true",
        help="allow the host to be rebooted",
    )
    parser.add_argument(
        "-s",
        "--service",
        help="service disruella should disrupt, otherwise a random PID will be chosen",
        nargs="+",
    )
    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        help="don't disrupt anything, just test",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="print messages to console",
    )
    return parser.parse_args()


def get_process(service, verbose):
    """Returns a service or a random process."""

    low_pids = 500

    if service:
        for service_name in service:
            processes = [p for p in psutil.process_iter() if p.name() == service_name]
    else:
        processes = [p for p in psutil.process_iter() if p.pid > low_pids]

    if verbose:
        print(processes)

    return random.SystemRandom().choice(processes)


def disruella(reboot, test, verbose, service):  # noqa: C901, PLR0912
    """Terminate a process or reboot the host, if specified."""
    host_fqdn = socket.getfqdn()
    handler = logging.handlers.SysLogHandler(address="/dev/log")
    disruella_log = logging.getLogger(host_fqdn)
    disruella_log.addHandler(handler)
    disruella_log.setLevel(logging.DEBUG)

    rhinehart_influence = random.SystemRandom().randint(1, 6)

    if verbose:
        print(
            f"host_fqdn: {host_fqdn}\nreboot: {reboot}\ntest: {test}\n",
        )

    dice_max = 6
    dice_median = 4

    if (rhinehart_influence == dice_max) and reboot:
        disruella_message = f"disruella: Rebooting '{host_fqdn}'"
        if test:
            disruella_message = f"{disruella_message} - TEST"

        if verbose:
            print(f"{disruella_message}")

        disruella_log.info(disruella_message)

        if not test:
            shutdown_command = shutil.which("shutdown")
            subprocess.run(
                [shutdown_command, "-r", "now", "Initialised by disruella"],
                shell=False,  # noqa: S603
                check=True,
            )
    elif rhinehart_influence >= dice_median:
        try:
            service = get_process(service, verbose)

            disruella_message = f"disruella: Terminating PID '{service.pid}' ({service.name}) on {host_fqdn}"  # noqa: E501
            if test:
                disruella_message = f"{disruella_message} - TEST"

            if verbose:
                print(
                    service.as_dict(
                        attrs=["cmdline", "name", "pid", "status", "username"],
                    ),
                )
                print(f"{disruella_message}")

            disruella_log.info(disruella_message)

            if not test:
                service.terminate()

        except psutil.AccessDenied:
            disruella_exc = f"disruella: {sys.exc_info()}."
            disruella_log.info(disruella_exc)

            if verbose:
                print(disruella_exc)

    else:
        disruella_message = f"disruella: Resting, rolled a {rhinehart_influence}"

        if verbose:
            print(f"{disruella_message}")

        disruella_log.info(disruella_message)


if __name__ == "__main__":
    args = parse_args()
    disruella(
        reboot=args.reboot,
        service=args.service,
        test=args.test,
        verbose=args.verbose,
    )
