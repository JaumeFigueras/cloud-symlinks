#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tempfile
import pytest
import os
import tarfile
import os.path


@pytest.fixture(scope='function')
def blank_tar_file() -> str:
    temp_dir = tempfile.TemporaryDirectory()
    with tarfile.open(os.path.join(temp_dir.name, 'test.tar.gz'), "w:gz") as tar:
        tar.close()

    yield os.path.join(temp_dir.name, 'test.tar.gz')

    temp_dir.cleanup()
