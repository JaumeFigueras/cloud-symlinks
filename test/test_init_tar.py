#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import tarfile

import pytest

from src import init_tar
from src.init_tar import collect_symlinks
from src.init_tar import build_tar


def test_collect_symlinks_recursive(directory_symlink_recursive: dict) -> None:
    """
    Test that the recursive collection returns the symlinks found in the subfolders
    as relative arcnames and skips any symlink placed directly in the top level,
    mirroring SymLinksEventHandler.compress().

    :param directory_symlink_recursive: Fixture with a Zotero v7-like storage layout
    :type directory_symlink_recursive: dict
    :return: Nothing
    """
    entries = collect_symlinks(directory_symlink_recursive['directory'], recursive=True)

    assert sorted(entries) == directory_symlink_recursive['arcnames']
    assert 'toplevel.pdf' not in entries


def test_collect_symlinks_non_recursive(directory_symlink_recursive: dict) -> None:
    """
    Test that the non-recursive collection returns every entry directly inside the
    directory (the item-key subfolders and the stray top-level symlink), as os.listdir
    would report them.

    :param directory_symlink_recursive: Fixture with a Zotero v7-like storage layout
    :type directory_symlink_recursive: dict
    :return: Nothing
    """
    entries = collect_symlinks(directory_symlink_recursive['directory'], recursive=False)

    assert sorted(entries) == sorted(os.listdir(directory_symlink_recursive['directory']))
    assert 'toplevel.pdf' in entries


def test_build_tar_recursive_contents(directory_symlink_recursive: dict, blank_tar_file: str) -> None:
    """
    Test that building the tar file recursively stores exactly the expected relative
    arcnames, that each member is stored as a symlink (not dereferenced into a copy of
    the file), and that the stored link target matches the original.

    :param directory_symlink_recursive: Fixture with a Zotero v7-like storage layout
    :type directory_symlink_recursive: dict
    :param blank_tar_file: Path to a blank tar file used as the destination
    :type blank_tar_file: str
    :return: Nothing
    """
    entries = build_tar(directory_symlink_recursive['directory'], blank_tar_file, recursive=True)

    assert sorted(entries) == directory_symlink_recursive['arcnames']
    with tarfile.open(blank_tar_file, 'r:gz') as tar:
        members = {m.name: m for m in tar.getmembers()}
    assert sorted(members.keys()) == directory_symlink_recursive['arcnames']
    for arcname, target in directory_symlink_recursive['targets'].items():
        assert members[arcname].issym()
        assert members[arcname].linkname == target


def test_build_tar_roundtrip_extract(directory_symlink_recursive: dict, blank_tar_file: str,
                                     directory_symlink: str) -> None:
    """
    Test that a tar built by build_tar extracts back into the expected subfolder
    structure as symlinks pointing at the original targets, i.e. it is compatible with
    the daemon's extraction path.

    :param directory_symlink_recursive: Fixture with a Zotero v7-like storage layout
    :type directory_symlink_recursive: dict
    :param blank_tar_file: Path to a blank tar file used as the destination
    :type blank_tar_file: str
    :param directory_symlink: Empty directory to extract into
    :type directory_symlink: str
    :return: Nothing
    """
    build_tar(directory_symlink_recursive['directory'], blank_tar_file, recursive=True)

    with tarfile.open(blank_tar_file, 'r:gz') as tar:
        tar.extractall(directory_symlink)

    for arcname, target in directory_symlink_recursive['targets'].items():
        extracted = os.path.join(directory_symlink, arcname)
        assert os.path.islink(extracted)
        assert os.readlink(extracted) == target


