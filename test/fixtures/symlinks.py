#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tempfile
import pytest
import os


@pytest.fixture(scope='function')
def directory_symlink() -> str:
    """
    Provides a fixture with the directory where the symbolic links are stored

    :return: The path of the symbolic links directory as a string
    :rtype: str
    """
    temp_dir = tempfile.TemporaryDirectory()
    os.mkdir(os.path.join(temp_dir.name, 'symlinks'))

    yield os.path.join(temp_dir.name, 'symlinks')

    temp_dir.cleanup()
