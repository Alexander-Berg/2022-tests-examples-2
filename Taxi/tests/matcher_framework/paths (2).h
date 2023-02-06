#pragma once

#include <util/folder/path.h>

inline TString GraphPath(const TString& name) {
    return BinaryPath(JoinFsPaths("taxi/graph/data/graph3", name));
}

inline TString TestDataPath(const TString& name) {
    return JoinFsPaths(ArcadiaSourceRoot(), "taxi/graph/data/matcher_framework", name);
}

const TString PATH_TO_ROAD_GRAPH = GraphPath("road_graph.fb");
const TString PATH_TO_RTREE = GraphPath("rtree.fb");

const TString CFG_PATH = JoinFsPaths(ArcadiaSourceRoot(), "taxi/graph/data/conf/mapmatcher/offline.json");
