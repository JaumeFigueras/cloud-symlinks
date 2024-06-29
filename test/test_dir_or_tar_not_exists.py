#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import logging
import threading

from src.cloud_symlinks import main


def test_dir_not_exist(caplog: pytest.LogCaptureFixture, logger: logging.Logger, temp_dir: str, empty_config_file: str) -> None:
    """
    TODO:

    :param caplog:
    :param logger:
    :param temp_dir:
    :param empty_config_file:
    :return:
    """
    with pytest.raises(SystemExit):
        main(temp_dir + '/symlinks', 'tar_file', logger, threading.Event(), empty_config_file)
        assert len(caplog.records) == 1
        for record in caplog.records:
            assert record.levelname == "ERROR"


def test_tar_file_not_exist(caplog: pytest.LogCaptureFixture, logger: logging.Logger, directory_symlink: str, empty_config_file: str) -> None:
    """
    TODO:

    :param caplog:
    :param logger:
    :param directory_symlink:
    :param empty_config_file:
    :return:
    """
    with pytest.raises(SystemExit):
        main(directory_symlink, 'tar_file', logger, threading.Event(), empty_config_file)
        assert len(caplog.records) == 1
        for record in caplog.records:
            assert record.levelname == "ERROR"

