#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import pytest
import logging
import threading
import time
import os
import datetime

from src.cloud_symlinks import main


def test_config_file_01(caplog: pytest.LogCaptureFixture, logger: logging.Logger, directory_symlink: str,
                        blank_tar_file: str, empty_config_file: str) -> None:
    """
    Test to check the creation of the config file if it does not exist. The main function should create it and add an
    entry in the main section of the date of the added tar file. As Freezegun can freeze the date of the test but not
    the fixtures, the test just checks that the date of the config file is OK.

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
    event.set()
    time.sleep(2)
    assert not thread.is_alive()
    assert len(caplog.records) == 0
    assert os.path.exists(empty_config_file)
    config = configparser.ConfigParser()
    config.read(empty_config_file)
    assert len(config.sections()) == 1
    assert config.has_section('main')
    assert blank_tar_file in config['main']


def test_config_file_02(caplog: pytest.LogCaptureFixture, logger: logging.Logger, directory_symlink: str,
                        blank_tar_file: str, config_file_other: str) -> None:
    """
    Test to check the read of the config file with an entry different from the current tar file. The main function
    should add an  entry in the main section of the date of the added tar file. As Freezegun can freeze the date of
    the test but not the fixtures, the test just checks that the date of the config file is OK.

    :param caplog: Pytest log capture fixture
    :type caplog: pytest.LogCaptureFixture
    :param logger: Current logger to pass to the main program to write to.
    :type logger: logging.Logger
    :param directory_symlink: Path to the directory that contains the symbolic links
    :type directory_symlink: str
    :param blank_tar_file: Path to a blank tar file.
    :type blank_tar_file: str
    :param config_file_other: Path to a config file with one entry different from the current tar file
    :type config_file_other: str
    :return: Nothing
    """
    event = threading.Event()
    caplog.set_level(logging.INFO)
    thread: threading.Thread = threading.Thread(target=main, args=(directory_symlink, blank_tar_file, logger, event,
                                                                   config_file_other))
    thread.start()
    time.sleep(1)
    event.set()
    time.sleep(2)
    assert not thread.is_alive()
    assert len(caplog.records) == 0
    assert os.path.exists(config_file_other)
    config = configparser.ConfigParser()
    config.read(config_file_other)
    assert len(config.sections()) == 1
    assert config.has_section('main')
    assert blank_tar_file in config['main']


def test_config_file_03(caplog: pytest.LogCaptureFixture, logger: logging.Logger, directory_symlink: str,
                        one_file_tar_file: str, config_file: str) -> None:
    """
    Test to check the update of the config file with an entry of the current tar file. The main function should update
    the date it and uncompress the tar file in the symbolic links' directory. As Freezegun can freeze the date of the
    test but not the fixtures, the test just checks that the date of the config file is OK.

    :param caplog: Pytest log capture fixture
    :type caplog: pytest.LogCaptureFixture
    :param logger: Current logger to pass to the main program to write to.
    :type logger: logging.Logger
    :param directory_symlink: Path to the directory that contains the symbolic links
    :type directory_symlink: str
    :param one_file_tar_file: Path to a tar file with files inside.
    :type one_file_tar_file: str
    :param config_file: Path to a config file with the current tar file information
    :type config_file: str
    :return: Nothing
    """
    event = threading.Event()
    caplog.set_level(logging.INFO)
    thread: threading.Thread = threading.Thread(target=main, args=(directory_symlink, one_file_tar_file, logger, event,
                                                                   config_file))
    thread.start()
    time.sleep(2)
    event.set()
    time.sleep(2)
    assert not thread.is_alive()
    assert len(caplog.records) == 2
    for record in caplog.records:
        assert record.levelname == "INFO"
    assert len([name for name in os.listdir(directory_symlink) if os.path.isfile(os.path.join(directory_symlink,
                                                                                              name))]) == 1
    assert os.path.exists(config_file)
    config = configparser.ConfigParser()
    config.read(config_file)
    assert len(config.sections()) == 1
    assert config.has_section('main')
    assert one_file_tar_file in config['main']
    assert config['main'][one_file_tar_file].startswith(datetime.datetime.utcnow().strftime("%Y-%m-%d"))


def test_config_file_04(caplog: pytest.LogCaptureFixture, logger: logging.Logger, directory_symlink: str,
                        one_file_tar_file: str, config_file: str) -> None:
    """
    Test to check the update of the config file with an entry of the current tar file, but with an error during the
    extraction. The main function should not update the date it as the uncompress process fails.

    :param caplog: Pytest log capture fixture
    :type caplog: pytest.LogCaptureFixture
    :param logger: Current logger to pass to the main program to write to.
    :type logger: logging.Logger
    :param directory_symlink: Path to the directory that contains the symbolic links
    :type directory_symlink: str
    :param one_file_tar_file: Path to a tar file with files inside.
    :type one_file_tar_file: str
    :param config_file: Path to a config file with the current tar file information
    :type config_file: str
    :return: Nothing
    """
    event = threading.Event()
    caplog.set_level(logging.INFO)
    os.chmod(directory_symlink, 0o444)
    thread: threading.Thread = threading.Thread(target=main, args=(directory_symlink, one_file_tar_file, logger, event,
                                                                   config_file))
    thread.start()
    time.sleep(2)
    event.set()
    time.sleep(2)
    assert not thread.is_alive()
    assert len(caplog.records) == 3
    for record in caplog.records[0:1]:
        assert record.levelname == "INFO"
    assert caplog.records[2].levelname == "ERROR"
    assert os.path.exists(config_file)
    config = configparser.ConfigParser()
    config.read(config_file)
    assert len(config.sections()) == 1
    assert config.has_section('main')
    assert one_file_tar_file in config['main']
    assert config['main'][one_file_tar_file] == "2020-01-01 15:16:17"
