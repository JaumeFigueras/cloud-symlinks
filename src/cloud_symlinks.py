#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import tarfile
import sys
import os
import logging
import time
import threading
from pathlib import Path

import psutil

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from logging.handlers import RotatingFileHandler

from typing import List
from typing import Dict


class TarEventHandler(FileSystemEventHandler):
    def __init__(self, log: logging.Logger):
        super().__init__()
        self.log = log

    @staticmethod
    def has_handle(path: str):
        f_path = Path(path)
        for proc in psutil.process_iter():
            try:
                for item in proc.open_files():
                    print(item.path)
                    if f_path == Path(item.path):
                        return True
            except Exception:
                pass
            return False

    def on_modified(self, event):
        if not self.has_handle(event.src_path):
            self.log.info("Tar file changed. Event: {0:}.".format(str(event)))


def main(directory: str, tar_file: str, log: logging.Logger, event: threading.Event) -> None:
    """

    :param directory:
    :param tar_file:
    :param log:
    :param event:
    :return:
    """

    # Check if the directory exists
    if not os.path.isdir(directory):
        log.error('Directory {0:} does not exist'.format(directory))
        sys.exit(1)
    # Check if the tar file exists
    if not os.path.isfile(tar_file):
        log.error('Tar file {0:} does not exist'.format(tar_file))
        sys.exit(1)

    event_handler = TarEventHandler(log)
    observer_tar_file = Observer()
    observer_tar_file.schedule(event_handler, tar_file, recursive=False)
    observer_tar_file.start()
    while not event.is_set():
        time.sleep(1)
    observer_tar_file.stop()
    observer_tar_file.join()


if __name__ == "__main__":  # pragma: no cover
    # Config the program arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir', help='Directory to tar', required=True)
    parser.add_argument('-f', '--tar-file', help='Location of the tar file containing ', required=True)
    parser.add_argument('-l', '--log-file', help='Log file to record program progress', required=False, default=None)
    args = parser.parse_args()

    # Turn on the logger
    logger = logging.getLogger(__name__)
    if args.log_file is not None:
        handler = RotatingFileHandler(args.log_file, mode='a', maxBytes=5*1024*1024, backupCount=15, encoding='utf-8', delay=False)
        logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s', handlers=[handler], encoding='utf-8', level=logging.DEBUG, datefmt="%Y-%m-%d %H:%M:%S")
    else:
        handler = ch = logging.StreamHandler()
        logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s', handlers=[handler], encoding='utf-8', level=logging.DEBUG, datefmt="%Y-%m-%d %H:%M:%S")

    # Run the watchdogs
    main(args.dir, args.tar_file, logger, threading.Event())
