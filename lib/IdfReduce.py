"""
This is the reduce procedure for Model-Cluster-Reduce BPS model reduction process,
developed by Zixiao Shi at the Department of Civil and Environmental Engineering at
Carleton University, Ottawa Canada

"""
from operator import itemgetter


def reduce(idf, centers, labels, output, normalization_method ="Area"):

    # First by generating a dictionary of values used for zone normalization
    # The scale factor of archetype zones can be calculated by using
    # floor area, volume or simple zone count

    zones = {}
    if normalization_method == "Area":
        for zone in idf.idfobjects["ZONE"]:
            zones[zone.Name] = [zone.Floor_Area, zone.Type]
    elif normalization_method == "Volume":
        for zone in idf.idfobjects["ZONE"]:
            zones[zone.Name] = [zone.Volume, zone.Type]
    elif normalization_method == "Constant":
        for zone in idf.idfobjects["ZONE"]:
            zones[zone.Name] = [1.0, zone.Type]
    else:
        raise NameError("Normalization method incorrect, use Area, Volume or Constant")

    # lists of zone normalization values and names
    zone_values = list(zones.values())
    names = itemgetter(*centers)(list(zones.keys()))

    # Calculate total baseline value for each archetype zone
    tot_value = {}
    tot_value_sum = 0
    tot_value_sum_labeled = 0
    size = len(labels)

    for i in range(0, size):
        label = labels[i]
        if label not in tot_value.keys():
            tot_value[label] = 0
            tot_value_sum += zone_values[i][0]
        else:
            tot_value[label] += zone_values[i][0]
            tot_value_sum += zone_values[i][0]
            tot_value_sum_labeled += zone_values[i][0]

    # Calculate zone multipliers for archetype zones
    # based on baseline values calculated previously

    multipliers = {}
    for label in range(0, len(tot_value)):
        multiplier = ((tot_value[label] + zone_values[centers[label]][0]) / zone_values[centers[label]][0])
        multiplier = multiplier * (tot_value_sum / tot_value_sum_labeled)
        multipliers[names[label]] = multiplier


    # Start applyting multipliers to archetype zones
    for zone in idf.idfobjects["ZONE"][:]:
        if zone.Name not in names:
            idf.idfobjects["ZONE"].remove(zone)
        else:
            zone.Multiplier = multipliers[zone.Name]

    # A list of objects to be removed to avoid EnergyPlus runtime error
    # first list contains Zone and ZoneList linking
    # second list contains only Zone linking

    remove_obj = ["PEOPLE", "LIGHTS", "ELECTRICEQUIPMENT", "ZONEINFILTRATION:DESIGNFLOWRATE", "SIZING:ZONE"]
    remove_obj2 = ["HVACTEMPLATE:ZONE:VAV"]

    for obj in remove_obj:
        for idf_obj in idf.idfobjects[obj][:]:
            if idf_obj.Zone_or_ZoneList_Name not in names:
                idf.idfobjects[obj].remove(idf_obj)

    for obj in remove_obj2:
        for idf_obj in idf.idfobjects[obj][:]:
            if idf_obj.Zone_Name not in names:
                idf.idfobjects[obj].remove(idf_obj)

    ## Remove unecassary surfaces, and change internal surfaces of the archetype zones to adiabatic
    surfaces = []
    adia_surfaces = []
    for surface in idf.idfobjects["BUILDINGSURFACE:DETAILED"][:]:
        if surface.Zone_Name not in names:
            idf.idfobjects["BUILDINGSURFACE:DETAILED"].remove(surface)
        else:
            surfaces.append(surface.Name)
            if surface.Outside_Boundary_Condition == "Surface":
                surface.Outside_Boundary_Condition = "Adiabatic"
                surface.Outside_Boundary_Condition_Object = ""
                adia_surfaces.append(surface.Name)

    # Remove unnecessary fenestration surfaces, have to use a loop since there seems to have some bug
    # with the remove function in eppy
    fen_surfaces = idf.idfobjects["FENESTRATIONSURFACE:DETAILED"][:]
    last_len = 0
    while last_len != len(fen_surfaces):
        last_len = len(fen_surfaces)
        for fen_surface in fen_surfaces:
            if fen_surface.Building_Surface_Name in surfaces:
                if fen_surface.Building_Surface_Name in adia_surfaces:
                    idf.removeidfobject(fen_surface)
            else:
                idf.removeidfobject(fen_surface)

    idf.saveas(output)

    print("The reduced model has {} zones, {} walls and {} sub-surfaces".
          format(len(idf.idfobjects["ZONE"][:]), len(idf.idfobjects["BUILDINGSURFACE:DETAILED"][:]),
                 len(idf.idfobjects["FENESTRATIONSURFACE:DETAILED"][:])))

    return
