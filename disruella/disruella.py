#!/usr/bin/env python3
"""disruella randomly disrupts system processes."""

import argparse
import logging
import logging.handlers
import os
import random
import signal
import socket
import sys
import psutil


def disruella(reboot=False):
    """SIGTERM a process or reboot the host, if specified."""
    host_fqdn = socket.getfqdn()
    handler = logging.handlers.SysLogHandler(address="/dev/log")
    disruella_log = logging.getLogger(host_fqdn)
    disruella_log.addHandler(handler)
    disruella_log.setLevel(logging.DEBUG)

    rhinehart_influence = random.SystemRandom().randint(1, 6)

    if (rhinehart_influence == 6) and reboot:
        disruella_message = f"disruella: Rebooting '{host_fqdn}'."
    elif rhinehart_influence >= 4 and rhinehart_influence < 6:
        try:
            process = get_random_process()
            # os.kill(process.pid, signal.SIGTERM)
            disruella_message = f"disruella: Performing SIGTERM on PID '{process.pid}' ({process.name}) on {host_fqdn}."
            disruella_log.info(disruella_message)
        except Exception:
            disruella_exc = f"Disruella error: {sys.exc_info()}."
            disruella_log.info(disruella_exc)


def get_random_process():
    """Returns a random process."""
    all_processes = psutil.process_iter(attrs=["pid", "name", "cmdline"])
    processes = [p for p in all_processes if p.pid > 500]
    return random.SystemRandom().choice(processes)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reboot", action="store_true", help="allow the host to be rebooted"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    disruella(reboot=args.reboot)
