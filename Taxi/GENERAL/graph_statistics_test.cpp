#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <yandex/taxi/graph2/graph.h>
#include <taxi/graph/tools/lib/graph_statistics.h>

#include <util/folder/path.h>

using NTaxiExternal::NGraph2::TGraph;
using NTaxiExternal::NGraph2::TRoadGraphFileLoader;
using NTaxi::NGraphStatistics::TGraphStatistics;

namespace {
    TString GraphPath(const TStringBuf& str) {
        return BinaryPath(JoinFsPaths("taxi/graph/data/graph3", str));
    }
}

Y_UNIT_TEST_SUITE(statistics_test) {
    Y_UNIT_TEST(graph_statistics_test) {
        TGraph graph(
            TRoadGraphFileLoader::Create(
                GraphPath("road_graph.fb").c_str(),
                GraphPath("rtree.fb").c_str()
            )
        );

        TGraphStatistics graph_statistics{graph};

        UNIT_ASSERT_EQUAL(graph_statistics.EdgesNumber, 303552);
        UNIT_ASSERT_EQUAL(graph_statistics.VerticesNumber, 129247);
        UNIT_ASSERT_EQUAL(graph_statistics.AccessPassesNumber, 0);
        UNIT_ASSERT_EQUAL(graph_statistics.TollEdgesNumber, 0);
        UNIT_ASSERT_EQUAL(graph_statistics.SpeedLimitsNumber, 15);
        UNIT_ASSERT_EQUAL(graph_statistics.EdgesWithMasstransitLaneNumber, 0);
        UNIT_ASSERT_EQUAL(graph_statistics.PavedEdgesNumber, 303552);
    }
}
