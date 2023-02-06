#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <maps/libs/geolib/include/distance.h>
#include <taxi/graph/libs/graph/graph.h>

#include <taxi/graph/libs/graph/road_graph_helpers.h>

#include <taxi/graph/libs/graph/edge_storage.h>
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
using NTaxi::NGraph2::NEdgeStorage::TStorage;
using NTaxi::NUtils::ToMapsPoint;

using namespace NTaxi::NGraph2Literals;

Y_UNIT_TEST_SUITE(graph_edge_storage) {
    Y_UNIT_TEST(base) {
        ::NTaxi::NGraph2::TGraphTestData test_data;
        auto graph = test_data.CreateRhombusRoadGraphWithPasses();
        graph.BuildEdgeStorage(16);
        const auto& storage = graph.GetEdgeStorage();
        UNIT_ASSERT(storage.IsInitialized());

        const auto edgeCount = graph.EdgesCount();
        for (size_t i = 0; i < edgeCount; ++i) {
            const auto edgeId = static_cast<TId>(i);
            const auto storageCategory = storage.GetCategory(edgeId);
            const auto graphCategory = graph.GetCategory(edgeId);
            UNIT_ASSERT_EQUAL(storageCategory, graphCategory);

            const auto edgeData = graph.GetEdgeData(edgeId);
            const auto storageAccess = storage.GetAccess(edgeId);
            UNIT_ASSERT_EQUAL(edgeData.Access, storageAccess);

            const auto storageLength = storage.GetLength(edgeId);
            UNIT_ASSERT_EQUAL(edgeData.Length, storageLength);

            const auto storageSpeed = storage.GetSpeed(edgeId);
            UNIT_ASSERT_EQUAL(edgeData.Speed, storageSpeed);
        }
    }

    Y_UNIT_TEST(base_on_demand) {
        ::NTaxi::NGraph2::TGraphTestData test_data;
        auto graph = test_data.CreateRhombusRoadGraphWithPasses();
        NTaxi::NGraph2::NEdgeStorage::TStorageOnDemand storage(graph, graph.GetYardIndex());
        UNIT_ASSERT(storage.IsInitialized());

        const auto edgeCount = graph.EdgesCount();
        for (size_t i = 0; i < edgeCount; ++i) {
            const auto edgeId = static_cast<TId>(i);
            const auto storageCategory = storage.GetCategory(edgeId);
            const auto graphCategory = graph.GetCategory(edgeId);
            UNIT_ASSERT_EQUAL(storageCategory, graphCategory);

            const auto edgeData = graph.GetEdgeData(edgeId);
            const auto storageAccess = storage.GetAccess(edgeId);
            UNIT_ASSERT_EQUAL(edgeData.Access, storageAccess);

            const auto storageLength = storage.GetLength(edgeId);
            UNIT_ASSERT_EQUAL(edgeData.Length, storageLength);

            const auto storageSpeed = storage.GetSpeed(edgeId);
            UNIT_ASSERT_EQUAL(edgeData.Speed, storageSpeed);
        }
    }

    Y_UNIT_TEST(clearing) {
        ::NTaxi::NGraph2::TGraphTestData test_data;
        auto graph = test_data.CreateRhombusRoadGraphWithPasses();
        graph.BuildEdgeStorage(16);
        const auto& storage = graph.GetEdgeStorage();
        UNIT_ASSERT(storage.IsInitialized());
        graph.ClearEdgeStorage();
        UNIT_ASSERT(!storage.IsInitialized());
    }

    Y_UNIT_TEST(clearing_on_demand) {
        ::NTaxi::NGraph2::TGraphTestData test_data;
        auto graph = test_data.CreateRhombusRoadGraphWithPasses();
        NTaxi::NGraph2::NEdgeStorage::TStorageOnDemand storage(graph, graph.GetYardIndex());
        UNIT_ASSERT(storage.IsInitialized());
        storage.ClearStorage();
        UNIT_ASSERT(!storage.IsInitialized());
    }

    Y_UNIT_TEST(filter_forbidden) {
        using TTurnInfoDesc = NTaxi::NGraph2::TGraphTestData::TTurnInfoDesc;

        ::NTaxi::NGraph2::TGraphTestData test_data;

        TVector<TTurnInfoDesc> turn_infos = {
            {0, 1, true, false, false}, // accessPass
            {2, 4, false, true, false}, // forbidden
            {4, 5, false, false, true}, // countryBorder
        };
        std::unordered_map<ui32, TId> mapping;
        auto graph = test_data.CreateRhombusRoadGraphWithPasses(turn_infos, &mapping);
        graph.BuildEdgeStorage(16);
        const auto& storage = graph.GetEdgeStorage();
        UNIT_ASSERT(storage.IsInitialized());

        UNIT_ASSERT(graph.IsAccessPass(mapping[0], mapping[1]));

        // country border filtered
        const auto& expected_in_5 = TVector<TId>{static_cast<TId>(3)};
        const auto& expected_in_5_ref = TArrayRef<const TId>(expected_in_5.data(), expected_in_5.size());
        const auto storage_edges = storage.GetInEdges(mapping[5]);
        UNIT_ASSERT_EQUAL(expected_in_5_ref, storage_edges);

        // forbidden filtered
        UNIT_ASSERT_EQUAL(0ul, storage.GetOutEdges(mapping[2]).size());
    }

    Y_UNIT_TEST(filter_forbidden_on_demand) {
        using TTurnInfoDesc = NTaxi::NGraph2::TGraphTestData::TTurnInfoDesc;

        ::NTaxi::NGraph2::TGraphTestData test_data;

        TVector<TTurnInfoDesc> turn_infos = {
            {0, 1, true, false, false}, // accessPass
            {2, 4, false, true, false}, // forbidden
            {4, 5, false, false, true}, // countryBorder
        };
        std::unordered_map<ui32, TId> mapping;
        auto graph = test_data.CreateRhombusRoadGraphWithPasses(turn_infos, &mapping);
        NTaxi::NGraph2::NEdgeStorage::TStorageOnDemand storage(graph, graph.GetYardIndex());
        UNIT_ASSERT(storage.IsInitialized());

        UNIT_ASSERT(graph.IsAccessPass(mapping[0], mapping[1]));

        // country border filtered
        const auto& expected_in_5 = TVector<TId>{static_cast<TId>(3)};
        const auto& expected_in_5_ref = TArrayRef<const TId>(expected_in_5.data(), expected_in_5.size());
        const auto storage_edges = storage.GetInEdges(mapping[5]);
        UNIT_ASSERT_EQUAL(expected_in_5_ref, storage_edges);

        // forbidden filtered
        UNIT_ASSERT_EQUAL(0ul, storage.GetOutEdges(mapping[2]).size());
    }
}
