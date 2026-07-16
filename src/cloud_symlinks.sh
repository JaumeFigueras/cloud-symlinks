#!/bin/bash
PATH=....
source /opt/cloud_symlinks/venv-cloud-symlinks/bin/activate
python /opt/cloud_symlinks/cloud_symlinks.py -d /home/jaume/dropbox/seguretat/biblioteca/zotero-links -f /home/jaume/dropbox/seguretat/biblioteca/zotero-tar/links.tar.gz -l /opt/cloud_symlinks/cloud_symlinks.log &
python /opt/cloud_symlinks/cloud_symlinks.py -d /home/jaume/dropbox/seguretat/biblioteca/zotero-data/storage -f /home/jaume/dropbox/seguretat/biblioteca/zotero-tar/links-zotero-v7.tar.gz -l /opt/cloud_symlinks/cloud_symlinks_v7.log -r &
