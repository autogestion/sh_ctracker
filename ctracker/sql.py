from django.db import connection


claim_to_polygon_join = """    
    LEFT OUTER JOIN ctracker_polygon_organizations  ON (houses.polygon_id = ctracker_polygon_organizations.polygon_id) 
    LEFT OUTER JOIN ctracker_organization ON (ctracker_polygon_organizations.organization_id = ctracker_organization.id) 
    LEFT OUTER JOIN ctracker_claim ON (ctracker_organization.id = ctracker_claim.organization_id)
"""


def get_claims_for_poly(polygon_id):
        cursor = connection.cursor()
        cursor.execute("""
            SELECT COUNT(*) AS "__count" FROM "ctracker_organization" 
                INNER JOIN "ctracker_polygon_organizations" ON ("ctracker_organization"."id" = "ctracker_polygon_organizations"."organization_id") 
                INNER JOIN "ctracker_claim" ON ("ctracker_organization"."id" = "ctracker_claim"."organization_id") 
                WHERE ("ctracker_polygon_organizations"."polygon_id" = '%s')                        
            """ % polygon_id)

        return cursor.fetchone()[0]


def get_sum_for_layers(layers_ids, level):
    cursor = connection.cursor()
    if level==4:
        cursor.execute("""
            SELECT ctracker_organization.id, COUNT(ctracker_claim.content_ptr_id) AS claims FROM ctracker_organization 
                LEFT OUTER JOIN ctracker_claim ON (ctracker_organization.id = ctracker_claim.organization_id) 
                WHERE (ctracker_organization.id IN (%s) )
                GROUP BY ctracker_organization.id                 
            """ % ','.join([str(x) for x in layers_ids])
            )

    elif level==3:
        cursor.execute("""
            SELECT district_id, SUM(claimz) as sum_claims FROM 
                (SELECT houses.layer_id as district_id, COUNT(ctracker_claim.content_ptr_id) AS claimz FROM ctracker_polygon houses                    
                    %s
                    WHERE (houses.layer_id IN (%s) )
                    GROUP BY houses.polygon_id ) x
                GROUP BY district_id
        """ % (claim_to_polygon_join, ','.join(["'" + str(x) + "'" for x in layers_ids]))
        )

    elif level==2:
        cursor.execute("""
            SELECT area_id, SUM(claimz) as sum_claims FROM 
                (SELECT districts.layer_id as area_id, COUNT(ctracker_claim.content_ptr_id) AS claimz FROM ctracker_polygon districts
                    LEFT OUTER JOIN ctracker_polygon houses  ON (houses.layer_id = districts.polygon_id)                    
                    %s
                    WHERE (districts.layer_id IN (%s) )
                    GROUP BY districts.polygon_id ) x
                GROUP BY area_id
        """ % (claim_to_polygon_join, ','.join(["'" + str(x) + "'" for x in layers_ids]))
        )

    elif level==1:
        cursor.execute("""
            SELECT region_id, SUM(claimz) as sum_claims FROM 
                (SELECT areas.layer_id as region_id, COUNT(ctracker_claim.content_ptr_id) AS claimz FROM ctracker_polygon areas                
                    LEFT OUTER JOIN ctracker_polygon districts ON (districts.layer_id = areas.polygon_id)   
                    LEFT OUTER JOIN ctracker_polygon houses ON (houses.layer_id = districts.polygon_id)                     
                    %s
                    WHERE (areas.layer_id IN (%s) )
                    GROUP BY areas.polygon_id ) x
                GROUP BY region_id
        """ % (claim_to_polygon_join, ','.join(["'" + str(x) + "'" for x in layers_ids]))
        )

    elif level==0:
        cursor.execute("""
            SELECT root_id, SUM(claimz) as sum_claims FROM 
                (SELECT regions.layer_id as root_id, COUNT(ctracker_claim.content_ptr_id) AS claimz FROM ctracker_polygon regions
                    LEFT OUTER JOIN ctracker_polygon areas ON (areas.layer_id = regions.polygon_id)                
                    LEFT OUTER JOIN ctracker_polygon districts ON (districts.layer_id = areas.polygon_id)   
                    LEFT OUTER JOIN ctracker_polygon houses ON (houses.layer_id = districts.polygon_id)                     
                    %s
                    WHERE (regions.layer_id IN (%s) )
                    GROUP BY regions.polygon_id ) x
                GROUP BY root_id
        """ % (claim_to_polygon_join, ','.join(["'" + str(x) + "'" for x in layers_ids]))
        )


    return dict(cursor.fetchall())


def get_max_for_layers(layer_id, level):
    layers_dict = {}
    cursor = connection.cursor()

    if level==4:
        # x = Polygon.objects.filter(layer_id=layer_id).annotate(claimz=Count('organizations__claim')) 
        
        cursor.execute("""
            SELECT layer_id, MAX(claimz) FROM 
                (SELECT houses.layer_id as layer_id, COUNT(ctracker_claim.content_ptr_id) AS claimz FROM ctracker_polygon houses 
                        %s
                        WHERE (houses.layer_id IN (%s) )
                        GROUP BY houses.polygon_id ) x
                GROUP BY layer_id
        """ % (claim_to_polygon_join, ','.join(["'" + str(x) + "'" for x in layer_id]))
        )

    elif level==3:
        cursor = connection.cursor()
        cursor.execute("""
                SELECT district_id, MAX(claimz) as sum_claims FROM (
                    SELECT districts.layer_id as district_id, COUNT(ctracker_claim.content_ptr_id) AS claimz FROM ctracker_polygon districts
                            LEFT OUTER JOIN ctracker_polygon houses  ON (houses.layer_id = districts.polygon_id) 
                            %s
                            WHERE (districts.layer_id IN (%s) )
                            GROUP BY districts.polygon_id) x
                    GROUP BY district_id
        """ % (claim_to_polygon_join, ','.join(["'" + str(x) + "'" for x in layer_id]))
        )       

    elif level==2:
        cursor.execute("""
                SELECT district_id, MAX(claimz) as sum_claims FROM (
                    SELECT areas.layer_id as district_id, COUNT(ctracker_claim.content_ptr_id) AS claimz FROM ctracker_polygon areas
                            LEFT OUTER JOIN ctracker_polygon districts  ON (districts.layer_id = areas.polygon_id)
                            LEFT OUTER JOIN ctracker_polygon houses  ON (houses.layer_id = districts.polygon_id) 
                            %s
                            WHERE (areas.layer_id IN (%s) )
                            GROUP BY areas.polygon_id) x
                    GROUP BY district_id
        """ % (claim_to_polygon_join, ','.join(["'" + str(x) + "'" for x in layer_id]))
        )

    elif level==1:
        cursor.execute("""
                SELECT district_id, MAX(claimz) as sum_claims FROM (
                    SELECT regions.layer_id as district_id, COUNT(ctracker_claim.content_ptr_id) AS claimz FROM ctracker_polygon regions
                            LEFT OUTER JOIN ctracker_polygon areas  ON (areas.layer_id = regions.polygon_id)
                            LEFT OUTER JOIN ctracker_polygon districts  ON (districts.layer_id = areas.polygon_id)
                            LEFT OUTER JOIN ctracker_polygon houses  ON (houses.layer_id = districts.polygon_id)
                            %s
                            WHERE (regions.layer_id IN (%s) )
                            GROUP BY regions.polygon_id) x
                    GROUP BY district_id
        """ % (claim_to_polygon_join, ','.join(["'" + str(x) + "'" for x in layer_id]))
        )

    return dict(cursor.fetchall())