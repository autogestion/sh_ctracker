
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from ctracker import views


class CustomRouter(DefaultRouter):

    def get_lookup_regex(self, viewset, lookup_prefix=''):
        if getattr(viewset, 'polygon', False):
            if viewset.polygon == 'get_nearest':
                return '(?P<layer>\d+)/(?P<distance>.*)/(?P<coord>.*)'
            elif viewset.polygon in ['check_in', 'fit_bounds']:
                return '(?P<layer>\d+)/(?P<coord>.*)'

        return super(CustomRouter,
                     self).get_lookup_regex(viewset, lookup_prefix)

router = CustomRouter()

router.register(r'claim', views.ClaimViewSet,
                base_name='claims')
router.register(r'organization', views.OrganizationViewSet,
                base_name='organizations')
# router.register(r'polygon', geoinfo.PolygonViewSet,
#                 base_name='polygon')
# router.register(r'polygon/get_nearest', geoinfo.GetNearestPolygons,
#                 base_name='get_nearest')
router.register(r'polygon/fit_bounds', views.FitBoundsPolygons,
                base_name='fit_bounds')
# router.register(r'polygon/check_in', geoinfo.CheckInPolygon,
#                 base_name='check_in')
# router.register(r'polygon/get_tree', geoinfo.GetPolygonsTree,
#                 base_name='get_polygons')
# router.register(r'update', views.GetUpdatedViewSet,
#                 base_name='updated')

urlpatterns = router.urls