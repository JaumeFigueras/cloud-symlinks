#!/usr/bin/env python3
# -*- coding: utf-8 -*-

pytest_plugins = [
    'test.fixtures.logger',
    'test.fixtures.temp_dir',
    'test.fixtures.symlinks',
    'test.fixtures.tar_file',
]
