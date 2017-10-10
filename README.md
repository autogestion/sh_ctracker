# A federated Corruption Tracker

Corruption tracker module for [Socialhome](https://github.com/jaywink/socialhome)
based on stand-alone [Corruption tracker](https://github.com/autogestion/corruption_tracker) engine

Corruption tracker lets you make cases of corruption and professionally unfit of civil servant public and as result track the level of it in public institutions

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

     Clone ctracker and symlink it to socialhome project folder

2. Update frontend part

    2.1 Install Vue2Leaflet

        npm install vue2-leaflet --save

    2.1 Update webpack config

        -Add to module.exports

        map: path.resolve(__dirname, "ctracker/front_vue/map.js"),

3. Update Django part

    3.1 Update settings in config/settings/common.py:

        -Add "ctracker"  and 'django.contrib.gis' to your INSTALLED_APPS
        INSTALLED_APPS = [
            ...
            'django.contrib.gis',
            'ctracker',
            
        ]

        -Add
        str(ROOT_DIR.path("ctracker").path("templates"))  to
        TEMPLATES["DIRS"]

        -Add
        str(ROOT_DIR.path("ctracker").path("static"))  to
        STATICFILES_DIRS

        -Add
        DATABASES["default"]['ENGINE'] = 'django.contrib.gis.db.backends.postgis'
        after DATABASES definition

    3.2 Update URLconf in socialhome config/urls.py:

        -Add 
        from ctracker.views import MapHomeView

        -Replace url(r"^$", HomeView.as_view(), name="home"), with
        url(r"^$", MapHomeView.as_view(), name="home"),

        -Add
        url(r'^ctracker/', include('ctracker.urls')),
        

    3.3. Run
    
        python manage.py migrate
        python manage.py initiate_db


API docs available on /api/#/ctracker