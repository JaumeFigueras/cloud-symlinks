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


@pytest.fixture(scope='function')
def directory_symlink_recursive() -> dict:
    """
    Provides a Zotero v7-like storage directory: item-key subfolders each holding a
    symlink to a real PDF in a sibling library folder, plus one stray symlink placed
    directly in the top level (which the recursive walk is expected to skip).

    :return: A dict with the storage 'directory', the list of relative 'arcnames'
        expected to be archived, and a 'targets' map from arcname to the symlink
        target path.
    :rtype: dict
    """
    temp_dir = tempfile.TemporaryDirectory()
    library = os.path.join(temp_dir.name, 'library')
    storage = os.path.join(temp_dir.name, 'storage')
    os.mkdir(library)
    os.mkdir(storage)

    targets = {}
    layout = {'ABCD1234': 'a.pdf', 'WXYZ9999': 'b.pdf'}
    for key, name in layout.items():
        pdf = os.path.join(library, name)
        with open(pdf, 'w') as f:
            f.write(name)
        os.mkdir(os.path.join(storage, key))
        link = os.path.join(storage, key, name)
        os.symlink(pdf, link)
        targets[os.path.join(key, name)] = pdf

    # Stray symlink directly in the top level: must NOT be archived.
    os.symlink(os.path.join(library, 'a.pdf'), os.path.join(storage, 'toplevel.pdf'))

    yield {
        'directory': storage,
        'arcnames': sorted(targets.keys()),
        'targets': targets,
    }

    temp_dir.cleanup()
