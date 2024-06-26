#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tempfile
import pytest
import os
import tarfile
import os.path


@pytest.fixture(scope='function')
def blank_tar_file() -> str:
    """
    Fixture that provides a path to a blank (without any file inside) tar file.

    :return: The path to a blank tar file
    :rtype: str
    """
    temp_dir = tempfile.TemporaryDirectory()
    os.mkdir(os.path.join(temp_dir.name, 'tar'))
    with tarfile.open(os.path.join(os.path.join(temp_dir.name, 'tar'), 'test.tar.gz'), "w:gz") as tar:
        tar.close()

    yield os.path.join(os.path.join(temp_dir.name, 'tar'), 'test.tar.gz')

    temp_dir.cleanup()


@pytest.fixture(scope='function')
def one_file_tar_file() -> str:
    """
    Fixture to provide a path to a tar file with one file inside it.

    :return: The path to a blank tar file
    :rtype: str
    """
    temp_dir = tempfile.TemporaryDirectory()
    os.mkdir(os.path.join(temp_dir.name, 'tar'))
    with open(os.path.join(temp_dir.name, 'test.txt'), 'w') as f:
        f.write('hola')
        f.close()
        with tarfile.open(os.path.join(os.path.join(temp_dir.name, 'tar'), 'test.tar.gz'), "w:gz") as tar:
            tar.add(os.path.join(temp_dir.name, 'test.txt'), arcname='test.txt')
            tar.close()

    yield os.path.join(os.path.join(temp_dir.name, 'tar'), 'test.tar.gz')

    temp_dir.cleanup()
