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


def test_changed_tar_file(caplog: pytest.LogCaptureFixture, logger: logging.Logger, directory_symlink: str, blank_tar_file: str) -> None:
    event = threading.Event()
    caplog.set_level(logging.INFO)
    thread: threading.Thread = threading.Thread(target=main, args=(directory_symlink, blank_tar_file, logger, event))
    thread.start()
    time.sleep(1)
    temp_dir = tempfile.TemporaryDirectory()
    f = open(os.path.join(temp_dir.name, 'test.txt'), 'w')
    f.write('hola')
    f.close()
    with tarfile.open(blank_tar_file, "w:gz") as tar:
        tar.add(temp_dir.name, arcname=os.path.join(temp_dir.name, 'test.txt'))
        tar.close()
    time.sleep(1)
    event.set()
    time.sleep(2)
    assert not thread.is_alive()
    assert len(caplog.records) == 1
    for record in caplog.records:
        assert record.levelname == "INFO"



