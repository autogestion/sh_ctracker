import os

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings

from ctracker.geoparser import GeoJSONParser
from ctracker.models import Polygon

class Command(BaseCommand):
    help = 'Fullfill database with basic data'

    def handle(self, *args, **options):

        # call_command('loaddata', 'initial_data')
        geo_path = str(settings.ROOT_DIR.path("ctracker").path("init_geo_data"))

        geofilenames = os.listdir(geo_path)
        fullpathes = [os.path.join(geo_path,
                      x) for x in geofilenames if x.endswith('.geojson')]
        geojsons = list(map(GeoJSONParser.get_geojson_file, fullpathes))
        geojsons.sort(key=lambda x: x['ctracker_config']['AL'])
        list(map(GeoJSONParser.geojson_to_db, geojsons))
