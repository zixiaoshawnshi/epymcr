import pickle
import eppy
from eppy.modeleditor import IDF
import lib.esoreader as esoreader
from lib import IdfModel, IdfCluster, IdfReduce


class ModelClusterReduce(object):
    def __init__(self, idf_path, idd_path="data/V8-5-0-Energy+.idd", save=False):
        #Object initialization
        IDF.setiddname(idd_path)
        self.save = save
        self.centers = []
        self.labels = []
        self.model_parameters = []

        #Read IDF file and generate zone dictionary
        self.idf = IDF(idf_path)
        self.zones = Idf_Zone_List(self.idf)

    def model_pca(self, eso, timestep="Hourly", environment_key="ENVIRONMENT", common_variables="", zone_variables=""):
        eso = esoreader.read_from_path(eso)
        if common_variables == "":
            common_variables = ["Site Solar Azimuth Angle",
                      "Site Solar Altitude Angle",
                      "Site Diffuse Solar Radiation Rate per Area",
                      "Site Direct Solar Radiation Rate per Area",
                      "Site Outdoor Air Drybulb Temperature"
                      ]
        if zone_variables == "":
            zone_variables = ["Zone Mean Air Temperature",
                    "Zone Air System Sensible Heating Rate"]
        self.model_parameters = IdfModel.eso_pca(eso, common_variables, zone_variables, self.zones, timestep,
                                                     environment_key)

    # Use timeseries for modeling purpose, note this timeseris will be normalized by floor area
    def model_timeseries(self, eso, var, timestep="Hourly"):
        eso = esoreader.read_from_path(eso)
        self.model_parameters = IdfModel.eso_timeseries(eso, var, timestep, self.zones)

    def cluster(self, damping=0.5):
        if self.model_parameters is []:
            raise Exception("Need to perform model step first")
        self.centers, self.labels = IdfCluster.cluster(self.model_parameters, damping=damping)

    def reduce(self, output, normalization_method="Area"):
        if self.centers is []:
            raise Exception("Need to perform cluster step first")
        IdfReduce.reduce(self.idf, self.centers, self.labels, output, normalization_method)


# This is a helper function that generates a zone dictionary from the idf file
def Idf_Zone_List(idf, save=False, path="temp/", fname="clustering.zones"):
    if type(idf) is not eppy.modeleditor.IDF:
        raise TypeError("Incorrect input type, please use eppy.idf")
    zones = {}
    for zone in idf.idfobjects["ZONE"]:
        zones[zone.Name] = [zone.Floor_Area, zone.Type]
    if save:
        output = path + fname
        with open(output, 'wb') as f:
            pickle.dump(zones, f)
    return zones


if __name__ == '__main__':
    idf_cluster_test = ModelClusterReduce('sample_data/CB_Original.idf')
    #idf_cluster_test.model_pca("sample_data/CB_Original.eso")
    idf_cluster_test.model_timeseries("sample_data/CB_Original.eso", "Zone Air System Sensible Heating Rate")
    idf_cluster_test.cluster(damping=0.7)
    idf_cluster_test.reduce("sample_data/CB_Reduced.idf")
