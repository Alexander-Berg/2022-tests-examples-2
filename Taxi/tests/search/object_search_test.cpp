#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <taxi/graph/libs/graph/graph_data_builder.h>
#include <taxi/graph/libs/search/dijkstra_edge_searcher.h>
#include <taxi/graph/libs/search/object_search_actions.h>

#include <iostream>

#include <taxi/graph/libs/graph-test/graph_test_data.h>

#include <util/stream/file.h>

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
using NTaxi::NGraphSearch2::TDriversOnEdgeInfo;

using namespace NTaxi::NGraph2Literals;

namespace {
    class TestObjectSearchCallback: public NTaxi::NGraphSearch2::IFoundObjectsCallback<ui64> {
    public:
        explicit TestObjectSearchCallback() = default;

    public:
        NTaxi::NGraphSearch2::SearchState OnFoundObjects(NTaxi::NGraphSearch2::IEdgeSearchActions& actions, TWeight currentDistance,
                double edgeStart, TWeight edgeWeight, const TDriversOnEdgeInfo& driversInfo,
                typename TObjectIndex<ui64>::TEdgeObjectsRange&& objsOnEdge) final {
            std::ignore = actions;
            if (objsOnEdge.begin() != objsOnEdge.end()) {
                const auto edge_id = (*objsOnEdge.begin()).second.GetEdgeId();
                EdgeLeeways[edge_id] = driversInfo.Leeway;
            }
            for (const auto& key_pos : objsOnEdge) {
                EdgeWeights.push_back(edgeWeight);
                const auto pos = key_pos.second;

                EdgeIds.push_back(pos.GetEdgeId());
                DistancesToFinalEdgesFromStart.push_back(currentDistance);

                // We calc distance same way in git/geograph
                TWeight distance = GetObjectWeight(currentDistance, edgeStart, edgeWeight, pos);
                Cout << "edgeWeight : " << edgeWeight << " currentDistance: " << currentDistance <<
                  " edgeStart: " << edgeStart << " pos: " << pos.Position << " final distance: " << distance << Endl;
                DistancesToObjects[key_pos.first] = distance;
            }

            return SearchState::ContinueState;
        }

        std::vector<TId> GetEdgeIds() const {
            return EdgeIds;
        }

        std::vector<TWeight> GetEdgeWeights() const {
            return EdgeWeights;
        }

        std::vector<TWeight> GetDistancesFromStart() const {
            return DistancesToFinalEdgesFromStart;
        }

        auto GetDistancesToObjects() const {
            return DistancesToObjects;
        }

        auto GetEdgeLeeways() const {
            return EdgeLeeways;
        }

        void Reset() {
            EdgeIds.clear();
            EdgeWeights.clear();
        }

    private:
        std::vector<TId> EdgeIds;
        std::vector<TWeight> EdgeWeights;
        std::vector<TWeight> DistancesToFinalEdgesFromStart;
        std::unordered_map<ui64, TWeight> DistancesToObjects;
        std::unordered_map<TId, int32_t> EdgeLeeways;
    };

    class TestImmediateStopCallback: public NTaxi::NGraphSearch2::IFoundObjectsCallback<ui64> {
    public:
        explicit TestImmediateStopCallback() = default;

    public:
        SearchState OnFoundObjects(NTaxi::NGraphSearch2::IEdgeSearchActions&,
                TWeight, double, TWeight, const TDriversOnEdgeInfo&, typename TObjectIndex<ui64>::TEdgeObjectsRange&&) final {
            return SearchState::BreakState;
        }
    };

    const TEdgeSearchSettings TEST_SETTINGS{
        [] {
            TEdgeSearchSettings result;
            result.MaxVisitedEdges = 10'000u;
            return result;
        }()};

    const TEdgeSearchSettings REVERSE_TEST_SETTINGS{
        [] {
            TEdgeSearchSettings result;
            result.MaxVisitedEdges = 10'000u;
            result.ReverseEdges = true;
            return result;
        }()};
}

class TGraphObjectsSearchFixture: public ::NUnitTest::TBaseTestCase, public NTaxi::NGraph2::TGraphTestData {
};

