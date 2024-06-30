#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tempfile
import pytest
import logging
import threading
import time
import tarfile
import os

from src.cloud_symlinks import main


def test_changed_tar_file_01(caplog: pytest.LogCaptureFixture, logger: logging.Logger, directory_symlink: str,
                             blank_tar_file: str, empty_config_file: str) -> None:
    """
    Test to check the response of the Tar observer to a change in a blank tar file. The change consists of an addition
    of a file to the tar file. It is supposed that the observer will pick the change, and uncompress the tar file,
    resulting in a couple of INFO messages in the log and one file in the symbolic links directory

    :param caplog: Pytest log capture fixture
    :type caplog: pytest.LogCaptureFixture
    :param logger: Current logger to pass to the main program to write to.
    :type logger: logging.Logger
    :param directory_symlink: Path to the directory that contains the symbolic links
    :type directory_symlink: str
    :param blank_tar_file: Path to a blank tar file.
    :type blank_tar_file: str
    :param empty_config_file: Path to an empty config file
    :type empty_config_file: str
    :return: Nothing
    """
    event = threading.Event()
    caplog.set_level(logging.INFO)
    thread: threading.Thread = threading.Thread(target=main, args=(directory_symlink, blank_tar_file, logger, event,
                                                                   empty_config_file))
    thread.start()
    temp_dir = tempfile.TemporaryDirectory()
    f = open(os.path.join(temp_dir.name, 'test.txt'), 'w')
    f.write('hola')
    f.close()
    with tarfile.open(blank_tar_file, "w:gz") as tar:
        tar.add(os.path.join(temp_dir.name, 'test.txt'), arcname='test.txt')
        tar.close()
    time.sleep(1)
    event.set()
    time.sleep(2)
    assert not thread.is_alive()
    assert len(caplog.records) == 2
    for record in caplog.records:
        assert record.levelname == "INFO"
    assert len([name for name in os.listdir(directory_symlink) if os.path.isfile(os.path.join(directory_symlink,
                                                                                              name))]) == 1


def test_changed_tar_file_02(caplog: pytest.LogCaptureFixture, logger: logging.Logger, directory_symlink: str,
                             blank_tar_file: str, empty_config_file: str) -> None:
    """
    Test to check the response of the Tar observer to a change in a blank tar file. The change consists of two
    consecutive additions of a file to the tar file. It is supposed that the observer will pick the changes, program
    a timer to not take into account events close in time, and uncompress the tar file, when no more events are issued
    resulting in a couple of INFO messages in the log and one file in the symbolic links directory

    :param caplog: Pytest log capture fixture
    :type caplog: pytest.LogCaptureFixture
    :param logger: Current logger to pass to the main program to write to.
    :type logger: logging.Logger
    :param directory_symlink: Path to the directory that contains the symbolic links
    :type directory_symlink: str
    :param blank_tar_file: Path to a blank tar file.
    :type blank_tar_file: str
    :param empty_config_file: Path to an empty config file
    :type empty_config_file: str
    :return: Nothing
    """
    event = threading.Event()
    caplog.set_level(logging.INFO)
    thread: threading.Thread = threading.Thread(target=main, args=(directory_symlink, blank_tar_file, logger, event,
                                                                   empty_config_file))
    thread.start()
    temp_dir = tempfile.TemporaryDirectory()
    f = open(os.path.join(temp_dir.name, 'test-1.txt'), 'w')
    f.write('hola')
    f.close()
    f = open(os.path.join(temp_dir.name, 'test-2.txt'), 'w')
    f.write('hola')
    f.close()
    with tarfile.open(blank_tar_file, "w:gz") as tar:
        tar.add(os.path.join(temp_dir.name, 'test-1.txt'), arcname='test.txt')
        tar.close()
    with tarfile.open(blank_tar_file, "w:gz") as tar:
        tar.add(os.path.join(temp_dir.name, 'test-2.txt'), arcname='test.txt')
        tar.close()
    time.sleep(1)
    event.set()
    time.sleep(2)
    assert not thread.is_alive()
    assert len(caplog.records) == 2
    for record in caplog.records:
        assert record.levelname == "INFO"
    assert len([name for name in os.listdir(directory_symlink) if os.path.isfile(os.path.join(directory_symlink,
                                                                                              name))]) == 1


def test_changed_tar_file_03(caplog: pytest.LogCaptureFixture, logger: logging.Logger, directory_symlink: str,
                             blank_tar_file: str, empty_config_file: str) -> None:
    """
    Test to check the response of the Tar observer to a change in a blank tar file with some kind of problem during its
    process. The change consists of the addition of a file and the rename of the tar file. It is supposed that the
    observer will pick the changes and generate an exception resulting in an INFO message telling the change and an
    ERROR message with the exception.

    :param caplog: Pytest log capture fixture
    :type caplog: pytest.LogCaptureFixture
    :param logger: Current logger to pass to the main program to write to.
    :type logger: logging.Logger
    :param directory_symlink: Path to the directory that contains the symbolic links
    :type directory_symlink: str
    :param blank_tar_file: Path to a blank tar file.
    :type blank_tar_file: str
    :param empty_config_file: Path to an empty config file
    :type empty_config_file: str
    :return: Nothing
    """
    event = threading.Event()
    caplog.set_level(logging.INFO)
    thread: threading.Thread = threading.Thread(target=main, args=(directory_symlink, blank_tar_file, logger, event,
                                                                   empty_config_file))
    thread.start()
    time.sleep(2)
    with tarfile.open(blank_tar_file, "w:gz") as tar:
        tar.close()
    os.rename(blank_tar_file, blank_tar_file + '.bak')
    time.sleep(1)
    event.set()
    time.sleep(2)
    assert not thread.is_alive()
    assert len(caplog.records) == 2
    assert caplog.records[0].levelname == "INFO"
    assert caplog.records[1].levelname == "ERROR"
