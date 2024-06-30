#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tempfile
import pytest
import os
import configparser


@pytest.fixture(scope='function')
def empty_config_file() -> str:
    """
    Provides the path to an empty config file to be used by configparser tools

    :return: The path to the empty config file as a string
    :rtype: str
    """
    temp_dir = tempfile.TemporaryDirectory()

    yield os.path.join(temp_dir.name, 'cloud_symlinks.ini')

    temp_dir.cleanup()


@pytest.fixture(scope='function')
def config_file_other() -> str:
    """
    Provides the path to a config file with one entry in the section main. It is aimed to be used by configparser tools

    :return: The path to the config file as a string
    :rtype: str
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
    Provides the path to a config file with one entry OF A TAR FILE in the section main. The date of the configured
    tar file is very old. It is aimed to be used by configparser tools

    :param one_file_tar_file: Fixture containing the path to a tar file with one file in it
    :type one_file_tar_file: str
    :return: The path to the config file as a string
    :rtype: str
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
