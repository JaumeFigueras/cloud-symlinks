#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime
import tarfile
import sys
import os
import logging
import time
import threading
import configparser
import watchdog.events

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import FileModifiedEvent
from watchdog.events import DirModifiedEvent

from logging.handlers import RotatingFileHandler


class SymLinksEventHandler(FileSystemEventHandler):
    def __init__(self, tar_filename: str, symlinks_directory: str, log: logging.Logger) -> None:
        """
        Class creator

        :param tar_filename: Path with the filename of the tar file where the symbolic links are stored.
        :type tar_filename: str
        :param symlinks_directory: Path of the directory containing the symbolic links.
        :type symlinks_directory: str
        :param log: Logger to write the status or error messages.
        :type log: logging.Logger
        """
        super().__init__()
        self.tar_filename = tar_filename
        self.symlinks_directory = symlinks_directory
        self.log = log
        self.timer = None
        self._controlled_change = False
        self._event_handler_tar = None

    @property
    def controlled_change(self) -> bool:
        """
        Getter of the boolean that enables or disables the reaction of the handler to an event in the file system

        :return: True when the actual change is controlled by the main program and should be ignored, False otherwise.
        :rtype: bool
        """
        return self._controlled_change

    @controlled_change.setter
    def controlled_change(self, controlled_change: bool) -> None:
        """
        Enables or disables the reaction of the handler to an event in the file system

        :param controlled_change: True when the actual change is controlled by the main program and should be ignored,
        False otherwise.
        :type controlled_change: bool
        :return: Nothing
        """
        self._controlled_change = controlled_change

    @property
    def tar_event_handler(self) -> TarEventHandler:
        """
        Property to store the tar file event handler reference

        :return: The tar file event handler reference
        :rtype: TarEventHandler
        """
        return self._event_handler_tar

    @tar_event_handler.setter
    def tar_event_handler(self, event_handler_tar: TarEventHandler) -> None:
        """
        Setter of the tar file event handler property

        :param event_handler_tar: The tar file event handler
        :type event_handler_tar: TarEventHandler
        """
        self._event_handler_tar = event_handler_tar

    def compress(self, event: watchdog.events.FileSystemEvent) -> None:
        """
        Helper method that compresses the symbolic links directory to the tar file

        :param event: The event that generated the storage of the symbolic links to the tar file
        :type event: watchdog.events.FileSystemEvent
        :return: Nothing
        """
        if not self._controlled_change:
            self.log.info("Directory changed. Event: {0:}.".format(str(event)))
            try:
                self.tar_event_handler.controlled_change = True
                os.remove(self.tar_filename)
                with tarfile.open(self.tar_filename, "w:gz") as tar:
                    self.log.info("Compressed symbolic links directory {0:}.".format(self.symlinks_directory))
                    for fn in os.listdir(self.symlinks_directory):
                        tar.add(os.path.join(self.symlinks_directory, fn), arcname=fn)
                    tar.close()
            except Exception as xcpt:
                self.log.error("Error compressing symbolic links. Exception: {0:}.".format(str(xcpt)))
        else:
            self._controlled_change = False
        self.timer = None

    def on_any_event(self, event: watchdog.events.FileSystemEvent) -> None:
        """
        Event handler for any type of change in the symbolic links directory

        :param event: The event that generated the storage of the symbolic links to the tar file
        :type event: watchdog.events.FileSystemEvent
        :return: Nothing
        """
        if isinstance(event, DirModifiedEvent):
            if self.timer is not None:
                self.timer.cancel()
            self.timer = threading.Timer(0.5, self.compress, args=(event,))
            self.timer.start()


class TarEventHandler(FileSystemEventHandler):
    def __init__(self, tar_filename: str, symlinks_directory: str, log: logging.Logger) -> None:
        """
        Class creator

        :param tar_filename: Path with the filename of the tar file where the symbolic links are stored.
        :type tar_filename: str
        :param symlinks_directory: Path of the directory containing the symbolic links.
        :type symlinks_directory: str
        :param log: Logger to write the status or error messages.
        :type log: logging.Logger
        """
        super().__init__()
        self.tar_filename = tar_filename
        self.symlinks_directory = symlinks_directory
        self.log = log
        self.timer = None
        self._event_handler_symlinks = None
        self._controlled_change = False

    @property
    def symlink_event_handler(self) -> SymLinksEventHandler:
        """
        Property to store the symbolic links directory event handler reference

        :return: The symbolic links directory event handler reference
        :rtype: SymLinksEventHandler
        """
        return self._event_handler_symlinks

    @symlink_event_handler.setter
    def symlink_event_handler(self, event_handler_symlinks: SymLinksEventHandler):
        """
        Setter of the tar file event handler property

        :param event_handler_symlinks: The symbolic links directory event handler
        :type event_handler_symlinks: SymLinksEventHandler
        """
        self._event_handler_symlinks = event_handler_symlinks

    @property
    def controlled_change(self) -> bool:
        """
        Getter of the boolean that enables or disables the reaction of the handler to an event in the file system

        :return: True when the actual change is controlled by the main program and should be ignored, False otherwise.
        :rtype: bool
        """
        return self._controlled_change

    @controlled_change.setter
    def controlled_change(self, controlled_change: bool) -> None:
        """
        Enables or disables the reaction of the handler to an event in the file system

        :param controlled_change: True when the actual change is controlled by the main program and should be ignored,
        False otherwise.
        :type controlled_change: bool
        :return: Nothing
        """
        self._controlled_change = controlled_change

    def untar(self, event: watchdog.events.FileSystemEvent) -> None:
        """
        Method that extracts the tar file into the symbolic links directory

        :param event: The event that generated the untar execution
        :type event: watchdog.events.FileSystemEvent
        :return: Nothing
        """
        if not self._controlled_change:
            self.log.info("Tar file changed. Event: {0:}.".format(str(event)))
            try:
                with tarfile.open(self.tar_filename, "r:gz") as tar:
                    self._event_handler_symlinks.controlled_change = True
                    self.log.info("Extracting file {0:} with {1:} elements.".format(self.tar_filename,
                                                                                    len(tar.getnames())))
                    tar.extractall(self.symlinks_directory, members=tar.getmembers())
                    tar.close()
            except Exception as e:
                self.log.error("Failed to extract file {0:}. Error: {1:}".format(self.tar_filename, str(e)))
        else:
            self.controlled_change = False
        self.timer = None

    def on_modified(self, event):
        """
        Event handler for any type of change in the symbolic links directory

        :param event: The event that generated extraction the symbolic links tar file
        :type event: watchdog.events.FileSystemEvent
        :return: Nothing
        """
        if isinstance(event, FileModifiedEvent):
            if self.timer is not None:
                self.timer.cancel()
            self.timer = threading.Timer(0.5, self.untar, args=[event])
            self.timer.start()