def test_main_creates_tar(directory_symlink_recursive: dict, blank_tar_file: str,
                          monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture) -> None:
    """
    Test that invoking main() writes the archive and reports the number of symlinks.
    The blank tar file is removed first so main() creates it from scratch.

    :param directory_symlink_recursive: Fixture with a Zotero v7-like storage layout
    :type directory_symlink_recursive: dict
    :param blank_tar_file: Path to a blank tar file (removed before the run)
    :type blank_tar_file: str
    :param monkeypatch: Pytest monkeypatch fixture to set the argv
    :type monkeypatch: pytest.MonkeyPatch
    :param capsys: Pytest capture fixture to read stdout
    :type capsys: pytest.CaptureFixture
    :return: Nothing
    """
    os.remove(blank_tar_file)
    monkeypatch.setattr(sys, 'argv', ['init_tar.py', '-d', directory_symlink_recursive['directory'],
                                      '-f', blank_tar_file, '-r'])

    init_tar.main()

    assert os.path.isfile(blank_tar_file)
    with tarfile.open(blank_tar_file, 'r:gz') as tar:
        assert sorted(tar.getnames()) == directory_symlink_recursive['arcnames']
    assert '2 symlink(s)' in capsys.readouterr().out


def test_main_refuses_existing_tar(directory_symlink_recursive: dict, blank_tar_file: str,
                                   monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test that main() refuses to overwrite an existing tar file unless --force is given.

    :param directory_symlink_recursive: Fixture with a Zotero v7-like storage layout
    :type directory_symlink_recursive: dict
    :param blank_tar_file: Path to an already existing tar file
    :type blank_tar_file: str
    :param monkeypatch: Pytest monkeypatch fixture to set the argv
    :type monkeypatch: pytest.MonkeyPatch
    :return: Nothing
    """
    monkeypatch.setattr(sys, 'argv', ['init_tar.py', '-d', directory_symlink_recursive['directory'],
                                      '-f', blank_tar_file, '-r'])

    with pytest.raises(SystemExit) as exc:
        init_tar.main()
    assert exc.value.code == 1


def test_main_force_overwrites_existing_tar(directory_symlink_recursive: dict, blank_tar_file: str,
                                            monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test that main() overwrites an existing tar file when --force is supplied.

    :param directory_symlink_recursive: Fixture with a Zotero v7-like storage layout
    :type directory_symlink_recursive: dict
    :param blank_tar_file: Path to an already existing (blank) tar file
    :type blank_tar_file: str
    :param monkeypatch: Pytest monkeypatch fixture to set the argv
    :type monkeypatch: pytest.MonkeyPatch
    :return: Nothing
    """
    monkeypatch.setattr(sys, 'argv', ['init_tar.py', '-d', directory_symlink_recursive['directory'],
                                      '-f', blank_tar_file, '-r', '--force'])

    init_tar.main()

    with tarfile.open(blank_tar_file, 'r:gz') as tar:
        assert sorted(tar.getnames()) == directory_symlink_recursive['arcnames']


def test_main_missing_dir(blank_tar_file: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test that main() exits with an error when the source directory does not exist.

    :param blank_tar_file: Path to a tar file destination
    :type blank_tar_file: str
    :param monkeypatch: Pytest monkeypatch fixture to set the argv
    :type monkeypatch: pytest.MonkeyPatch
    :return: Nothing
    """
    os.remove(blank_tar_file)
    monkeypatch.setattr(sys, 'argv', ['init_tar.py', '-d', '/does/not/exist',
                                      '-f', blank_tar_file, '-r'])

    with pytest.raises(SystemExit) as exc:
        init_tar.main()
    assert exc.value.code == 1
    assert not os.path.exists(blank_tar_file)


def test_main_missing_destination_dir(directory_symlink_recursive: dict,
                                      monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test that main() exits with an error when the tar file's destination directory does
    not exist, rather than silently failing to write.

    :param directory_symlink_recursive: Fixture with a Zotero v7-like storage layout
    :type directory_symlink_recursive: dict
    :param monkeypatch: Pytest monkeypatch fixture to set the argv
    :type monkeypatch: pytest.MonkeyPatch
    :return: Nothing
    """
    destination = os.path.join(directory_symlink_recursive['directory'], 'nope', 'links.tar.gz')
    monkeypatch.setattr(sys, 'argv', ['init_tar.py', '-d', directory_symlink_recursive['directory'],
                                      '-f', destination, '-r'])

    with pytest.raises(SystemExit) as exc:
        init_tar.main()
    assert exc.value.code == 1
