# A federated Corruption Tracker

Corruption tracker module for [Socialhome](https://github.com/jaywink/socialhome)
Based on stand-alone [Corruption tracker](https://github.com/autogestion/corruption_tracker) engine

Corruption tracker lets you make cases of corruption and professionally unfit of civil servant public and as result track the level of it in public institutions

FB - https://www.facebook.com/activecorruptiontracking/


Quick start
-----------
1. Add "ctracker" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'ctracker',
    ]

2. Include the ctracker URLconf in socialhome project urls.py like this::

    url(r'^ctracker/', include('ctracker.urls')),

3. Run `python manage.py migrate` to create the ctracker models.
