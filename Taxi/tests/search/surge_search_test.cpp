#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <taxi/graph/libs/graph/graph_data_builder.h>
#include <taxi/graph/libs/search/dijkstra_edge_searcher.h>
#include <taxi/graph/libs/search/object_search_actions.h>

#include <iostream>

#include <taxi/graph/libs/graph-test/graph_test_data.h>

#include <util/stream/file.h>

// maybe just using namespace NTaxi::NGraph2 ???
using NTaxi::NGraph2::TClosures;
using NTaxi::NGraph2::TEdge;
using NTaxi::NGraph2::TEdgeData;
using NTaxi::NGraph2::TEdgeId;
using NTaxi::NGraph2::TGraph;
using NTaxi::NGraph2::TId;
using NTaxi::NGraph2::TZoneId;
using NTaxi::NGraph2::TPoint;
using NTaxi::NGraph2::TPositionOnEdge;
using NTaxi::NGraph2::TVertexId;
using NTaxi::NGraph2::TSurgeZoneIndex;
using NTaxi::NGraphSearch2::TEdgeSearchSettings;
using NTaxi::NGraphSearch2::TWeight;

using namespace NTaxi::NGraph2Literals;

namespace {
    class TestSurgeSearchCallback: public NTaxi::NGraphSearch2::IFoundSurgeZoneCallback {
    public:
        explicit TestSurgeSearchCallback() = default;

    public:
        NTaxi::NGraphSearch2::SearchState OnFoundSurgeZone(NTaxi::NGraphSearch2::IEdgeSearchActions& actions, TWeight currentDistance,
                const TPositionOnEdge& zoneEntryPoint, TZoneId zoneId) final {
            std::ignore = actions;

            ZoneEntryPoints[zoneId] = zoneEntryPoint;
            FoundDistances[zoneId] = currentDistance;

            return SearchState::ContinueState;
        }

        const auto& GetZoneEntryPoints() const {
            return ZoneEntryPoints;
        }

        const auto& GetFoundDistances() const {
            return FoundDistances;
        }

        void Reset() {
            ZoneEntryPoints.clear();
        }

    private:
        std::unordered_map<TZoneId, TPositionOnEdge> ZoneEntryPoints;
        std::unordered_map<TZoneId, TWeight> FoundDistances;
    };

    const TEdgeSearchSettings TEST_SETTINGS{
        [] {
            TEdgeSearchSettings result;
            result.MaxVisitedEdges = 10'000u;
            return result;
        }()};

}

class TGraphSurgeSearchFixture: public ::NUnitTest::TBaseTestCase, public NTaxi::NGraph2::TGraphTestData {
};

