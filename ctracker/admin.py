
from django.contrib.gis import admin

from ctracker.models import Uploader
from ctracker.models import Polygon
from ctracker.models import Organization
from ctracker.models import OrganizationType
from ctracker.models import ClaimType
from ctracker.models import Claim


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'org_type',
                    'first_polygon', 'claims', 'url',
                    'updated', 'is_verified')
    search_fields = ('name',)
    list_filter = ('org_type',)


class OrganizationTypeAdmin(admin.ModelAdmin):
    list_display = ('type_id', 'name')
    search_fields = ('type_id', 'name')


class ClaimTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'linked_org_types')
    search_fields = ('name',)


class PolygonAdmin(admin.OSMGeoAdmin):

    list_display = ('polygon_id', 'layer',
                    'first_organization', 'address',
                    # 'total_claims',
                    # 'claims',
                    'centroid', 'level',
                    'is_verified',
                    'updated')
    search_fields = ('polygon_id', 'address')
    list_filter = ('level', 'is_verified')


class ClaimAdmin(admin.ModelAdmin):
    list_display = ('id', 'organization', 'servant',
                    'claim_type', 'text',
                    'complainer', 'bribe',)
    search_fields = ('organization', 'servant', 'text')
    list_filter = ('organization',)


admin.site.register(Uploader)
admin.site.register(Polygon, PolygonAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(OrganizationType, OrganizationTypeAdmin)
admin.site.register(ClaimType, ClaimTypeAdmin)
admin.site.register(Claim, ClaimAdmin)
