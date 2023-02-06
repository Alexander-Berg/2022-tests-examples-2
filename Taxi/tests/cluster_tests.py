# coding: utf-8

import json
import os

import pandas as pd

from business_models.models.cluster import FilterCluster
from .common import make_path

DATA_DIRECTORY = os.path.abspath(os.path.dirname(__file__)) + "/data"


def filter_cluster_tests():
    clusters = ['first', 'second', 'third']
    rules = ['exclude', 'include', 'include_attribute']
    cluster_args = json.load(open(make_path("filter_cluster_kwargs.json")))

    data = pd.DataFrame()
    data['number'] = [1, 2, 3, 4, 5, 6, 7, 8]
    data['letter'] = ['a', 'b', 'a', 'b', 'a', 'b', 'a', 'a']
    data['month'] = pd.date_range('2018-01-01', periods=8, freq="W-MON")

    test_clust = FilterCluster(clusters=clusters, rules=rules,
                               cluster_kwargs=cluster_args)
    splited_data = test_clust.split(data, only_single_cluster=True, as_dict=True)

    pd.testing.assert_frame_equal(splited_data['first'], data.iloc[[4, 5, 6, 7]], obj='first cluster')
    pd.testing.assert_frame_equal(splited_data['second'], data.iloc[[0, 2]], obj='second cluster')
    pd.testing.assert_frame_equal(splited_data['third'], data.iloc[[1, 3]], obj='third cluster')\

