#script to detect distance between two points based on lat and long 

#based on Haversine formula that cauclates the shortest distance between two points on the surface of a sphere

from math import radians, sin, cos, asin, sqrt

def haversine_km(lat1,lon1, lat2, lon2):
    """Straight-line distance between two points on Earth via haversine formula"""
    dlat = radians(lat2-lat1)
    dlon = radians(lon2-lon1)
    r = 6371 #radius of the earth
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon)**2
    distance = 2*asin(sqrt(a))
    return distance