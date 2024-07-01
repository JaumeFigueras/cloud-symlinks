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


def test_changed_symlink_directory_01(caplog: pytest.LogCaptureFixture, logger: logging.Logger, directory_symlink: str,
                                      blank_tar_file: str, empty_config_file: str) -> None:
    """
    Test to check the response of the Symlink observer to a change in the directory. The change consists of an addition
    of 10 files. It is supposed that the observer will pick the change, and compress all the directory

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
    for i in range(10):
        f = open(os.path.join(directory_symlink, "test-{0:}.txt".format(i)), 'w')
        f.write('hola')
        f.close()
    time.sleep(1)
    event.set()
    time.sleep(2)
    assert not thread.is_alive()
    assert len(caplog.records) == 2
    for record in caplog.records:
        assert record.levelname == "INFO"
    temp_dir = tempfile.TemporaryDirectory()
    with tarfile.open(blank_tar_file, "r:gz") as tar:
        tar.extractall(temp_dir.name,  members=tar.getmembers())
        tar.close()
    assert len(os.listdir(temp_dir.name)) == 10


def test_changed_symlink_directory_02(caplog: pytest.LogCaptureFixture, logger: logging.Logger, directory_symlink: str,
                                      blank_tar_file: str, empty_config_file: str) -> None:
    """
    Test to check the response of the Symlink observer to a change in the directory but forcing an error. The change
    consists of an addition of 10 files but the tar file is renamed to generate an exception. It is supposed that the
    observer will pick the change, and generate an error into the log telling the directory can't be compressed using
    the tar file

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
    time.sleep(1)
    os.rename(blank_tar_file, blank_tar_file + '.bak')
    for i in range(10):
        f = open(os.path.join(directory_symlink, "test-{0:}.txt".format(i)), 'w')
        f.write('hola')
        f.close()
    time.sleep(1)
    event.set()
    time.sleep(2)
    assert not thread.is_alive()
    assert len(caplog.records) == 2
    assert caplog.records[0].levelname == "INFO"
    assert caplog.records[1].levelname == "ERROR"


def test_changed_symlink_directory_03(caplog: pytest.LogCaptureFixture, logger: logging.Logger, directory_symlink: str,
                                      blank_tar_file: str, empty_config_file: str) -> None:
    """
    Test to check the response of the Symlink observer to a change in the directory. The change consists of a deletion
    of 2 of the existing 10 files. It is supposed that the observer will pick the change, and compress all the directory

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
    for i in range(10):
        f = open(os.path.join(directory_symlink, "test-{0:}.txt".format(i)), 'w')
        f.write('hola')
        f.close()
    thread: threading.Thread = threading.Thread(target=main, args=(directory_symlink, blank_tar_file, logger, event,
                                                                   empty_config_file))
    thread.start()
    time.sleep(1)
    for i in range(2):
        os.remove(os.path.join(directory_symlink, "test-{0:}.txt".format(i)))
    time.sleep(1)
    event.set()
    time.sleep(2)
    assert not thread.is_alive()
    assert len(caplog.records) == 2
    for record in caplog.records:
        assert record.levelname == "INFO"
    temp_dir = tempfile.TemporaryDirectory()
    with tarfile.open(blank_tar_file, "r:gz") as tar:
        tar.extractall(temp_dir.name,  members=tar.getmembers())
        tar.close()
    assert len(os.listdir(temp_dir.name)) == 8


def test_changed_symlink_directory_04(caplog: pytest.LogCaptureFixture, logger: logging.Logger, directory_symlink: str,
                                      blank_tar_file: str, empty_config_file: str) -> None:
    """
    Test to check the response of the Symlink observer to a change in the directory. The change consists of a rename
    of 2 of the existing 10 files. It is supposed that the observer will pick the change, and compress all the directory

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
    for i in range(10):
        f = open(os.path.join(directory_symlink, "test-{0:}.txt".format(i)), 'w')
        f.write('hola')
        f.close()
    thread: threading.Thread = threading.Thread(target=main, args=(directory_symlink, blank_tar_file, logger, event,
                                                                   empty_config_file))
    thread.start()
    time.sleep(1)
    for i in range(2):
        os.rename(os.path.join(directory_symlink, "test-{0:}.txt".format(i)),
                  os.path.join(directory_symlink, "test-{0:}.txt.bak".format(i)))
    time.sleep(1)
    event.set()
    time.sleep(2)
    assert not thread.is_alive()
    assert len(caplog.records) == 2
    for record in caplog.records:
        assert record.levelname == "INFO"
    temp_dir = tempfile.TemporaryDirectory()
    with tarfile.open(blank_tar_file, "r:gz") as tar:
        tar.extractall(temp_dir.name,  members=tar.getmembers())
        tar.close()
    assert len(os.listdir(temp_dir.name)) == 10


def test_changed_symlink_directory_05(caplog: pytest.LogCaptureFixture, logger: logging.Logger, directory_symlink: str,
                                      blank_tar_file: str, empty_config_file: str) -> None:
    """
    Test to check the response of the Symlink observer to a change in the directory. The change consists of an update
    of 2 of the existing 10 files. It is supposed that the observer will pick the change, and compress all the directory

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
    for i in range(10):
        f = open(os.path.join(directory_symlink, "test-{0:}.txt".format(i)), 'w')
        f.write('hola')
        f.close()
    thread: threading.Thread = threading.Thread(target=main, args=(directory_symlink, blank_tar_file, logger, event,
                                                                   empty_config_file))
    thread.start()
    time.sleep(1)
    for i in range(2):
        f = open(os.path.join(directory_symlink, "test-{0:}.txt".format(i)), 'a')
        f.write(' + hola')
        f.close()
    time.sleep(1)
    event.set()
    time.sleep(2)
    assert not thread.is_alive()
    assert len(caplog.records) == 2
    for record in caplog.records:
        assert record.levelname == "INFO"
    temp_dir = tempfile.TemporaryDirectory()
    with tarfile.open(blank_tar_file, "r:gz") as tar:
        tar.extractall(temp_dir.name,  members=tar.getmembers())
        tar.close()
    assert len(os.listdir(temp_dir.name)) == 10
