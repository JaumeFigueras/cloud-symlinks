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
import watchdog.observers

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, DirModifiedEvent, FileModifiedEvent

from logging.handlers import RotatingFileHandler

from typing import List
from typing import Dict


class LinksEventHandler(FileSystemEventHandler):
    def __init__(self, tar_filename: str, directory: str, log: logging.Logger):
        super().__init__()
        self.tar_file = tar_filename
        self.directory = directory
        self.log = log
        self.timer = None
        self._controlled_change = False

    @property
    def controlled_change(self):
        return self._controlled_change

    @controlled_change.setter
    def controlled_change(self, controlled_change: bool):
        self._controlled_change = controlled_change

    def compress(self, event):
        if not self._controlled_change:
            self.log.info("Directory changed. Event: {0:}.".format(str(event)))
        else:
            self._controlled_change = False

    def on_any_event(self, event):
        if self.timer is not None:
            self.timer.cancel()
        self.timer = threading.Timer(0.5, self.compress, args=(event,))
        self.timer.start()


class TarEventHandler(FileSystemEventHandler):
    def __init__(self, tar_filename: str, directory: str, log: logging.Logger, event_handler_dir: LinksEventHandler):
        super().__init__()
        self.tar_file = tar_filename
        self.directory = directory
        self.log = log
        self.timer = None
        self.event_handler_dir = event_handler_dir

    def untar(self, event):
        self.log.info("Tar file changed. Event: {0:}.".format(str(event)))
        try:
            with tarfile.open(self.tar_file, "r:gz") as tar:
                self.event_handler_dir.controlled_change = True
                self.log.info("Extracting file {0:} with {1:} elements.".format(self.tar_file, len(tar.getnames())))
                tar.extractall(self.directory, members=tar.getmembers())
                tar.close()
        except Exception as e:
            self.log.error("Failed to extract file {0:}. Error: {1:}".format(self.tar_file, str(e)))

    def on_modified(self, event):
        if isinstance(event, FileModifiedEvent):
            if self.timer is not None:
                self.timer.cancel()
            self.timer = threading.Timer(0.5, self.untar, args=[event])
            self.timer.start()


def main(directory: str, tar_filename: str, log: logging.Logger, event: threading.Event) -> None:
    """

    :param directory:
    :param tar_filename:
    :param log:
    :param event:
    :return:
    """

    # Check if the directory exists
    if not os.path.isdir(directory):
        log.error('Directory {0:} does not exist'.format(directory))
        sys.exit(1)
    # Check if the tar file exists
    if not os.path.isfile(tar_filename):
        log.error('Tar file {0:} does not exist'.format(tar_filename))
        sys.exit(1)

    observer_tar_file = Observer()
    observer_directory = Observer()
    event_handler_dir = LinksEventHandler(tar_filename=tar_filename, directory=directory, log=log)
    observer_directory.schedule(event_handler_dir, directory, recursive=False)
    observer_directory.start()
    event_handler_tar = TarEventHandler(tar_filename=tar_filename, directory=directory, log=log, event_handler_dir=event_handler_dir)
    observer_tar_file.schedule(event_handler_tar, tar_filename, recursive=False)
    observer_tar_file.start()
    while not event.is_set():
        time.sleep(1)
    observer_tar_file.stop()
    observer_directory.stop()
    observer_tar_file.join()
    observer_directory.join()


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
