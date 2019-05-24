#!/bin/sh


attachment-downloader --host ${DMARC_VIEWER_IMAP_HOST} --username ${DMARC_VIEWER_IMAP_USER} --password ${DMARC_VIEWER_IMAP_PASS} --imap-folder ${DMARC_VIEWER_IMAP_FOLDER} --output /imapbox

find /imapbox -type f -iname *.zip -exec unzip {} -d /imapbox \;

python manage.py parse --type in /imapbox

rm -Rf /imapbox/*