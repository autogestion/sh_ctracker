# A federated Corruption Tracker

Corruption tracker module for [Socialhome](https://github.com/jaywink/socialhome),
based on stand-alone [Corruption tracker](https://github.com/autogestion/corruption_tracker) engine

Corruption tracker lets people to make cases of corruption and professionally unfit of civil servant public and as result track the level of it in public institutions.
Centralized server encountered with the problem, that it is hard to get together journalists, politicians and public organizations, they have different standards and requirements. So in federated version actors will aggregate claims on their own pods with their specific marketing strategy and share results using Diaspora protocol

FB - https://www.facebook.com/activecorruptiontracking/


## Quick start

1. Install prerequisites

    1.1 Intstall Socialhome using sh guides:

        http://socialhome.readthedocs.io/en/latest/development.html#development
        http://socialhome.readthedocs.io/en/latest/install_guides.html#install-guides

    1.2 Install postgis

        sudo apt-get install postgis

    1.3 On db creation, use next flow (or create extension postgis later):

        sudo su - postgres
        createuser -s -P socialhome  # give password 'socialhome'
        createdb -O socialhome socialhome
        psql
        \c socialhome;
        create extension postgis;
        \q    
        exit

    1.4 Install ctracker using pip

        pip install git+https://github.com/autogestion/sh_ctracker.git

        or symlink for development

        ln -s ~/.../sh_ctracker/ctracker/ ~/.../env/lib/python3.5/site-packages/ctracker

2. Configure project

    2.1 Edit .env file to add next values:

        -Update DATABASE_URL to next value (replace postgres with postgis):
        DATABASE_URL=postgis://socialhome:socialhome@127.0.0.1:5432/socialhome

        -Add 
        SOCIALHOME_HOME_VIEW=ctracker.views.MapPublicStreamView
        SOCIALHOME_ADDITIONAL_APPS=django.contrib.gis,ctracker
        SOCIALHOME_ADDITIONAL_APPS_URLS=ctracker/,ctracker.urls

    2.2 Run
    
        python manage.py migrate
        python manage.py initiate_db
        python manage.py createsuperuser  # with username 'acts', it will be used for broadcasting claims


API docs available on .../api/#/ctracker

## Submit a bug

We would like to hear about any bugs or odd behavior that you uncover. Use the [issue tracker](../../issues/) to open a new item. When describing the issue, we recommend that you discuss the following items:

  * Describe the bug
  * Describe the steps you did to discover the bug
  * What was the expected outcome of the above steps?
  * Please provide screenshots, if applicable     