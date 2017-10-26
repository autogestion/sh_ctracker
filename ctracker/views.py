
from django.views.generic import TemplateView
from django.contrib.gis import geos
from django.db.models import Q
from django.db.models import Count
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import filters
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import list_route
from rest_framework.decorators import detail_route

from socialhome.streams.views import PublicStreamView
from socialhome.users.models import Profile

from ctracker.models import Polygon
from ctracker.models import Organization
from ctracker.models import OrganizationType
from ctracker.models import Claim
from ctracker.serializers import PolygonSerializer
from ctracker.serializers import OrganizationSerializer
from ctracker.serializers import OrganizationTypeSerializer
from ctracker.serializers import ClaimSerializer


class MapPublicStreamView(PublicStreamView):
    template_name = "ctracker_map.html"


class ClaimViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):

    queryset = Claim.objects.all().order_by('-created')
    serializer_class = ClaimSerializer

    lookup_field = 'id'


    def get_by_id(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)        

    @detail_route()
    def user(self, request, id=None):
        """
        return claims for given user id (web)

        Example:  .../claim/2/user/
        """         
        queryset = self.queryset.filter(complainer__id=id)
        return self.get_by_id(queryset)


    @detail_route()
    def broadcaster(self, request, id=None):
        """
        return claims for given broadcaster id (web)

        Example:  .../claim/3/broadcaster/        
        """         
        queryset = self.queryset.filter(author__id=id)
        return self.get_by_id(queryset)


    def retrieve(self, request, id=None):
        """
        return claims for given organization id (web)

        Example:  .../claim/13/
        """         
        # queryset = self.queryset.filter(organization__id=id)
        organization = Organization.objects.get(id=id)
        queryset = organization.moderation_filter(
            ).select_related().annotate(num_c=Count(
                'complainer__claim')).order_by('created')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, org_or_user='org')
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, org_or_user='org')
        return Response(serializer.data)

    def create(self, request):
        """
        add claim for given organization id (web)

        required fields - 'text', 'organization', 'servant', 'claim_type'

        optional  fields - 'live', 'bribe', 'anonymously':'on'

        Example:

        { "text": "Покусали комарі",
        "claim_type": "2",
        "servant": "Бабця",
        "organization": "13",
        "bribe": "50" }
        """          
        return super(ClaimViewSet, self).create(request)

    def perform_create(self, serializer):
        author = Profile.objects.get(user__username='acts')
        if self.request.user.is_anonymous() or self.request.data.get('anonymously', None):
            serializer.save(complainer=None, author=author)
        else:
            serializer.save(complainer=self.request.user.profile, author=author) 


class OrganizationViewSet(mixins.ListModelMixin,
                          viewsets.GenericViewSet):

    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    lookup_field = 'polygon_id'

    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    @list_route()
    def orgtypes(self, request):
        """
        return list of organization types with availaible claim types (web)

        for organization and claim creation forms
        """
        org_types = OrganizationType.objects.all()
        serializer = OrganizationTypeSerializer(org_types, many=True)
        return Response(serializer.data)

    def list(self, request):
        """
        search organizations by name (web)

        Example:  .../organization/?search=прок
        """
        search = self.request.query_params.get('search', None)
        if search:
            return super(OrganizationViewSet, self).list(request)
        else:
            return Response('can be used only with ?search=')

    def retrieve(self, request, polygon_id=None):
        """
        return organizations for polygon (web)

        Example:  .../organization/21citzhovt0002/
        """
        queryset = Organization.objects.filter(polygon__polygon_id=polygon_id)
        serializer = OrganizationSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        """
        add organization with polygon (or marker) (web)

        Example parameters with building shape:

        {"shape": "{'type': 'Polygon', 'coordinates': [ [ [ 36.296753463843954,
            50.006170131432199 ], [ 36.296990304344928, 50.006113443092367 ],
            [ 36.296866409713009, 50.005899627208827 ], [ 36.296629569212049,
            50.00595631580083 ], [ 36.296753463843954, 50.006170131432199 ] ] ]}",
        "org_type": "prosecutors",
        "layer_id": "21citzhovt",
        "address": "Shevshenko street, 3",
        "org_name": "Ministry of defence",
        "centroid": "36.2968099,50.0060348",
        "polygon_id": "mindef"}

        Example parameters for marker:

        {"org_type": "prosecutors",
        "layer_id": "21citzhovt",
        "address": "Shevshenko street, 3",
        "org_name": "Ministry of defence",
        "centroid": "36.2968099,50.0060348",
        "polygon_id": "mindef"}

        """

        parent_polygon_id = request.data.get('parent_polygon_id', None)
        polygon_id = request.data.get('polygon_id', None)
        level = request.data.get('level', None)
        centroid = request.data['centroid']
        centroid_pnt = geos.fromstr("POINT(%s %s)" % tuple(centroid.split(',')))

        layer = None
        if parent_polygon_id:
            layer = Polygon.objects.get(polygon_id=parent_polygon_id)
        else:
            districts = Polygon.objects.filter(shape__contains=centroid_pnt,
                                               level=Polygon.district)
            if districts:
                layer = districts[0]

        if not polygon_id:
            polygon_id = centroid

        if not level:
            level = Polygon.building

        polygon = Polygon(
            polygon_id=polygon_id,
            centroid=centroid_pnt,
            shape=request.data.get('shape', None),
            address=request.data['address'],
            layer=layer,
            level=level,
            is_verified=False)
        polygon.save()

        org_type = OrganizationType.objects.get(
            type_id=request.data['org_type'])

        organization = Organization(
            name=request.data['org_name'],
            org_type=org_type,
            is_verified=False)
        organization.save()

        polygon.organizations.add(organization)

        serializer = self.get_serializer(organization)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FitBoundsPolygons(viewsets.ViewSet):

    polygon = 'fit_bounds'

    def retrieve(self, request, layer, coord):
        """
        return polygons that fit to bounds (coordinates in W, S, E, N). (web)

        Available layers:

        region = 1, area = 2, district = 3, building = 4

        Example:  .../polygon/fit_bounds/4/2.81,18.15,86.04,60.89/

        to search polygon by addres in polygons that fit bounds,
        use .../polygon/fit_bounds/_layer_/_coordinates_/?search=_value_

        Example:  .../polygon/fit_bounds/4/2.81,18.15,86.04,60.89/?search=студ
        """

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
        serializer = PolygonSerializer(geodata, many=True)
        data = serializer.data
        # print('  serialization', time.time() - serializer_start)

        return Response(data)

        # serializer = PolygonSerializer(queryset.prefetch_related('organizations'), many=True)
        # return Response(serializer.data)        