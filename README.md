# A federated Corruption Tracker

Corruption tracker module for [Socialhome](https://github.com/jaywink/socialhome)
based on stand-alone [Corruption tracker](https://github.com/autogestion/corruption_tracker) engine

Corruption tracker lets you make cases of corruption and professionally unfit of civil servant public and as result track the level of it in public institutions

FB - https://www.facebook.com/activecorruptiontracking/


Quick start
-----------

0. Install Socialhome using sh guides
    http://socialhome.readthedocs.io/en/latest/development.html#development
    http://socialhome.readthedocs.io/en/latest/install_guides.html#install-guides

    And copy ctracker to project folder

1. Update frontend part

1.1 Install Vue2Leaflet
    npm install vue2-leaflet --save

1.1 Update webpack config

    -Add to module.exports
    map: path.resolve(__dirname, "ctracker/front_vue/map.js"),

2. Update Django part

2.1 Update settings in config/settings/common.py:

    -Add "ctracker" to your INSTALLED_APPS
    INSTALLED_APPS = [
        ...
        'ctracker',
    ]

    -Add
    str(ROOT_DIR.path("ctracker").path("templates"))  to
    TEMPLATES["DIRS"]

    -Add
    str(ROOT_DIR.path("ctracker").path("static"))  to
    STATICFILES_DIRS

2.2 Update URLconf in socialhome config/urls.py:

    -Add 
    from ctracker.views import MapHomeView

    -Replace url(r"^$", HomeView.as_view(), name="home"), with
    url(r"^$", MapHomeView.as_view(), name="home"),

    -Add
    url(r'^ctracker/', include('ctracker.urls')),
    

3. Run `python manage.py migrate` to create the ctracker models.
