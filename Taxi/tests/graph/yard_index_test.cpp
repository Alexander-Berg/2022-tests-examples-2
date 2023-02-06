#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <maps/libs/geolib/include/distance.h>
#include <taxi/graph/libs/graph/graph.h>

#include <taxi/graph/libs/graph/road_graph_helpers.h>

#include <taxi/graph/libs/graph/yard_index.h>
#include <taxi/graph/libs/graph-test/graph_test_data.h>
#include <iostream>

using TaxiGraph = NTaxi::NGraph2::TGraph;
using NTaxi::NGraph2::TEdgeAccess;
using NTaxi::NGraph2::TEdgeCategory;
using NTaxi::NGraph2::TId;
using NTaxi::NGraph2::TPoint;
using NTaxi::NGraph2::TPolyline;
using NTaxi::NGraph2::TPositionOnEdge;
using NTaxi::NGraph2::TPositionOnGraph;
using NTaxi::NGraph2::TYardId;
using NTaxi::NGraph2::TYardIndex;
using NTaxi::NUtils::ToMapsPoint;

using namespace NTaxi::NGraph2Literals;

namespace {
    TVector<size_t> CountEdgesInEachYard(const NTaxi::NGraph2::TYardIndex& index) {
        const size_t edge_count = index.GetEdgeCount();
        TVector<size_t> ret(index.GetYardCount(), 0);
        for (size_t i = 0; i < edge_count; ++i) {
            const auto yard_id = index.GetYard(static_cast<TId>(i));
            if (yard_id != TYardIndex::UNDEFINED_YARD)
                ++ret[yard_id.value()];
        }
        return ret;
    }

    size_t CountPasses(const NTaxi::NGraph2::TGraph& graph) {
        const size_t edge_count = graph.EdgesCount();
        size_t ret = 0;
        for (size_t i = 0; i < edge_count; ++i)
            ret += graph.GetCategory(static_cast<TId>(i)) == TEdgeCategory::EC_PASSES;

        return ret;
    }
}

Y_UNIT_TEST_SUITE(graph_yard_index) {
    Y_UNIT_TEST(base) {
        ::NTaxi::NGraph2::TGraphTestData test_data;
        const auto& graph = test_data.CreateRhombusGraphWithPasses();
        const auto& yard_index = NTaxi::NGraph2::TYardIndex(graph);
        const auto& yards_count = yard_index.GetYardCount();
        const auto& edge_count = yard_index.GetEdgeCount();
        const auto& edges_in_each_yard = CountEdgesInEachYard(yard_index);
        const auto& yard_edges_count = std::accumulate(edges_in_each_yard.begin(), edges_in_each_yard.end(), 0u);
        const auto& passes_count = CountPasses(graph);

        UNIT_ASSERT_EQUAL(edge_count, graph.EdgesCount());
        /// sum of all yard edges == edge count of EC_PASSES category
        UNIT_ASSERT_EQUAL(yard_edges_count, passes_count);

        UNIT_ASSERT_EQUAL(2u, yards_count);

        const TVector<TYardId> expected_yard_ids = {
            static_cast<NTaxi::NGraph2::TYardId>(0),
            NTaxi::NGraph2::TYardIndex::UNDEFINED_YARD,
            static_cast<NTaxi::NGraph2::TYardId>(0),
            static_cast<NTaxi::NGraph2::TYardId>(1),
            NTaxi::NGraph2::TYardIndex::UNDEFINED_YARD,
            static_cast<NTaxi::NGraph2::TYardId>(1)};
        TVector<TYardId> yard_ids;
        for (ui32 i = 0; i < yard_index.GetEdgeCount(); ++i) {
            yard_ids.push_back(yard_index.GetYard(NTaxi::NGraph2::TEdgeId{i}));
        }

        UNIT_ASSERT_EQUAL(expected_yard_ids, yard_ids);
    }
}
