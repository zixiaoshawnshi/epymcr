"""
Some custom objects

developed by Zixiao Shi at the Department of Civil and Environmental Engineering at
Carleton University, Ottawa Canada

"""
import math


class Wall(object):
    def __init__(self, name, area, azimuth, zone_name):

        self.name = name
        self.area = area
        self.azimuth = azimuth
        self.zone_name = zone_name




class Zone(object):
    def __init__(self, name, type, area):
        self.name = name
        self.type = type
        self.area = area
        self.wallEast = 0.0
        self.wallWest = 0.0
        self.wallSouth = 0.0
        self.wallNorth = 0.0
        self.winEast = 0.0
        self.winWest = 0.0
        self.winSouth = 0.0
        self.winNorth = 0.0
        self.wallClasses = []
        self.equipmentLoad = 0.0
        self.lightingLoad = 0.0
        self.occupancy = 0.0
        self.infiltration = 0.0

    def AddWallClustered(self, walltype):
        self.wallClasses.append(walltype)
        self.wallClasses.sort()

    def projectWall(self, surface):
        if surface.azimuth < 90 or surface.azimuth > 270:
            self.wallNorth += math.cos(toRad(surface.azimuth)) * surface.area
        if surface.azimuth < 180 or surface.azimuth > 0:
            self.wallEast += math.cos(toRad(surface.azimuth-90)) * surface.area
        if surface.azimuth < 270 or surface.azimuth > 90:
            self.wallSouth += math.cos(toRad(surface.azimuth-180)) * surface.area
        if surface.azimuth < 360 or surface.azimuth > 180:
            self.wallWest += math.cos(toRad(surface.azimuth-270)) * surface.area

def toRad(deg):
    return math.pi*(deg/180.0)