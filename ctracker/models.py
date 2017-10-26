import json
from pprint import pprint
import datetime

from django.db import connection
from django.contrib.gis.db import models
from django.db.models import Sum
from django.db.models import Count
from django.utils.translation import ugettext as _
# from django.utils.safestring import mark_safe
from django.core.cache import cache

from socialhome.content.models import Content
from socialhome.users.models import Profile

# from django.contrib.auth.models import User

# from claim.sql import moderation_filter
# from claim.sql import get_claims_for_poly, get_sum_for_layers

class Uploader(models.Model):

    json_file = models.FileField(upload_to='geojsons')

    def save(self, *args, **kwargs):
        if self.json_file:
            from utils.geoparser import GeoJSONParser
            geojson = json.loads(self.json_file.read().decode('utf8'))
            GeoJSONParser.geojson_to_db(geojson)

    def __str__(self):
        return self.json_file.name

    class Meta:
        verbose_name_plural = "Uploader"


class OrganizationType(models.Model):
    type_id = models.CharField(primary_key=True, max_length=155)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.type_id


class AddressException(Exception):
    pass


class Organization(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField(null=True, blank=True)
    org_type = models.ForeignKey(OrganizationType, null=True, blank=True)

    is_verified = models.BooleanField(default=True)
    updated = models.DateTimeField(auto_now=True)

    def moderation_filter(self):
        return self.claim_set.filter(
    #         moderation__in=Moderator.allowed_statuses()
    )

    def first_polygon(self):
        try:
            return self.polygon_set.all()[0]
        except IndexError:
            return None

    def polygons(self):
        polygons = None
        cached = cache.get('polygons_for::%s' % self.id)
        if cached is not None:
            polygons = cached
        else:
            polygons = self.polygon_set.all().values_list('polygon_id', flat=True)
            cache.set('polygons_for::%s' % self.id, polygons, 300)

        return polygons

    def address(self):
        try:
            cached = cache.get('address_for::%s' % self.id)
            if cached is not None:
                address = cached
            else:
                address = self.polygon_set.all()[0].address
                cache.set('address_for::%s' % self.id, address, 300)

            return address
        except IndexError:
            raise AddressException

    @property
    def claims(self):
        # return self.moderation_filter().count()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT COUNT(*) AS __count FROM claim_claim WHERE 
                (claim_claim.organization_id = %d AND %s );                   
            """ % (self.id, moderation_filter))

        return cursor.fetchone()[0]
  
    def __str__(self):
        return self.name


class Polygon(models.Model):
    """
    Polygon represent geo object,
    and could refer to collection of lower polygons
    """

    # Polygon as polygon
    polygon_id = models.CharField(max_length=50, primary_key=True)
    organizations = models.ManyToManyField(Organization, blank=True)
    shape = models.PolygonField(null=True, blank=True)
    centroid = models.PointField(null=True, blank=True)
    address = models.CharField(max_length=800, null=True, blank=True)
    layer = models.ForeignKey('self', blank=True, null=True)

    # Polygon as layer
    country = 0
    region = 1
    area = 2
    district = 3
    building = 4
    LEVEL = (
        (country, _("Root polygon")),
        (region, _("Regions of country")),
        (area, _("Subregions or big sities")),
        (district, _("Towns or districts of city")),
        (building, _("Houses"))
    )
    level = models.IntegerField(choices=LEVEL, default=building)
    
    is_verified = models.BooleanField(default=True)
    updated = models.DateTimeField(auto_now=True)

    objects = models.GeoManager()

    # moderation_filter
    @property
    def total_claims(self):
        claims = 0
        if self.level == self.building:
            # claims += sum([x.claims for x in self.organizations.all()])
            # claims =  self.organizations.filter(claim__moderation__in=Moderator.allowed_statuses()).count()
            claims = get_claims_for_poly(self.polygon_id)
        else:
            # cached = cache.get('claims_for::%s' % self.polygon_id)
            cached = None
            if cached is not None:
                claims = cached
            else:
                # childs = self.polygon_set.all()
                # for child in childs:
                    # claims += child.total_claims
                try:
                    claims = get_sum_for_layers([self.polygon_id], self.level)[self.polygon_id]
                except KeyError:
                    claims = 0

                # cache.set('claims_for::%s' % self.polygon_id, claims, 300)
        return claims

    @staticmethod
    def color_spot(value, max_value):
        if max_value:
            percent = value * 100 / max_value
        else:
            percent = 0

        if percent <= 20:
            return 'green'
        elif percent <= 70:
            return 'yellow'
        else:
            return 'red'

    def first_organization(self):
        orgs = self.organizations.all()
        if orgs:
            return orgs[0]
        else:
            return None

    def __str__(self):
        return 'Polygon ' + str(self.polygon_id)


class Claim(Content):
    organization = models.ForeignKey(Organization)
    servant = models.CharField(max_length=550)
    complainer = models.ForeignKey(Profile, null=True, blank=True, default=None)  
    bribe = models.IntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        super(Claim, self).save(*args, **kwargs)
        key = 'color_for::%s' % self.organization.first_polygon().polygon_id
        if cache.has_key(key):
            cache.delete(key)