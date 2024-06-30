#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import logging
import threading

from src.cloud_symlinks import main


def test_dir_not_exist(caplog: pytest.LogCaptureFixture, logger: logging.Logger, temp_dir: str,
                       empty_config_file: str) -> None:
    """
    Test to check that if the symbolic links directory does not exist, the program fails and write the error to the log

    :param caplog: Pytest log capture fixture
    :type caplog: pytest.LogCaptureFixture
    :param logger: Current logger to pass to the main program to write to.
    :type logger: logging.Logger
    :param empty_config_file: Path to an empty config file
    :type empty_config_file: str
    :return: Nothing
    """
    with pytest.raises(SystemExit):
        main(temp_dir + '/symlinks', 'tar_file', logger, threading.Event(), empty_config_file)
        assert len(caplog.records) == 1
        for record in caplog.records:
            assert record.levelname == "ERROR"


def test_tar_file_not_exist(caplog: pytest.LogCaptureFixture, logger: logging.Logger, directory_symlink: str,
                            empty_config_file: str) -> None:
    """
    Test to check that if the tar file does not exist, the program fails and write the error to the log

    :param caplog: Pytest log capture fixture
    :type caplog: pytest.LogCaptureFixture
    :param logger: Current logger to pass to the main program to write to.
    :type logger: logging.Logger
    :param directory_symlink: Path to the directory that contains the symbolic links
    :type directory_symlink: str
    :param empty_config_file: Path to an empty config file
    :type empty_config_file: str
    :return: Nothing
    """
    with pytest.raises(SystemExit):
        main(directory_symlink, 'tar_file', logger, threading.Event(), empty_config_file)
        assert len(caplog.records) == 1
        for record in caplog.records:
            assert record.levelname == "ERROR"
