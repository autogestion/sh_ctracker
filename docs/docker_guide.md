## Docker Quick start

sh-guide http://socialhome.readthedocs.io/en/latest/development.html#developing-with-docker

1. Install docker and docker-compose

    http://www.itzgeek.com/how-tos/linux/ubuntu-how-tos/how-to-install-docker-on-ubuntu-16-04.html
    https://docs.docker.com/compose/install/#install-compose

2. Configure project

    2.1 Copy and edit docker config

        -Copy
        cp docker/dev/docker-compose.yml.example ./docker-compose.yml

        -Replace in docker-compose.yml
            postgres:
              image: postgres:9.6
            to
            postgres:
              image: mdillon/postgis:9.6

            django:
              environment:
                DATABASE_URL=postgres://socialhome:socialhome@postgres:5432/socialhome
            to
            django:
              environment:
                DATABASE_URL=postgis://socialhome:socialhome@postgres:5432/socialhome

    2.2 Edit .env.example file to add next values:

        -Update variables:
            DATABASE_URL=postgis://socialhome:socialhome@127.0.0.1:5432/socialhome
            DJANGO_SECRET_KEY=verysecret
            DJANGO_ALLOWED_HOSTS=localhost

        -Add
            SOCIALHOME_HOME_VIEW=ctracker.views.MapPublicStreamView
            SOCIALHOME_ADDITIONAL_APPS=django.contrib.gis,ctracker
            SOCIALHOME_ADDITIONAL_APPS_URLS=ctracker/,ctracker.urls

    2.3 Edit socialhome/docker/dev/Dockerfile.django

        -Add after FROM python:3
            RUN apt-get update && \
              apt-get dist-upgrade -y && \
              apt-get install -y libgdal-dev && \
              apt-get clean && \
              rm -rf /var/lib/apt/lists*

    2.4 Copy ctracker to socialhome

        cp -a ~/.../sh_ctracker/ctracker/ ~/.../socialhome/ctracker

3. Run

        docker-compose build
        docker-compose run django manage migrate
        docker-compose run django manage initiate_db
        docker-compose run django manage createsuperuser  # with username 'acts', it will be used for broadcasting claims
        docker-compose up

4. You can browse to http://localhost:8000 to see the Django instance running