Y_UNIT_TEST_SUITE_F(graph_objects_search, TGraphObjectsSearchFixture) {
    Y_UNIT_TEST(TestObjectRulesEdgeLimit) {
        const auto& graph = GetTestGraph();
        const auto& uuid = 1ull;
        TObjectIndex<ui64> objIndex(graph);
        UNIT_ASSERT(objIndex.Insert(uuid, NTaxi::NGraph2::TPoint{37.676062, 55.748181}));
        UNIT_ASSERT(objIndex.Insert(uuid + 1, NTaxi::NGraph2::TPoint{37.684551, 55.746956}));
        UNIT_ASSERT(objIndex.Insert(uuid + 3, NTaxi::NGraph2::TPoint{37.586798, 55.653567}));

        const auto& edgeId = objIndex.GetPosition(uuid).GetEdgeId();
        const auto& edgeId2 = objIndex.GetPosition(uuid + 1).GetEdgeId();

        TestObjectSearchCallback foundCallback;
        NTaxi::NGraphSearch2::TObjectSearchActions searchActions{foundCallback, objIndex};

        NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, searchActions, TEST_SETTINGS);
        searcher.Search(edgeId);

        std::vector<TId> res{edgeId, edgeId2};
        UNIT_ASSERT_EQUAL(foundCallback.GetEdgeIds(), res);
    }

    Y_UNIT_TEST(TestObjectRulesStopImmediately) {
        const auto& graph = GetTestGraph();
        const auto& uuid = 1ull;
        TObjectIndex<ui64> objIndex(graph);
        UNIT_ASSERT(objIndex.Insert(uuid, NTaxi::NGraph2::TPoint{37.676062, 55.748181}));

        const auto& edgeId = objIndex.GetPosition(uuid).GetEdgeId();

        TestImmediateStopCallback foundCallback;
        NTaxi::NGraphSearch2::TObjectSearchActions searchActions{foundCallback, objIndex};
        NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, searchActions, TEST_SETTINGS);
        searcher.Search(edgeId);

        UNIT_ASSERT_EQUAL(searcher.GetEdgesVisited(), 1);
    }

    Y_UNIT_TEST(TestCountObjectsOnlyOnce) {
        TGraph graph{CreateCycleGraph()};
        TPersistentIndex index{CreateCyclePersistentIndex()};
        TJams jams(index);

        const auto& uuid = 1ull;
        const auto& positionsOnEdge = std::vector<TPositionOnEdge>{
            {0_eid, 0.5},
            {0_eid, 0.0},
            {0_eid, 1.0},
        };
        for (size_t reverse = 0; reverse < 2; ++reverse) {
            const auto& settings = reverse ? REVERSE_TEST_SETTINGS : TEST_SETTINGS;
            for (const auto& posOnEdge : positionsOnEdge) {
                TObjectIndex<ui64> objIndex(graph);
                objIndex.Insert(uuid, posOnEdge);

                TestObjectSearchCallback foundCallback;
                NTaxi::NGraphSearch2::TObjectSearchActions searchActions{foundCallback, objIndex, &jams};
                NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, searchActions, settings);
                searcher.Search(posOnEdge);

                UNIT_ASSERT_EQUAL(foundCallback.GetEdgeIds().size(), 1);
            }
        }
    }

    Y_UNIT_TEST(TestObjectRulesEmptyJams) {
        TGraph graph{CreateRhombusGraph()};
        TPersistentIndex index{CreateRhombusPersistentIndex()};
        TJams jams(index);

        const auto& uuid = 1ull;
        TObjectIndex<ui64> objIndex(graph);
        objIndex.Insert(uuid, TPositionOnEdge{3_eid, 0.5});
        objIndex.Insert(uuid + 1, TPositionOnEdge{4_eid, 0.5});

        TestObjectSearchCallback foundCallback;
        NTaxi::NGraphSearch2::TObjectSearchActions searchActions{foundCallback, objIndex, &jams};
        NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, searchActions, TEST_SETTINGS);
        searcher.Search(0_eid);

        std::vector<TId> res{3_eid, 4_eid};
        std::vector<TWeight> expWeights{3, 1};
        UNIT_ASSERT_EQUAL(foundCallback.GetEdgeIds(), res);
        UNIT_ASSERT_EQUAL(foundCallback.GetEdgeWeights(), expWeights);
    }

    Y_UNIT_TEST(TestObjectRulesStartFromPositionOnEdge) {
        TGraph graph{CreateGiantRhombusGraph()};
        TPersistentIndex index{CreateRhombusPersistentIndex()};
        TJams jams(index);

        const auto& uuid = 1ull;
        TObjectIndex<ui64> objIndex(graph);
        objIndex.Insert(uuid, TPositionOnEdge{3_eid, 0.5});
        objIndex.Insert(uuid + 1, TPositionOnEdge{4_eid, 0.5});

        TestObjectSearchCallback foundCallback;
        NTaxi::NGraphSearch2::TObjectSearchActions searchActions{foundCallback, objIndex, &jams};
        NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, searchActions, TEST_SETTINGS);
        searcher.Search(TPositionOnEdge{0_eid, 0.5});

        std::vector<TId> res{3_eid, 4_eid};
        std::vector<TWeight> expDistancesFromStart{1500, 2500};
        UNIT_ASSERT_EQUAL(foundCallback.GetEdgeIds(), res);
        UNIT_ASSERT_EQUAL(foundCallback.GetDistancesFromStart(), expDistancesFromStart);
        Cout << "uuid 1 distance: " << foundCallback.GetDistancesToObjects()[uuid] << Endl;
        Cout << "uuid 2 distance: " << foundCallback.GetDistancesToObjects()[uuid+1] << Endl;
        UNIT_ASSERT_EQUAL(foundCallback.GetDistancesToObjects()[uuid], 3000);
        UNIT_ASSERT_EQUAL(foundCallback.GetDistancesToObjects()[uuid+1], 3000);
    }

    Y_UNIT_TEST(TestObjectRulesStartFromPositionOnEdgeReverse) {
        TGraph graph{CreateGiantRhombusGraphReversed()};
        TPersistentIndex index{CreateRhombusPersistentIndex()};
        TJams jams(index);

        const auto& uuid = 1ull;
        TObjectIndex<ui64> objIndex(graph);
        objIndex.Insert(uuid, TPositionOnEdge{3_eid, 0.5});
        objIndex.Insert(uuid + 1, TPositionOnEdge{4_eid, 0.5});

        TestObjectSearchCallback foundCallback;
        NTaxi::NGraphSearch2::TObjectSearchActions searchActions{foundCallback, objIndex, &jams};
        NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, searchActions, REVERSE_TEST_SETTINGS);
        searcher.Search(TPositionOnEdge{0_eid, 0.5});

        std::vector<TId> res{3_eid, 4_eid};
        std::vector<TWeight> expDistancesFromStart{1500, 2500};
        UNIT_ASSERT_EQUAL(foundCallback.GetEdgeIds(), res);
        UNIT_ASSERT_EQUAL(foundCallback.GetDistancesFromStart(), expDistancesFromStart);
        Cout << "uuid 1 distance: " << foundCallback.GetDistancesToObjects()[uuid] << Endl;
        Cout << "uuid 2 distance: " << foundCallback.GetDistancesToObjects()[uuid+1] << Endl;
        UNIT_ASSERT_EQUAL(foundCallback.GetDistancesToObjects()[uuid], 3000);
        UNIT_ASSERT_EQUAL(foundCallback.GetDistancesToObjects()[uuid+1], 3000);
    }

    Y_UNIT_TEST(TestObjectRulesStartSameEdge) {
        TGraph graph{CreateGiantCycleGraph()};
        TPersistentIndex index{CreateCyclePersistentIndex()};
        TJams jams(index);

        const auto& uuid = 1ull;
        TObjectIndex<ui64> objIndex(graph);
        objIndex.Insert(uuid, TPositionOnEdge{0_eid, 0.1});
        objIndex.Insert(uuid + 1, TPositionOnEdge{0_eid, 0.6});
        objIndex.Insert(uuid + 2, TPositionOnEdge{2_eid, 0.4});

        TestObjectSearchCallback foundCallback;
        NTaxi::NGraphSearch2::TObjectSearchActions searchActions{foundCallback, objIndex, &jams};
        NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, searchActions, TEST_SETTINGS);
        searcher.Search(TPositionOnEdge{0_eid, 0.3});

        Cout << "uuid 1 distance: " << foundCallback.GetDistancesToObjects()[uuid] << Endl;
        Cout << "uuid 2 distance: " << foundCallback.GetDistancesToObjects()[uuid+1] << Endl;
        Cout << "uuid 3 distance: " << foundCallback.GetDistancesToObjects()[uuid+2] << Endl;
        UNIT_ASSERT_DOUBLES_EQUAL(foundCallback.GetDistancesToObjects()[uuid], 2800, 1e-2);
        UNIT_ASSERT_DOUBLES_EQUAL(foundCallback.GetDistancesToObjects()[uuid+1], 300, 1e-2);
        UNIT_ASSERT_DOUBLES_EQUAL(foundCallback.GetDistancesToObjects()[uuid+2], 2100, 1e-2);
    }

    /// Same, but on small cycle, with edge length == 1. This will test
    /// that we don't loose precision due to fringe being unsigned-int-based
    Y_UNIT_TEST(TestObjectRulesStartSameEdge2) {
        TGraph graph{CreateCycleGraph()};
        TPersistentIndex index{CreateCyclePersistentIndex()};
        TJams jams(index);

        const auto& uuid = 1ull;
        TObjectIndex<ui64> objIndex(graph);
        objIndex.Insert(uuid, TPositionOnEdge{0_eid, 0.1});
        objIndex.Insert(uuid + 1, TPositionOnEdge{0_eid, 0.6});
        objIndex.Insert(uuid + 2, TPositionOnEdge{2_eid, 0.4});

        TestObjectSearchCallback foundCallback;
        NTaxi::NGraphSearch2::TObjectSearchActions searchActions{foundCallback, objIndex, &jams};
        NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, searchActions, TEST_SETTINGS);
        searcher.Search(TPositionOnEdge{0_eid, 0.3});

        Cout << "uuid 1 distance: " << foundCallback.GetDistancesToObjects()[uuid] << Endl;
        Cout << "uuid 2 distance: " << foundCallback.GetDistancesToObjects()[uuid+1] << Endl;
        Cout << "uuid 3 distance: " << foundCallback.GetDistancesToObjects()[uuid+2] << Endl;
        UNIT_ASSERT_DOUBLES_EQUAL(foundCallback.GetDistancesToObjects()[uuid], 2.8, 1e-2);
        UNIT_ASSERT_DOUBLES_EQUAL(foundCallback.GetDistancesToObjects()[uuid+1], 0.3, 1e-2);
        UNIT_ASSERT_DOUBLES_EQUAL(foundCallback.GetDistancesToObjects()[uuid+2], 2.1, 1e-2);
    }

    Y_UNIT_TEST(TestObjectRulesStartSameEdgeReverse) {
        TGraph graph{CreateGiantCycleGraph()};
        TPersistentIndex index{CreateCyclePersistentIndex()};
        TJams jams(index);

        const auto& uuid = 1ull;
        TObjectIndex<ui64> objIndex(graph);
        objIndex.Insert(uuid, TPositionOnEdge{0_eid, 0.1});
        objIndex.Insert(uuid + 1, TPositionOnEdge{0_eid, 0.6});
        objIndex.Insert(uuid + 2, TPositionOnEdge{2_eid, 0.4});

        TestObjectSearchCallback foundCallback;
        NTaxi::NGraphSearch2::TObjectSearchActions searchActions{foundCallback, objIndex, &jams};
        NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, searchActions, REVERSE_TEST_SETTINGS);
        searcher.Search(TPositionOnEdge{0_eid, 0.3});

        Cout << "uuid 1 distance: " << foundCallback.GetDistancesToObjects()[uuid] << Endl;
        Cout << "uuid 1 distance: " << foundCallback.GetDistancesToObjects()[uuid] << Endl;
        Cout << "uuid 2 distance: " << foundCallback.GetDistancesToObjects()[uuid+1] << Endl;
        Cout << "uuid 3 distance: " << foundCallback.GetDistancesToObjects()[uuid+2] << Endl;
        UNIT_ASSERT_DOUBLES_EQUAL(foundCallback.GetDistancesToObjects()[uuid], 200, 1e-2); // should be 200, but lost 1 to rounding error
        UNIT_ASSERT_DOUBLES_EQUAL(foundCallback.GetDistancesToObjects()[uuid+1], 2700, 1e-2);
        UNIT_ASSERT_DOUBLES_EQUAL(foundCallback.GetDistancesToObjects()[uuid+2], 900, 1e-2);
    }

    Y_UNIT_TEST(TestObjectRulesWithJams) {
        TGraph graph{CreateRhombusGraph()};
        TPersistentIndex index{CreateRhombusPersistentIndex()};
        TJams jams(index);

        const auto& uuid = 1ull;
        TObjectIndex<ui64> objIndex(graph);
        objIndex.Insert(uuid, TPositionOnEdge{3_eid, 0.5});
        objIndex.Insert(uuid + 1, TPositionOnEdge{4_eid, 0.5});

        // add jams to first edge
        jams.AddJam(1_eid, 0.02);

        TestObjectSearchCallback foundCallback;
        NTaxi::NGraphSearch2::TObjectSearchActions searchActions{foundCallback, objIndex, &jams};
        NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, searchActions, TEST_SETTINGS);
        searcher.Search(0_eid);

        // edge and weights are in reversed order, because we made a jam on first edge.
        std::vector<TId> res{4_eid, 3_eid};
        std::vector<TWeight> expWeights{1, 3};
        UNIT_ASSERT_EQUAL(foundCallback.GetEdgeIds(), res);
        UNIT_ASSERT_EQUAL(foundCallback.GetEdgeWeights(), expWeights);
    }

    Y_UNIT_TEST(TestObjectRulesLeewayCounting) {
        TGraph graph{CreateRhombusGraphReversed()};
        TPersistentIndex index{CreateRhombusPersistentIndex()};
        const auto& now = std::chrono::system_clock::now();
        TClosures closures(index, now);

        const auto& uuid = 1ull;
        // One driver on each edge, needed for OnFoundObjects to be called at every edge
        TObjectIndex<ui64> objIndex(graph);
        objIndex.Insert(uuid, TPositionOnEdge{0_eid, 0.5});
        objIndex.Insert(uuid + 1, TPositionOnEdge{1_eid, 0.5});
        objIndex.Insert(uuid + 2, TPositionOnEdge{2_eid, 0.5});
        objIndex.Insert(uuid + 3, TPositionOnEdge{3_eid, 0.5});
        objIndex.Insert(uuid + 4, TPositionOnEdge{4_eid, 0.5});
        objIndex.Insert(uuid + 5, TPositionOnEdge{5_eid, 0.5});

        // add closure to 2 edge
        const int kRegion = 0;
        const auto two_seconds_after = now + std::chrono::seconds(2);
        const auto three_seconds_after = now + std::chrono::seconds(3);
        const auto four_seconds_after = now + std::chrono::seconds(4);
        const auto five_seconds_after = now + std::chrono::seconds(5);
        const auto six_seconds_after = now + std::chrono::seconds(6);
        closures.AddClosure(2_eid, kRegion, two_seconds_after, four_seconds_after);
        closures.AddClosure(3_eid, kRegion, four_seconds_after, six_seconds_after);
        closures.AddClosure(5_eid, kRegion, three_seconds_after, five_seconds_after);

        // This closure happened in the past, it musn't affect anything now
        closures.AddClosure(1_eid, kRegion, now - std::chrono::seconds(10), now - std::chrono::seconds(5));

        // The graph now looks like this.
        ///    vertices             edges
        ///       0                   x search point, start edge
        ///       |                   | length 0
        ///       |                   | leeway: INF
        ///       1                   x
        ///      / \       length 1  / \ length: 2, leeway: 0 (2-2)
        ///     /   \               /   \ closure: [2; 4].
        ///    2     3             x     x
        ///     \   /      length 3 \   / length: 1
        ///      \ /  closure [4; 6] \ /  leeway: -1
        ///       4   leeway: 1 (4-3) x
        ///       |                   | length 1
        ///       |                   | closure [3; 5]
        ///       5                   x leeway must be -2 here.
        ///                             Despite there is a path with leeway 0, the shorter path with lowest leeway is preferrable.

        TestObjectSearchCallback foundCallback;
        const int32_t INF = NTaxi::NGraphSearch2::INF_LEEWAY;

        // Test with enabled leeway counting
        {
            NTaxi::NGraphSearch2::TObjectSearchActions searchActions{foundCallback, objIndex, nullptr, &closures};
            searchActions.SetLeewaysCountMode(true);
            NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, searchActions, REVERSE_TEST_SETTINGS);
            searcher.Search(0_eid);

            const auto actualLeeways = foundCallback.GetEdgeLeeways();

            std::unordered_map<TId, int32_t> expectedLeeways = {{0_eid, INF}, {1_eid, INF}, {2_eid, 0}, {3_eid, 1}, {4_eid, -1}, {5_eid, -2}};
            UNIT_ASSERT_EQUAL(foundCallback.GetEdgeLeeways(), expectedLeeways);
        }

        // Test with disabled leeway counting, all leeways must be INF
        {
            NTaxi::NGraphSearch2::TObjectSearchActions searchActions{foundCallback, objIndex, nullptr, &closures};
            searchActions.SetLeewaysCountMode(false);
            NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, searchActions, REVERSE_TEST_SETTINGS);
            searcher.Search(0_eid);

            const auto actualLeeways = foundCallback.GetEdgeLeeways();

            std::unordered_map<TId, int32_t> expectedLeeways = {{0_eid, INF}, {1_eid, INF}, {2_eid, INF}, {3_eid, INF}, {4_eid, INF}, {5_eid, INF}};
            UNIT_ASSERT_EQUAL(foundCallback.GetEdgeLeeways(), expectedLeeways);
        }
    }

    Y_UNIT_TEST(TestObjectRulesLeewayCountStartFromClosure) {
        TGraph graph{BuildGraphForDijkstraFromWikipedia()};
        TPersistentIndex index{CreatePersistentIndexForGraphFromWikipedia()};
        const auto& now = std::chrono::system_clock::now();
        TClosures closures(index, now);

        const auto& uuid = 1ull;
        // One driver on each edge, needed for OnFoundObjects to be called at every edge
        TObjectIndex<ui64> objIndex(graph);
        for (size_t i = 0; i < 10; ++i) {
            objIndex.Insert(uuid + i, TPositionOnEdge{TEdgeId(i), 0.5});
        }
        // add closure to edges
        const int kRegion = 0;
        closures.AddClosure(9_eid, kRegion, now - std::chrono::seconds(10), now + std::chrono::seconds(5));
        closures.AddClosure(6_eid, kRegion, now - std::chrono::seconds(10), now + std::chrono::seconds(5));
        closures.AddClosure(5_eid, kRegion, now - std::chrono::seconds(10), now + std::chrono::seconds(5));

        closures.AddClosure(1_eid, kRegion, now + std::chrono::seconds(3), now + std::chrono::seconds(6));
        closures.AddClosure(2_eid, kRegion, now + std::chrono::seconds(4), now + std::chrono::seconds(7));

        TestObjectSearchCallback foundCallback;
        NTaxi::NGraphSearch2::TObjectSearchActions searchActions{foundCallback, objIndex, nullptr, &closures};
        searchActions.SetLeewaysCountMode(true);
        NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, searchActions, REVERSE_TEST_SETTINGS);
        searcher.Search(9_eid);

        const int32_t INF = NTaxi::NGraphSearch2::INF_LEEWAY;
        const auto actualLeeways = foundCallback.GetEdgeLeeways();

        std::unordered_map<TId, int32_t> expectedLeeways = {{0_eid, -5}, {1_eid, -4}, {2_eid, -5}, {3_eid, INF}, {4_eid, INF}, {7_eid, INF}, {9_eid, INF}};

        for (auto [k, v]: expectedLeeways) std::cout << k << ' ' << v << '\n';
        std::cout << '\n';
        for (auto [k, v]: actualLeeways) std::cout << k << ' ' << v << '\n';

        std::cout << std::endl;
        UNIT_ASSERT_EQUAL(foundCallback.GetEdgeLeeways(), expectedLeeways);
    }

   Y_UNIT_TEST(TestObjectRulesWithClosures) {
        TGraph graph{CreateRhombusGraph()};
        TPersistentIndex index{CreateRhombusPersistentIndex()};
        const auto& now = std::chrono::system_clock::now();
        const auto& some_future_moment = now + std::chrono::hours(10);
        const auto& some_past_moment = now - std::chrono::hours(10);
        TClosures closures(index, now);

        const auto& uuid = 1ull;
        TObjectIndex<ui64> objIndex(graph);
        objIndex.Insert(uuid, TPositionOnEdge{3_eid, 0.5});
        objIndex.Insert(uuid + 1, TPositionOnEdge{4_eid, 0.5});

        // add closure to 2 edge
        const int kRegion = 0;
        closures.AddClosure(2_eid, kRegion, some_past_moment, some_future_moment);

        UNIT_ASSERT(closures.IsClosedAtMoment(2_eid, now));

        TestObjectSearchCallback foundCallback;
        NTaxi::NGraphSearch2::TObjectSearchActions searchActions{foundCallback, objIndex, nullptr, &closures};
        NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, searchActions, TEST_SETTINGS);
        searcher.Search(0_eid);

        // there is only one driver in response, because we could not reach the second one
        // because of the closure on 2 edge.
        std::vector<TId> res{3_eid};
        std::vector<TWeight> expWeights{3};
        UNIT_ASSERT_EQUAL(foundCallback.GetEdgeIds(), res);
        UNIT_ASSERT_EQUAL(foundCallback.GetEdgeWeights(), expWeights);
    }

    Y_UNIT_TEST(TestObjectRulesStartFromClosedByClosureEdge) {
        TGraph graph{CreateRhombusGraph()};
        TPersistentIndex index{CreateRhombusPersistentIndex()};
        const auto& now = std::chrono::system_clock::now();
        const auto& some_future_moment = now + std::chrono::hours(10);
        const auto& some_past_moment = now - std::chrono::hours(10);
        TClosures closures(index, now);

        const auto& uuid = 1ull;
        TObjectIndex<ui64> objIndex(graph);
        objIndex.Insert(uuid, TPositionOnEdge{3_eid, 0.5});
        objIndex.Insert(uuid + 1, TPositionOnEdge{4_eid, 0.5});

        // add closure to 0 and 1 edge
        const int kRegion = 0;
        closures.AddClosure(0_eid, kRegion, some_past_moment, some_future_moment);
        closures.AddClosure(1_eid, kRegion, some_past_moment, some_future_moment);

        UNIT_ASSERT(closures.IsClosedAtMoment(0_eid, now));
        UNIT_ASSERT(closures.IsClosedAtMoment(1_eid, now));

        TestObjectSearchCallback foundCallback;
        NTaxi::NGraphSearch2::TObjectSearchActions searchActions{foundCallback, objIndex, nullptr, &closures};
        NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, searchActions, TEST_SETTINGS);
        searcher.Search(0_eid);

        // because closures on start edges 0 and 1 not considered,
        // that's why we found all drivers like without closures.
        std::vector<TId> res{3_eid, 4_eid};
        std::vector<TWeight> expWeights{3, 1};
        UNIT_ASSERT_EQUAL(foundCallback.GetEdgeIds(), res);
        UNIT_ASSERT_EQUAL(foundCallback.GetEdgeWeights(), expWeights);

        // Search again to check that init for closures function works correctly.
        foundCallback.Reset();
        searcher.Search(0_eid);
        UNIT_ASSERT_EQUAL(foundCallback.GetEdgeIds(), res);
        UNIT_ASSERT_EQUAL(foundCallback.GetEdgeWeights(), expWeights);
    }

    Y_UNIT_TEST(TestObjectRulesWithYards) {
        TGraph graph{CreateRhombusGraphWithPasses()};

        const auto& uuid = 1ull;
        TObjectIndex<ui64> objIndex(graph);

        objIndex.Insert(uuid, TPositionOnEdge{2_eid, 0.5});
        objIndex.Insert(uuid + 1, TPositionOnEdge{5_eid, 0.5});

        // Both drivers in yards
        {
            TestObjectSearchCallback foundCallback;
            NTaxi::NGraphSearch2::TObjectSearchActions searchActions{foundCallback, objIndex};
            NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, searchActions, TEST_SETTINGS);
            searcher.Search(2_eid);

            const TVector<TId> expectedRes{2_eid, 5_eid};
            const auto& res = foundCallback.GetEdgeIds();
            UNIT_ASSERT_EQUAL(res, expectedRes);

            const auto& stats = searchActions.GetStats();
            // we started from yard, so this yard no counted
            UNIT_ASSERT_EQUAL(1u, stats.YardsStats.YardsVisited);
            UNIT_ASSERT_EQUAL(0u, stats.YardsStats.YardsSkipped);
        }

        // Remove driver from from edge 5
        objIndex.Remove(uuid + 1);
        {
            TestObjectSearchCallback foundCallback;
            NTaxi::NGraphSearch2::TObjectSearchActions searchActions{foundCallback, objIndex};
            NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, searchActions, TEST_SETTINGS);
            searcher.Search(2_eid);

            const TVector<TId> expectedRes{2_eid};
            const auto& res = foundCallback.GetEdgeIds();
            UNIT_ASSERT_EQUAL(res, expectedRes);

            const auto& stats = searchActions.GetStats();
            // we started from yard, so this yard no counted
            UNIT_ASSERT_EQUAL(0u, stats.YardsStats.YardsVisited);
            // skip yard without any drivers
            UNIT_ASSERT_EQUAL(1u, stats.YardsStats.YardsSkipped);
        }
    }
    
    Y_UNIT_TEST(TestObjectRulesLooseFieldRoad) {
        TGraph graph{CreateRhombusGraphWithFieldRoad()};

        const auto& uuid = 1ull;
        TObjectIndex<ui64> objIndex(graph);

        objIndex.Insert(uuid, TPositionOnEdge{1_eid, 0.5});

        TestObjectSearchCallback foundCallback;
        NTaxi::NGraphSearch2::TObjectSearchActions searchActions{foundCallback, objIndex};
        NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, searchActions, REVERSE_TEST_SETTINGS);
        searcher.Search(5_eid);

        // Should find the driver because field road must be labeled as yard
        const TVector<TId> expectedRes{1_eid};
        const auto& res = foundCallback.GetEdgeIds();
        UNIT_ASSERT_EQUAL(res, expectedRes);

        const auto& stats = searchActions.GetStats();
        UNIT_ASSERT_EQUAL(0u, stats.YardsStats.YardsVisited);
        UNIT_ASSERT_EQUAL(0u, stats.YardsStats.YardsSkipped);
    }        

    Y_UNIT_TEST(TestObjectRulesFieldBetweenHighways) {
        TGraph graph{CreateGraphWithFieldBetweenStreets()};

        const auto& uuid = 1ull;
        TObjectIndex<ui64> objIndex(graph);

        objIndex.Insert(uuid, TPositionOnEdge{0_eid, 0.5});

        TestObjectSearchCallback foundCallback;
        NTaxi::NGraphSearch2::TObjectSearchActions searchActions{foundCallback, objIndex};
        NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, searchActions, REVERSE_TEST_SETTINGS);
        searcher.Search({5_eid, 0.5});

        // Should find the driver because field road is not part of yard now
        const TVector<TId> expectedRes{0_eid};
        const auto& res = foundCallback.GetEdgeIds();
        UNIT_ASSERT_EQUAL(res, expectedRes);

        const auto& stats = searchActions.GetStats();
        // Yard must be skipped because it is empty
        UNIT_ASSERT_EQUAL(0u, stats.YardsStats.YardsVisited);
        UNIT_ASSERT_EQUAL(1u, stats.YardsStats.YardsSkipped);
    }        

    Y_UNIT_TEST(TestObjectRulesFieldBetweenYards) {
        TGraph graph{CreateGraphWithFieldBetweenYards()};

        const auto& uuid = 1ull;
        TObjectIndex<ui64> objIndex(graph);

        objIndex.Insert(uuid, TPositionOnEdge{0_eid, 0.5});
        objIndex.Insert(uuid+1, TPositionOnEdge{5_eid, 0.5});

        TestObjectSearchCallback foundCallback;
        NTaxi::NGraphSearch2::TObjectSearchActions searchActions{foundCallback, objIndex};
        {
            NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, searchActions, REVERSE_TEST_SETTINGS);
            searcher.Search({4_eid, 0.5});

            // Shouldn't find anybody because an empty yard is on the way, field is not part of the yard
            const auto& res = foundCallback.GetEdgeIds();
            UNIT_ASSERT_EQUAL(res.size(), 0);

            const auto& stats = searchActions.GetStats();
            // Yard must be skipped because it is empty
            UNIT_ASSERT_EQUAL(0u, stats.YardsStats.YardsVisited);
            UNIT_ASSERT_EQUAL(1u, stats.YardsStats.YardsSkipped);
        }
        {
            NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, searchActions, REVERSE_TEST_SETTINGS);
            searcher.Search({3_eid, 0.5});

            // Now should find both drivers because starting from yard
            const auto& res = foundCallback.GetEdgeIds();
            UNIT_ASSERT_EQUAL(res.size(), 2);

            const auto& stats = searchActions.GetStats();
            // Yard must be visited
            UNIT_ASSERT_EQUAL(1u, stats.YardsStats.YardsVisited);
            UNIT_ASSERT_EQUAL(0u, stats.YardsStats.YardsSkipped);
        }
    }        
}
