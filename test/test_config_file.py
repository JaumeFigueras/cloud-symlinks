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


def test_config_file_01(caplog: pytest.LogCaptureFixture, logger: logging.Logger, directory_symlink: str, blank_tar_file: str, empty_config_file: str) -> None:
    """
    TODO:

    :param caplog:
    :param logger:
    :param directory_symlink:
    :param blank_tar_file:
    :param empty_config_file:
    :return:
    """
    event = threading.Event()
    caplog.set_level(logging.INFO)
    thread: threading.Thread = threading.Thread(target=main, args=(directory_symlink, blank_tar_file, logger, event, empty_config_file))
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


def test_config_file_02(caplog: pytest.LogCaptureFixture, logger: logging.Logger, directory_symlink: str, blank_tar_file: str, config_file_other: str) -> None:
    """
    TODO:

    :param caplog:
    :param logger:
    :param directory_symlink:
    :param blank_tar_file:
    :param config_file_other:
    :return:
    """
    event = threading.Event()
    caplog.set_level(logging.INFO)
    thread: threading.Thread = threading.Thread(target=main, args=(directory_symlink, blank_tar_file, logger, event, config_file_other))
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


def test_config_file_03(caplog: pytest.LogCaptureFixture, logger: logging.Logger, directory_symlink: str, one_file_tar_file: str, config_file: str) -> None:
    """
    TODO:

    :param caplog:
    :param logger:
    :param directory_symlink:
    :param one_file_tar_file:
    :param config_file:
    :return:
    """
    event = threading.Event()
    caplog.set_level(logging.INFO)
    thread: threading.Thread = threading.Thread(target=main, args=(directory_symlink, one_file_tar_file, logger, event, config_file))
    thread.start()
    time.sleep(2)
    event.set()
    time.sleep(2)
    assert not thread.is_alive()
    assert len(caplog.records) == 2
    for record in caplog.records:
        assert record.levelname == "INFO"
    assert len([name for name in os.listdir(directory_symlink) if os.path.isfile(os.path.join(directory_symlink, name))]) == 1
    assert os.path.exists(config_file)
    config = configparser.ConfigParser()
    config.read(config_file)
    assert len(config.sections()) == 1
    assert config.has_section('main')
    assert one_file_tar_file in config['main']
    assert config['main'][one_file_tar_file].startswith(datetime.datetime.utcnow().strftime("%Y-%m-%d"))


def test_config_file_04(caplog: pytest.LogCaptureFixture, logger: logging.Logger, directory_symlink: str, one_file_tar_file: str, config_file: str) -> None:
    """
    TODO:

    :param caplog:
    :param logger:
    :param directory_symlink:
    :param one_file_tar_file:
    :param config_file:
    :return:
    """
    event = threading.Event()
    caplog.set_level(logging.INFO)
    os.chmod(directory_symlink, 0o444)
    thread: threading.Thread = threading.Thread(target=main, args=(directory_symlink, one_file_tar_file, logger, event, config_file))
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
