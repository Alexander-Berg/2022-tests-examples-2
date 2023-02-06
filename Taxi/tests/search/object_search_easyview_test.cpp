#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <taxi/graph/libs/graph/graph_data_builder.h>
#include <taxi/graph/libs/search/dijkstra_edge_searcher.h>
#include <taxi/graph/libs/search/object_search_easyview.h>

#include <iostream>

#include <taxi/graph/libs/graph-test/graph_test_data.h>

using NTaxi::NGraph2::TClosures;
using NTaxi::NGraph2::TEdge;
using NTaxi::NGraph2::TEdgeData;
using NTaxi::NGraph2::TEdgeId;
using NTaxi::NGraph2::TGraph;
using NTaxi::NGraph2::TId;
using NTaxi::NGraph2::TJams;
using NTaxi::NGraph2::TObjectIndex;
using NTaxi::NGraph2::TPersistentIndex;
using NTaxi::NGraph2::TPositionOnEdge;
using NTaxi::NGraph2::TVertexId;
using NTaxi::NGraphSearch2::TEdgeSearchSettings;
using NTaxi::NGraphSearch2::TWeight;

using namespace NTaxi::NGraph2Literals;

namespace {
    const TEdgeSearchSettings TEST_SETTINGS{
        [] {
            TEdgeSearchSettings result;
            result.MaxVisitedEdges = 10'000u;
            return result;
        }()};
}

class TGraphObjectsSearchEasyviewFixture: public ::NUnitTest::TBaseTestCase, public NTaxi::NGraph2::TGraphTestData {
};

Y_UNIT_TEST_SUITE_F(graph_objects_search_easyview, TGraphObjectsSearchEasyviewFixture) {
    Y_UNIT_TEST(TestSimpleVisualization) {
        const TGraph& graph{GetTestGraph()};

        TString data;
        TStringOutput output(data);
        auto outputStream = std::make_unique<NTaxi::NEasyview::TYsonOutputStream>(&output);

        const auto& uuid = 1ull;
        TObjectIndex<ui64> objIndex(graph);
        objIndex.Insert(uuid, TPositionOnEdge{3_eid, 0.5});
        objIndex.Insert(uuid + 1, TPositionOnEdge{4_eid, 0.5});

        NTaxi::NGraphSearch2::TDijkstraObjectSearcherEasyview searcher(NTaxi::NGraphSearch2::TNullFoundObjectsCallback<ui64>::NullCallback,
                                                                       graph, objIndex, nullptr, nullptr);

        searcher.SetSearchSettings(TEST_SETTINGS);

        TPositionOnEdge startPos{0_eid, 0.0};
        TArrayRef<NTaxi::NGraph2::TPositionOnEdge> startPositions{&startPos, 1};
        searcher.Search(startPositions, outputStream.get());

        output.Flush();

        UNIT_ASSERT(data.Size() != 0);
    }
}