// TODO(mesyarik): why test suite doesn't see tests below if "graph_objects_search" replace by "graph_surge_search"???!!!
Y_UNIT_TEST_SUITE_F(graph_surge_search, TGraphSurgeSearchFixture) {

   Y_UNIT_TEST(TestSurgeSearchOnRhombusGraph) {
        TGraph graph{CreateRhombusRoadGraph()};

        // Visualization: https://wiki.yandex-team.ru/users/mesyarik/test-na-poisk-blizhajjshix-shestiugolnikov/
        TSurgeZoneIndex index(graph);

        // red hexagon - zone id 0
        index.AddHexagonalZone({0.0, 1.0}, 0.5);

        // orange hexagon - zone id 1
        index.AddHexagonalZone({0.75, 0.0}, 0.75);

        // green hexagon - zone id 2
        index.AddHexagonalZone({-0.5, -0.5}, 1.0);

        // purple hexagon - zone id 3
        index.AddHexagonalZone({0.0, -1.5}, 0.6);

        auto edgesToZones = index.GetEdgesToZonesMapping();

        using TZoneEntryInfo = NTaxi::NGraph2::TSurgeZoneIndex::TZoneEntryInfo;
        std::unordered_multimap<TEdgeId, TZoneEntryInfo> expectedEdgesToZones;
        // edge id -> (zone id, zone entry position, zone exit position)
        expectedEdgesToZones.insert({0_eid, {0, 0.566987, 1}});
        expectedEdgesToZones.insert({1_eid, {0, 0, 0.316976}});
        expectedEdgesToZones.insert({1_eid, {2, 0.633964, 1}});
        expectedEdgesToZones.insert({2_eid, {0, 0, 0.316976}});
        expectedEdgesToZones.insert({2_eid, {1, 0.366014, 1}});
        expectedEdgesToZones.insert({3_eid, {2, 0, 1}});
        expectedEdgesToZones.insert({3_eid, {3, 0.980385, 1}});
        expectedEdgesToZones.insert({4_eid, {1, 0, 0.633982}});
        expectedEdgesToZones.insert({4_eid, {2, 0.500007, 1}});
        expectedEdgesToZones.insert({4_eid, {3, 0.980385, 1}});
        expectedEdgesToZones.insert({5_eid, {2, 0, 0.366025}});
        expectedEdgesToZones.insert({5_eid, {3, 0, 1}});
        
        for (size_t i = 0; i < 6; ++i) {
            TEdgeId id = TEdgeId(i);
            auto [from_it, to_it] = expectedEdgesToZones.equal_range(id);
            auto [from_that, to_that] = edgesToZones.equal_range(id);
            UNIT_ASSERT_EQUAL(std::distance(from_it, to_it), std::distance(from_that, to_that));

            std::vector<std::pair<TEdgeId, TZoneEntryInfo>> expected;
            std::vector<std::pair<TEdgeId, TZoneEntryInfo>> actual;

            for (auto it = from_it, that = from_that; it != to_it && that != to_that; ++it, ++that) {
                expected.push_back(*it);
                actual.push_back(*that);
            }

            auto cmp = [](const auto& item, const auto& another) -> bool {
                return std::make_pair(item.first, item.second.ZoneId) < std::make_pair(another.first, another.second.ZoneId);
            };
            
            std::sort(expected.begin(), expected.end(), cmp);
            std::sort(actual.begin(), actual.end(), cmp);

            std::cout << "expected:\n";
            for (const auto& item: expected) {
                std::cout << item.first << ' ' << item.second.ZoneId << ' ' << item.second.StartPosition << ' ' << item.second.EndPosition << '\n';
            }
            std::cout << "actual:\n";
            for (const auto& item: actual) {
                std::cout << item.first << ' ' << item.second.ZoneId << ' ' << item.second.StartPosition << ' ' << item.second.EndPosition << '\n';
            }
            std::cout << std::endl;

            for (auto it = expected.begin(), that = actual.begin(); it != expected.end() && that != actual.end(); ++it, ++that) {
                UNIT_ASSERT_EQUAL(it->first, that->first);
                UNIT_ASSERT_EQUAL(it->second.ZoneId, that->second.ZoneId);
                UNIT_ASSERT_DOUBLES_EQUAL(it->second.StartPosition, that->second.StartPosition, 1e-3);
                UNIT_ASSERT_DOUBLES_EQUAL(it->second.EndPosition, that->second.EndPosition, 1e-3);
            }
        }
        
        TestSurgeSearchCallback foundCallback;
        NTaxi::NGraphSearch2::TSurgeSearchActions searchActions{foundCallback, index, nullptr, nullptr};
        NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, searchActions, TEST_SETTINGS);
        searcher.Search(TPositionOnEdge{0_eid, 0.25});

        std::unordered_map<TZoneId, TPositionOnEdge> expectedEntryPoints;
        expectedEntryPoints[TZoneId(0)] = {0_eid, 0.566987};
        expectedEntryPoints[TZoneId(1)] = {2_eid, 0.366014};
        expectedEntryPoints[TZoneId(2)] = {1_eid, 0.633964};
        expectedEntryPoints[TZoneId(3)] = {4_eid, 0.980385};

        const auto& actualEntryPoints = foundCallback.GetZoneEntryPoints();
        
        std::cout << "Entry points:" << std::endl;
        for (int i = 0; i < 4; ++i) {
            TZoneId id = TZoneId(i);
            TPositionOnEdge expected = expectedEntryPoints.at(id);
            TPositionOnEdge actual = actualEntryPoints.at(id);
            UNIT_ASSERT_EQUAL(expected.EdgeId, actual.EdgeId);
            UNIT_ASSERT_DOUBLES_EQUAL(expected.Position, actual.Position, 1e-3);
            std::cout << id << ": " << actual.EdgeId << " " << actual.Position << std::endl;
        }

        const auto& foundDistances = foundCallback.GetFoundDistances();

        for (int i = 0; i < 4; ++i) {
            TZoneId id = TZoneId(i);
            TWeight distance = foundDistances.at(id);
            std::cout << id << ": " << distance << std::endl;
        }
        
        UNIT_ASSERT(true);
    }
    
    Y_UNIT_TEST(TestDistancesToZones) {
        TGraph graph{CreateTriangleRoadGraph()};

        TSurgeZoneIndex index(graph);

        // visualization: https://wiki.yandex-team.ru/users/mesyarik/test-na-rasstojanija-pri-poiske-shestiugolnikov/
        // red hexagon - zone id 0
        index.AddHexagonalZone({1.5, 0.0}, 0.6);

        // green hexagon - zone id 1
        index.AddHexagonalZone({0.6, 0.0}, 0.2);

        // dark blue - zone id 2
        index.AddHexagonalZone({1.0, 0.0}, 0.4);

        // light blue - zone id 3
        index.AddHexagonalZone({1.6, 0}, 0.2);

        // brown - zone id 4
        index.AddHexagonalZone({0.0, 0.0}, 0.2);

        // orange - zone id 5
        index.AddHexagonalZone({0.5, 0.0}, 0.6);

        auto edgesToZones = index.GetEdgesToZonesMapping();
        
        TestSurgeSearchCallback foundCallback;
        NTaxi::NGraphSearch2::TSurgeSearchActions searchActions{foundCallback, index, nullptr, nullptr};
        NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, searchActions, TEST_SETTINGS);
        
        searcher.Search(TPositionOnEdge{0_eid, 0.5});

        std::unordered_map<TZoneId, TPositionOnEdge> expectedEntryPoints;
        expectedEntryPoints[TZoneId(0)] = {0_eid, 0.5};
        expectedEntryPoints[TZoneId(1)] = {0_eid, 0.2};
        expectedEntryPoints[TZoneId(2)] = {0_eid, 0.5};
        expectedEntryPoints[TZoneId(3)] = {0_eid, 0.7};
        expectedEntryPoints[TZoneId(4)] = {2_eid, 0.873201};
        expectedEntryPoints[TZoneId(5)] = {0_eid, 0.5};

        const auto& actualEntryPoints = foundCallback.GetZoneEntryPoints();
        
        std::cout << "Entry points:" << std::endl;
        for (int i = 0; i < 6; ++i) {
            TZoneId id = TZoneId(i);
            TPositionOnEdge expected = expectedEntryPoints.at(id);
            TPositionOnEdge actual = actualEntryPoints.at(id);
            UNIT_ASSERT_EQUAL(expected.EdgeId, actual.EdgeId);
            UNIT_ASSERT_DOUBLES_EQUAL(expected.Position, actual.Position, 1e-3);
            std::cout << id << ": " << actual.EdgeId << " " << actual.Position << std::endl;
        }

        std::unordered_map<TZoneId, TWeight> expectedDistances;
        expectedDistances[TZoneId(0)] = 0;
        expectedDistances[TZoneId(1)] = 3.4;
        expectedDistances[TZoneId(2)] = 0;
        expectedDistances[TZoneId(3)] = 0.4;
        expectedDistances[TZoneId(4)] = 2.8732;
        expectedDistances[TZoneId(5)] = 0;

        const auto& actualDistances = foundCallback.GetFoundDistances();

        for (int i = 0; i < 6; ++i) {
            TZoneId id = TZoneId(i);
            TWeight expected = expectedDistances.at(id);
            TWeight actual = actualDistances.at(id);
            UNIT_ASSERT_DOUBLES_EQUAL(expected, actual, 1e-3);
            std::cout << id << ": " << actual << std::endl;
        }
        
        UNIT_ASSERT(true);
    }
}
