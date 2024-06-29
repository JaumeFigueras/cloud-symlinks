#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tempfile
import pytest


@pytest.fixture(scope='function')
def temp_dir() -> str:
    """
    TODO:

    :return:
    """
    temp_dir = tempfile.TemporaryDirectory()

    yield temp_dir.name

    temp_dir.cleanup()
