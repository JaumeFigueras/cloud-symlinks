#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import logging


@pytest.fixture(scope='function')
def logger() -> logging.Logger:
    """
    Fixture to provide a log for testing purposes

    :return: A logger object
    :rtype: logging.Logger
    """
    return logging.getLogger('test_logger')
