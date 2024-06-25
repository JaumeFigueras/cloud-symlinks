#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tempfile
import pytest
import logging

from src.cloud_symlinks import main


def test_dir_not_exist(caplog: pytest.LogCaptureFixture, logger: logging.Logger, temp_dir: str) -> None:
    with pytest.raises(SystemExit):
        main(temp_dir + '/symlinks', 'tar_file', logger)
        assert len(caplog.records) == 1
        for record in caplog.records:
            assert record.levelname == "ERROR"


def test_tar_file_not_exist(caplog: pytest.LogCaptureFixture, logger: logging.Logger, directory_symlink: str) -> None:
    with pytest.raises(SystemExit):
        main(directory_symlink, 'tar_file', logger)
        assert len(caplog.records) == 1
        for record in caplog.records:
            assert record.levelname == "ERROR"

