#pragma once

#include <util/folder/path.h>

inline TString GraphPath(const TString& name) {
    return BinaryPath(JoinFsPaths("taxi/graph/data/graph3", name));
}

inline TString TestDataPath(const TString& name) {
    return JoinFsPaths(ArcadiaSourceRoot(), "taxi/graph/data/matcher_framework", name);
}

const TString PATH_TO_TOPOLOGY = GraphPath("topology.mms.2");
const TString PATH_TO_DATA = GraphPath("data.mms.2");
const TString PATH_TO_EDGES_RTREE = GraphPath("edges_rtree.mms.2");
const TString PATH_TO_SEGMENTS_RTREE = GraphPath("segments_rtree.mms.2");
const TString PATH_TO_PRECALC = GraphPath("graph_precalc.mms.2");

const TString CFG_PATH = JoinFsPaths(ArcadiaSourceRoot(), "taxi/graph/data/conf/mapmatcher/offline.json");
