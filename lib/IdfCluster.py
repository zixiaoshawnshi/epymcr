"""
This is the clustering procedure for Model-Cluster-Reduce BPS model reduction process,
developed by Zixiao Shi at the Department of Civil and Environmental Engineering at
Carleton University, Ottawa Canada

"""
import pickle
import numpy as np
from sklearn.preprocessing import scale
from sklearn.cluster import AffinityPropagation


def cluster(model_results, damping, save = False, path="temp/", fname="temp"):

    X = scale(np.array(model_results))
    af = AffinityPropagation(damping=damping).fit(X)
    cluster_centers_indices = af.cluster_centers_indices_
    labels = af.labels_
    n_clusters_ = len(cluster_centers_indices)
    print('Estimated number of clusters: %d' % n_clusters_)

    if save is True:
        labels_fname = path + fname + ".cluster"
        with open(labels_fname, 'wb') as f:
            pickle.dump(labels, f)

        centers_fname = path + fname + ".center"
        with open(centers_fname, 'wb') as f:
            pickle.dump(cluster_centers_indices, f)

    return cluster_centers_indices, labels
