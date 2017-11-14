import os

from django.core.management.base import BaseCommand

from ctracker.geoparser import GeoJSONParser


class Command(BaseCommand):
    help = 'Fullfill database with basic data'

    def handle(self, *args, **options):

        path = os.path.abspath(os.path.dirname(__file__))
        geo_path = os.path.join(path, "../../init_geo_data/")

        geofilenames = os.listdir(geo_path)
        fullpathes = [os.path.join(geo_path,
                      x) for x in geofilenames if x.endswith('.geojson')]
        geojsons = list(map(GeoJSONParser.get_geojson_file, fullpathes))
        geojsons.sort(key=lambda x: x['ctracker_config']['AL'])
        list(map(GeoJSONParser.geojson_to_db, geojsons))
