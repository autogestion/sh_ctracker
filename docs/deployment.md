
# Federated Corruption Tracker Deployment in single Guide

Could be outdated due to updates in SocialHome

## Development Server

1 Install system packages

    sudo apt-get install git python-virtualenv python3-setuptools python-dev python3-dev build-essential \
     python-pip libpq-dev libxml2-dev libxslt-dev lib32z1-dev redis-server postgresql postgis

2 Create a database and user

    sudo su - postgres
    createuser -s -P socialhome  # give password 'socialhome'
    createdb -O socialhome socialhome
    psql
    \c socialhome;
    create extension postgis;
    \q
    exit

3 Install Python dependencies

    pip install virtualenvwrapper

    Add the following lines to your .bashrc and reload it via source ~/.bashrc

        export WORKON_HOME=$HOME/.virtualenvs
        source ~/.local/bin/virtualenvwrapper.sh
        export DJANGO_SETTINGS_MODULE=config.settings.production

    mkvirtualenv -p /usr/bin/python3 socialhome
    pip install -r dev-requirements.txt
    pip install git+https://github.com/autogestion/sh_ctracker.git

4 Create configuration

    Create the file .env with the following contents, replacing values as needed.

        DATABASE_URL=postgis://socialhome:socialhome@127.0.0.1:5432/socialhome

        DJANGO_SETTINGS_MODULE=config.settings.local
        DJANGO_SECRET_KEY=bbb
        DJANGO_ALLOWED_HOSTS=localhost
        DJANGO_SERVER_EMAIL=
        DJANGO_SECURE_SSL_REDIRECT=False
        DJANGO_ACCOUNT_ALLOW_REGISTRATION=True

        SOCIALHOME_DOMAIN=ctracker
        SOCIALHOME_HTTPS=False

        MOCHA_TESTS=True

        SOCIALHOME_HOME_VIEW=ctracker.views.MapPublicStreamView
        SOCIALHOME_ADDITIONAL_APPS=django.contrib.gis,ctracker
        SOCIALHOME_ADDITIONAL_APPS_URLS=ctracker/,ctracker.urls

5 Run

    python manage.py migrate
    python manage.py initiate_db
    python manage.py createsuperuser  # with username 'acts', it will be used for broadcasting claims
    python manage.py collectstatic
    python manage.py runserver 0.0.0.0:8000

    You can browse to http://localhost:8000 to see the Django instance running

6 Optional

    To verify user's emails

        python manage.py shell_plus

            EmailAddress.objects.all().update(verified=True)


