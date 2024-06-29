#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tempfile
import pytest
import os
import configparser


@pytest.fixture(scope='function')
def empty_config_file() -> str:
    """
    TODO:
    :return:
    """
    temp_dir = tempfile.TemporaryDirectory()

    yield os.path.join(temp_dir.name, 'cloud_symlinks.ini')

    temp_dir.cleanup()


@pytest.fixture(scope='function')
def config_file_other() -> str:
    """
    TODO:
    :return:
    """
    temp_dir = tempfile.TemporaryDirectory()
    config_filename = os.path.join(temp_dir.name, 'cloud_symlinks.ini')
    config = configparser.ConfigParser()
    config.add_section('main')
    config.set('main', '/a/b/c', '2020-01-01 15:16:17')
    with open(config_filename, 'w') as f:
        config.write(f)
        f.close()

    yield config_filename

    temp_dir.cleanup()


@pytest.fixture(scope='function')
def config_file(one_file_tar_file: str) -> str:
    """
    TODO:
    :param one_file_tar_file:
    :return:
    """
    temp_dir = tempfile.TemporaryDirectory()
    config_filename = os.path.join(temp_dir.name, 'cloud_symlinks.ini')
    config = configparser.ConfigParser()
    config.add_section('main')
    config.set('main', one_file_tar_file, '2020-01-01 15:16:17')
    with open(config_filename, 'w') as f:
        config.write(f)
        f.close()

    yield config_filename

    temp_dir.cleanup()
