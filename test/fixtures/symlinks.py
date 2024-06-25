#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tempfile
import pytest
import os


@pytest.fixture(scope='function')
def directory_symlink() -> str:
    temp_dir = tempfile.TemporaryDirectory()
    os.mkdir(os.path.join(temp_dir.name, 'symlinks'))

    yield os.path.join(temp_dir.name, 'symlinks')

    temp_dir.cleanup()
