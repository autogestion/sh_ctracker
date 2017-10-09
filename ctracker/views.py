
from django.views.generic import TemplateView
from django.contrib.gis import geos
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.response import Response

from socialhome.streams.views import PublicStreamView

from ctracker import serializers
from ctracker.models import Polygon


class MapPublicStreamView(PublicStreamView):
    template_name = "map_public.html"


class MapHomeView(TemplateView):
    template_name = "map_base.html"

    def get(self, request, *args, **kwargs):
        return MapPublicStreamView.as_view()(request)


class FitBoundsPolygons(viewsets.ViewSet):
    """
    API endpoint for getting polygons
    that fit to bounds (_coordinates_ in W, S, E, N).

    - to get polygons, use .../polygon/fit_bounds/_layer_/_coordinates_

    Available layers:
        region = 1
        area = 2
        district = 3
        building = 4

    Example:  .../polygon/fit_bounds/4/2.81,18.15,86.04,60.89/

    .

    - to search polygon by addres in polygons that fit bounds,
    use .../polygon/fit_bounds/_layer_/_coordinates_/?search=_value_

    Example:  .../polygon/fit_bounds/4/2.81,18.15,86.04,60.89/?search=студ

    .
    """

    polygon = 'fit_bounds'

    def retrieve(self, request, layer, coord):

        raw = [x for x in coord.split(',')]
        area_coord = ((raw[0], raw[1]), (raw[0], raw[3]), (raw[2], raw[3]),
                      (raw[2], raw[1]), (raw[0], raw[1]))

        area_coord_str = ', '.join([' '.join(x) for x in area_coord])
        area = geos.GEOSGeometry('POLYGON ((%s))' % area_coord_str)

        # if settings.DISPLAY_DISTRICTS and int(layer) == 4:
        #     queryset = Polygon.objects.filter(
        #         Q(shape__bboverlaps=area) | Q(centroid__within=area),
        #         level__in=[3, 4])
        # else:
        queryset = Polygon.objects.filter(
            Q(shape__bboverlaps=area) | Q(centroid__within=area),
            level=int(layer))

        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(address__icontains=search)

        # db_start = time.time()
        geodata = list(queryset.prefetch_related('organizations'))
        # print('  get polygon and orgs(sql)', time.time() - db_start)

        # serializer_start = time.time()
        serializer = serializers.PolygonSerializer(geodata, many=True)
        data = serializer.data
        # print('  serialization', time.time() - serializer_start)

        return Response(data)

        # serializer = PolygonSerializer(queryset.prefetch_related('organizations'), many=True)
        # return Response(serializer.data)        