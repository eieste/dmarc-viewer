# DMARC viewer

Version v0.16.0


`DMARC viewer` is a [Django](https://docs.djangoproject.com/en/1.11/)-based web
application that lets you visually analyze [DMARC aggregate
reports](https://dmarc.org/), providing unique insights into how your mailing
domains are used and abused. Moreover, with `DMARC viewer` you can create and
store custom `analysis views` that filter reports based on the criteria you are
interested in.

## Live Demo
A  `DMARC viewer` demo is available at
[dmarc-viewer.abteil.org](https://dmarc-viewer.abteil.org).


## Configure DNS
To **receive DMARC aggregate reports** for your domains all you need to do is
to add a DMARC entry to your DNS records. Read [*"Anatomy of a DMARC resource
record in the DNS"*](https://dmarc.org/overview/) for initial guidance.


## Start Analyzing!
To analyze your own DMARC aggregate reports you need to deploy an instance of
`DMARC viewer`. Follow these steps to get you started:

 1. [Deploy](DEPLOYMENT.md) your own instance of `DMARC viewer`,
 1. [import](REPORTS.md) DMARC aggregate reports,
 1. and [create `analysis views`](ANALYSIS_VIEWS.md).

Alternatively you can deploy [`DMARC viewer` using docker](DOCKER.md).

You'll find further usage instructions on the
[`DMARC viewer` help page](https://dmarc-viewer.abteil.org/help/) and plenty of
contextual help throughout the website (look out for "**`?`**" symbols).

## Contribute
`DMARC viewer` is an open source project [*(MIT)*](LICENSE). If you want a new
feature, discover a bug or have some general feedback, feel free to file an
[*issue*](https://github.com/dmarc-viewer/dmarc-viewer/issues). You can also
[*fork*](https://help.github.com/articles/fork-a-repo/) this repository,
[**start coding**](CONTRIBUTE.md) and submit [*pull
requests*](https://github.com/dmarc-viewer/dmarc-viewer/pulls).


## Configuration
This is a fork from the orgina [Project](https://github.com/dmarc-viewer/dmarc-viewer)
which means that this project can load emails from a mailbox and analyze them automatically.
This project also works with the modified GeoLite2 Database.
To use this project you need a free license key from [maxmind.com](https://maxmind.com) (To download the GeoLite2 City database)

**Configuration Variables**
 * DMARC_VIEWER_ALLOWED_HOSTS=127.0.0.1;localhost
 * DMARC_VIEWER_SECRET_KEY=arandomkey
 * DMARC_VIEWER_DB_HOST=database
 * DMARC_VIEWER_DB_NAME=dmarc-viewer
 * DMARC_VIEWER_DB_USER=dmarc-viewer
 * DMARC_VIEWER_DB_PASS=NOTASECRET
 * DMARC_VIEWER_DB_ENGINE=django.db.backends.mysql
 * DMARC_VIEWER_IMAP_HOST=mailhost.com
 * DMARC_VIEWER_IMAP_USER=dmarcreports@mail.com
 * DMARC_VIEWER_IMAP_PASS=NOTASECRET
 * DMARC_VIEWER_IMAP_FOLDER=INBOX
 * GEOIP_LICENSE_IP
