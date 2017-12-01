"""
This is the modeling procedure for Model-Cluster-Reduce BPS model reduction process,
currently supports PCA and time-series modeling
developed by Zixiao Shi at the Department of Civil and Environmental Engineering at
Carleton University, Ottawa Canada
"""
import pickle
import pandas as pd
from sklearn.decomposition import PCA
from sklearn import preprocessing
import numpy as np
import csv


def eso_pca(eso, common_variables, zone_variables, zones, timestep="Hourly", environment_key ="ENVIRONMENT",
            save = False, path="temp/"):
    common_df = pd.DataFrame()
    for common_variable in common_variables:
        df = eso.to_frame(common_variable, key=environment_key, frequency=timestep)
        common_df = pd.merge(common_df, df, right_index=True, left_index=True, how="outer")

    common_df.columns = common_variables
    data_len = common_df.shape[0]
    pca = PCA(n_components=len(common_variables) + len(zone_variables) + 1, whiten=False)
    pca_results = []
    pca_transformed = []
    for zone in zones:
        zone_df = pd.DataFrame()
        for zone_variable in zone_variables:
            df = eso.to_frame(zone_variable, key=zone, frequency=timestep)
            if df.empty:
                df = pd.DataFrame(np.zeros(data_len))
            zone_df = pd.merge(zone_df,
                                df,
                                right_index=True, left_index=True, how="outer")
        zone_df.columns = zone_variables
        zone_df = pd.merge(zone_df, common_df, right_index=True, left_index=True, how='outer')
        zone_df.fillna(method="pad")
        zone_df["Zone Mean Air Temperature Difference"] = zone_df["Zone Mean Air Temperature"].diff().fillna(0)
        all_columns = common_variables + zone_variables + ["Zone Mean Air Temperature Difference"]
        zone_df_scaled = zone_df[all_columns].apply(lambda x: (x-x.mean())/x.std())

        try:
            pca.fit(zone_df_scaled)
            pca_results.append(pca.components_[0])
            pca_transformed.append(pca.transform(zone_df_scaled))
        except:
            print("fail to use PCA transformation for " + zone)

    if save:
        output_name = path+"temp.pca"
        with open(output_name, 'wb') as f:
            pickle.dump(pca_results, f)

        with open(path+'temp_pca.csv', 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(pca_results)

        output_name = path+"temp.pcatrans"
        with open(output_name, 'wb') as f:
            pickle.dump(pca_transformed, f)

    return pca_results


def eso_timeseries(eso, var, timestep, zones, save = False, path="temp/"):

    # create a list of zone names
    zone_names = zones.keys()
    df_trial = eso.to_frame("Site Outdoor Air Drybulb Temperature", key="ENVIRONMENT", frequency=timestep)
    # get the length of the data
    data_len = df_trial.shape[0]

    # get time series values
    size = 0
    ts_df = pd.DataFrame()
    for zone in zone_names:
        area = zones[zone][0]
        size += 1
        df = eso.to_frame(var, key=zone, frequency=timestep).divide(area)
        if df.empty:
            df = pd.DataFrame(np.zeros(data_len))
        ts_df = pd.merge(ts_df, df, right_index=True, left_index=True, how="outer")
    # scale the data with min-max scaling
    x = ts_df.transpose().values  # returns a numpy array
    min_max_scaler = preprocessing.MinMaxScaler()
    x_scaled = min_max_scaler.fit_transform(x)
    return x_scaled
