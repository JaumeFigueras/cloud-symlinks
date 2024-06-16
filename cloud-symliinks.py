#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import tarfile
import sys

from pathlib import Path
from typing import List
from typing import Dict


def main(dir: str, tar_file: str) -> None:
    pass


if __name__ == "__main__":  # pragma: no cover
    # Config the program arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir', help='Directory to tar', required=True)
    parser.add_argument('-f', '--tar-file', help='Location of the tar file containing ', required=True)
    args = parser.parse_args()

    # Get the data and store to the database
    main(args.dir, args.tar_file)
