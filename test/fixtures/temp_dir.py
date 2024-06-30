#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tempfile
import pytest


@pytest.fixture(scope='function')
def temp_dir() -> str:
    """
    Fixture that provides a path to a temporary directory

    :return: The path to a temporary directory as a string
    :rtype: str
    """
    temp_dir = tempfile.TemporaryDirectory()

    yield temp_dir.name

    temp_dir.cleanup()
