#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import logging


@pytest.fixture(scope='function')
def logger() -> logging.Logger:
    return logging.getLogger('test_logger')

