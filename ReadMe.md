
This is a simple Python package used for the paper "Building Energy Model Reduction using Model-Cluster-Reduce Pipeline" published on Journal of Building Performance Simulation. It is used to perform model order reduction on EnergyPlus models. This readme includes a simple introduction to how to use this code. Other packages required for this tool are: eppy, sklearn, pandas and numpy.

This package does not include codes to make the reduced model 100% ready for simulation. Other modifications such as HVAC system node elimination may required. It is recommend to use HVAC template for the reduced model in this case. Future updates will improve the functionality of this tool.

First we import and initiate the ModelClusterReduce class. Note a default .idd file for EnergyPlus 8.5 is provided. However, for newer EnergyPlus versions, .idd file may need to be manually defined.


```python
from IdfPipeline import ModelClusterReduce
test_pipeline = ModelClusterReduce("sample_data/CB_Original.idf", idd_path="data/V8-5-0-Energy+.idd")
```

After the pipeline is initiated, we can perform the model procedure by providing the .eso file -- standard EnergyPlus output file. Currently two model approahes are provided, PCA (.model_pca) and time series (.model_timeseries).


```python
%%capture
# First with PCA method
# PCA requires a list of variables to be read from the .eso file
# A default list of variables are provided, however, it can be modified for different applications
# First define common variables used for all zones, such as outdoor air temperature, etc.
common_variables = ["Site Solar Azimuth Angle",
          "Site Solar Altitude Angle",
          "Site Diffuse Solar Radiation Rate per Area",
          "Site Direct Solar Radiation Rate per Area",
          "Site Outdoor Air Drybulb Temperature"
          ]

# Next define zone variables, such as air temperature for each zone
zone_variables = ["Zone Mean Air Temperature",
        "Zone Air System Sensible Heating Rate"]

# After the definition of variables is complete, the PCA modeling process can start
test_pipeline.model_pca("sample_data/CB_Original.eso", 
                        timestep="Hourly", common_variables=common_variables, zone_variables=zone_variables)
```


```python
%%capture
# Next with time series method
# This method is more straight forward, only one unique zone variable is required
# This variable will then be normalized by floor area and min-max normalization
test_pipeline.model_timeseries("sample_data/CB_Original.eso", "Zone Air System Sensible Heating Rate")
```

After the model step is done, a clustering process can be performed to identify archetype zones. Note oscillation may occur when using Affinity Propagation, so damping factor may need to be changed.


```python
test_pipeline.cluster()
```

    Estimated number of clusters: 94
    

Looks like there this is a case of oscillation, so we can try a damping factor of 0.7 instead.


```python
test_pipeline.cluster(damping=0.7)
```

    Estimated number of clusters: 13
    

Now the damping issue is solved, the reduced model can then be produced. There are two ways to calculate scale factors for archetype zones, one is to use floor area ("Area"), another is to use zone volume ("Volume").


```python
test_pipeline.reduce(output="sample_data/CB_reduced.idf", normalization_method="Area")
```

    The reduced model has 13 zones, 201 walls and 22 sub-surfaces
    
