#!/bin/sh
set -x -e

if [ ! -f "GeoLite2-City.mmdb.gz" ]; then
    wget -O GeoLite2-City.mmdb.gz https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-City\&license_key=${GEOIP_LICENSE_IP}\&suffix=tar.gz
    gunzip GeoLite2-City.mmdb.gz
fi



# NOTE: Below management commands are no-ops if they ran before
# Populate initial DMARC viewer db model
>&2 echo "Setup DB"
python manage.py makemigrations website --noinput
python manage.py migrate --noinput

# Collect and copy required static web assets
# (see sdmarc_viewer.ettings.STATIC_ROOT)
>&2 echo "Collect and move static files"
python manage.py collectstatic --noinput

# Change cache dir ownership (see dmarc-viewer/dmarc-viewer#10)
# The cache dir is created when running `makemigrations` above (as root), but
# the uwsgi daemon is running with `UWSGI_UID` (see Dockerfile)
chown ${UWSGI_UID} /var/tmp/django_cache

while true; do sh /code/imap-importer.sh; sleep 300; done &


exec "$@"
