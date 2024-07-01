#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from src.cloud_symlinks import SymLinksEventHandler
from src.cloud_symlinks import TarEventHandler


def test_properties_01(logger: logging.Logger):
    """
    Test to check the read and write of properties of the directory and tar event handlers

    :param logger: Current logger to pass to the main program to write to.
    :type logger: logging.Logger
    """
    event_handler_dir = SymLinksEventHandler(tar_filename="tar", symlinks_directory="dir", log=logger)
    event_handler_tar = TarEventHandler(tar_filename="tar", symlinks_directory="dir", log=logger)
    event_handler_dir.tar_event_handler = event_handler_tar
    event_handler_tar.symlink_event_handler = event_handler_dir
    event_handler_tar.controlled_change = True
    assert event_handler_tar.controlled_change
    event_handler_dir.controlled_change = True
    assert event_handler_dir.controlled_change
    event_handler_tar.controlled_change = False
    assert not event_handler_tar.controlled_change
    event_handler_dir.controlled_change = False
    assert not event_handler_dir.controlled_change
    assert event_handler_tar.symlink_event_handler == event_handler_dir
    assert event_handler_dir.tar_event_handler == event_handler_tar