def main(directory: str, tar_filename: str, log: logging.Logger, event: threading.Event, config_filename: str) -> None:
    """
    Main function that tests for the existence of the tar file and symlink directory, loads the configuration file and
    starts the file system observers

    :param directory: Path of the directory containing the symbolic links.
    :type directory: str
    :param tar_filename: Path with the filename of the tar file where the symbolic links are stored.
    :type tar_filename: str
    :param log: Logger to write the status or error messages.
    :type log: logging.Loger
    :param event: Event to stop the main thread and the observers threads.
    :type event: threading.Event
    :param config_filename: Configuration path and filename of the ini file containing the tar filenames and dates.
    :type config_filename: str
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

    # Load or creation of the configuration file
    tar_file_time = (datetime.datetime.utcfromtimestamp(int(os.path.getmtime(tar_filename))).
                     strftime('%Y-%m-%d %H:%M:%S'))
    config = configparser.ConfigParser()
    config.read(config_filename)
    if 'main' in config.sections():
        if tar_filename in config['main']:
            config_file_time = config['main'][tar_filename]
            tar_time = datetime.datetime.strptime(tar_file_time, '%Y-%m-%d %H:%M:%S')
            config_time = datetime.datetime.strptime(config_file_time, '%Y-%m-%d %H:%M:%S')
            if config_time < tar_time:
                log.info("Found newer tar file; config: {0:} - file: {1:}".format(config_file_time, tar_file_time))
                try:
                    with tarfile.open(tar_filename, "r:gz") as tar:
                        log.info("Extracting file {0:} with {1:} elements.".format(tar_filename, len(tar.getnames())))
                        tar.extractall(directory, members=tar.getmembers())
                        tar.close()
                    tar_file_time = (datetime.datetime.utcfromtimestamp(int(os.path.getmtime(tar_filename))).
                                     strftime('%Y-%m-%d %H:%M:%S'))
                    config.set('main', tar_filename, tar_file_time)
                    with open(config_filename, 'w') as f:
                        config.write(f)
                        f.close()
                except Exception as e:
                    log.error("Failed to extract file {0:}. Error: {1:}".format(tar_filename, str(e)))
        else:
            config.set('main', tar_filename, tar_file_time)
            with open(config_filename, 'w') as f:
                config.write(f)
                f.close()
    else:
        config.add_section('main')
        config.set('main', tar_filename, tar_file_time)
        with open(config_filename, 'w') as f:
            config.write(f)
            f.close()

    # Creation and start of the file system observers
    observer_tar_file = Observer()
    observer_directory = Observer()
    event_handler_dir = SymLinksEventHandler(tar_filename=tar_filename, symlinks_directory=directory, log=log)
    observer_directory.schedule(event_handler_dir, directory, recursive=False)
    event_handler_tar = TarEventHandler(tar_filename=tar_filename, symlinks_directory=directory, log=log)
    observer_tar_file.schedule(event_handler_tar, tar_filename, recursive=False)
    event_handler_dir.tar_event_handler = event_handler_tar
    event_handler_tar.symlink_event_handler = event_handler_dir
    observer_directory.start()
    observer_tar_file.start()
    try:
        while not event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:  # pragma: nocover
        pass
    finally:
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
        handler = RotatingFileHandler(args.log_file, mode='a', maxBytes=5*1024*1024, backupCount=15, encoding='utf-8',
                                      delay=False)
        logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s', handlers=[handler],
                            encoding='utf-8', level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S")
    else:
        handler = ch = logging.StreamHandler()
        logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s', handlers=[handler],
                            encoding='utf-8', level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S")

    # Set up the config file
    config_dir = os.path.dirname(os.path.realpath(__file__))
    config_file = os.path.join(config_dir, 'cloud_symlinks.ini')

    # Run the watchdogs
    main(args.dir, args.tar_file, logger, threading.Event(), config_file)
