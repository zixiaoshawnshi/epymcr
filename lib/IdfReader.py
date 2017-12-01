"""
This is the simple idf reader for Model-Cluster-Reduce BPS model reduction process,
using eppy and some custom objects

developed by Zixiao Shi at the Department of Civil and Environmental Engineering at
Carleton University, Ottawa Canada
"""

from eppy.modeleditor import IDF
from lib.Models import Wall, Zone

__author__ = 'Zixiao(Shawn) Shi'


def read_idf(fname, iddfile="lib/V8-5-0-Energy+.idd"):
    IDF.setiddname(iddfile)
    idf = IDF(fname)

    zones = {}

    for zone in idf.idfobjects["ZONE"]:
        zone_obj = Zone(zone.Name, "Zone", zone.Floor_Area)
        zone_obj.equipmentLoad = 0.0
        zone_obj.occupancy = 0.0
        zone_obj.lightingLoad = 0.0
        zone_obj.wallClasses = []
        zones[zone.Name] = zone_obj

