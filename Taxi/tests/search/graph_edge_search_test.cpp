#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <taxi/graph/libs/graph/graph_data_builder.h>
#include <taxi/graph/libs/search/dijkstra_edge_searcher.h>

#include <iostream>

#include <taxi/graph/libs/graph-test/graph_test_data.h>

#define UNIT_ASSERT_OPTIONAL_DOUBLES_EQUAL(E, A, D)                                        \
    do {                                                                                   \
        if (!(E) && !(A))                                                                  \
            continue;                                                                      \
        if ((!(E) && (A)) || ((E) && (!A))) {                                              \
            if (!E) {                                                                      \
                const auto _as = ToString(ToTestDouble(A));                            \
                auto&& failMsg = Sprintf("left is std::nullopt, right is %s", _as.data()); \
                UNIT_FAIL(failMsg);                                                        \
            }                                                                              \
            const auto _es = ToString(ToTestDouble(E));                                \
            auto&& failMsg = Sprintf("left is %s, right is std::nullopt", _es.data());     \
            UNIT_FAIL(failMsg);                                                            \
        }                                                                                  \
        UNIT_ASSERT_DOUBLES_EQUAL(ToTestDouble(E), ToTestDouble(A), D);                                          \
    } while (false)


using NTaxi::NGraph2::TEdge;
using NTaxi::NGraph2::TEdgeData;
using NTaxi::NGraph2::TEdgeId;
using NTaxi::NGraph2::TGraph;
using NTaxi::NGraph2::TId;
using NTaxi::NGraph2::TPersistentEdgeId;
using NTaxi::NGraph2::TPositionOnEdge;
using NTaxi::NGraph2::TRoadGraphDataBuilder;
using NTaxi::NGraph2::TVertexId;
using NTaxi::NGraphSearch2::EEdgeVisitState;
using NTaxi::NGraphSearch2::EStopReason;
using NTaxi::NGraphSearch2::IEdgeSearchActions;
using NTaxi::NGraphSearch2::TEdgeSearchSettings;
using NTaxi::NGraphSearch2::TWeight;
using NTaxi::NGraphSearch2::Impl::TPathGeolength;

using namespace NTaxi::NGraph2Literals;

namespace {

    double ToTestDouble(const std::optional<NTaxi::NGraphSearch2::Impl::TPathGeolength>& value) {
      Y_VERIFY(value);
      return value->value();
    }

    double ToTestDouble(const std::optional<double>& value) {
      Y_VERIFY(value);
      return *value;
    }

    /* Unused at the moment, but generally required
    double ToTestDouble(double value) {
      return value;
    }

    double ToTestDouble(NTaxi::NGraphSearch2::Impl::TPathGeolength value) {
      return value.value();
    }*/

    struct TestSearchActions: public IEdgeSearchActions {
        TestSearchActions(bool reverseEdges)
            : reverseEdges(reverseEdges)
        {
        }

        TEdgeDiscoverResult OnDiscoveredEdge(const TGraph& graph, const TEdge& currentEdge,
                                             TWeight currentDistance, TEdgeId discoveredEdgeId) override {
            std::ignore = graph;
            std::ignore = currentEdge;
            std::ignore = currentDistance;
            std::ignore = discoveredEdgeId;
            DiscoveredEdgeDistances.insert({discoveredEdgeId, currentDistance});

            return {false, 0};
        }

        TEdgeVisitResult OnVisitedEdge(const TGraph& graph, TEdgeId edgeId, TWeight currentDistance,
                                       double fromFraction, double toFraction) override {
            const auto& edge = graph.GetEdge(edgeId);
            const auto& edgeData = graph.GetEdgeData(edgeId);

            const TWeight edgeWeight = std::llround(edgeData.Length / edgeData.Speed * std::fabs(toFraction - fromFraction));

            const auto& endEdgeVertexId = reverseEdges ? edge.Source : edge.Target;
            const auto& startEdgeVertexId = reverseEdges ? edge.Target : edge.Source;

            VertexVisitOrder.push_back(endEdgeVertexId);
            EdgeVisitOrder.push_back(edgeId);
            if (reverseEdges && fromFraction == 1.0 || !reverseEdges && fromFraction == 0.0) {
                EdgeFinalDistances[edgeId] = currentDistance;
            }

            // To check for correctness, we emulate 'seach by vertexes' via edges search:
            // 1. min distance to vertex is min( (min distance to edge) for every outgoing edge)
            // 2. preceding edge is an preceding edge for edge selected above
            if (UpdateWithMin(FinalDistances, endEdgeVertexId, currentDistance + edgeWeight)) {
                PrecedingEdges[endEdgeVertexId] = edgeId;
            }
            if (reverseEdges && fromFraction == 1.0 || !reverseEdges && fromFraction == 0.0) {
                UpdateWithMin(FinalDistances, startEdgeVertexId, currentDistance);
            }
            DiscoveredDistances.insert({endEdgeVertexId, currentDistance + edgeWeight});

            return {EEdgeVisitState::Continue, edgeWeight};
        }

        void InitBeforeSearch() final {
            Clear();
        }

        template <typename TId>
        static bool UpdateWithMin(std::unordered_map<TId, TWeight>& map, TId targetId, TWeight targetWeight) {
            auto fit = map.find(targetId);
            if (fit == map.end()) {
                // Key not present. inserting
                map.insert({targetId, targetWeight});

                return true;
            } else {
                // Key present. Comparing
                if (targetWeight < fit->second) {
                    // Updating
                    fit->second = targetWeight;
                    return true;
                }
            }

            return false;
        }

        void Clear() {
            DiscoveredDistances.clear();
            DiscoveredEdgeDistances.clear();
            FinalDistances.clear();
            EdgeFinalDistances.clear();
            PrecedingEdges.clear();
            VertexVisitOrder.clear();
            EdgeVisitOrder.clear();
        }

        bool reverseEdges;
        std::unordered_map<TVertexId, TWeight> DiscoveredDistances;
        std::unordered_map<TEdgeId, TWeight> DiscoveredEdgeDistances;
        std::unordered_map<TVertexId, TWeight> FinalDistances;
        std::unordered_map<TEdgeId, TWeight> EdgeFinalDistances;
        std::unordered_map<TVertexId, TId> PrecedingEdges;
        std::vector<TVertexId> VertexVisitOrder;
        std::vector<TEdgeId> EdgeVisitOrder;
    };
}

class TGraphEdgeDijkstraSearchFixture: public ::NUnitTest::TBaseTestCase, public NTaxi::NGraph2::TGraphTestData {
};

Y_UNIT_TEST_SUITE_F(graph_dijkstra_edge_search, TGraphEdgeDijkstraSearchFixture) {
    Y_UNIT_TEST(dijkstra_search_rhombus) {
        for (auto with_edge_storage : std::vector<bool>{ true, false }) {
            TGraph graph{CreateRhombusGraph()};
            if (with_edge_storage) {
                graph.BuildEdgeStorage(32);
            }
            TestSearchActions actions(false);
            NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, actions);
            const auto searchStopReason = searcher.Search(0_eid);
            UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);
            // clang-format off
        std::unordered_map<TEdgeId, TWeight> expectedDiscoveredDistances = {
            {1_eid, 0},
            {2_eid, 0},
            {3_eid, 1},
            {4_eid, 2},
            {5_eid, 4},
        };
        std::unordered_map<TVertexId, TWeight> expectedFinalDistances = {
            {0_vid, 0},
            {1_vid, 0},
            {2_vid, 1},
            {3_vid, 2},
            {4_vid, 3},
            {5_vid, 4},
        };
        std::unordered_map<TVertexId, TId> expectedPrecedingEdges = {
            {1_vid, 0_eid},
            {2_vid, 1_eid},
            {3_vid, 2_eid},
            {4_vid, 4_eid},
            {5_vid, 5_eid},
        };
            // clang-format on
            std::vector<TVertexId> expectedVertexVisitOrder = {1_vid, 2_vid, 3_vid, 4_vid, 4_vid, 5_vid};
            std::vector<TEdgeId> expectedEdgeVisitOrder = {0_eid, 1_eid, 2_eid, 3_eid, 4_eid, 5_eid};

            UNIT_ASSERT_EQUAL(actions.FinalDistances, expectedFinalDistances);
            UNIT_ASSERT_EQUAL(actions.EdgeVisitOrder, expectedEdgeVisitOrder);
            UNIT_ASSERT_EQUAL(actions.VertexVisitOrder, expectedVertexVisitOrder);

            UNIT_ASSERT_EQUAL(actions.DiscoveredEdgeDistances, expectedDiscoveredDistances);
            UNIT_ASSERT_EQUAL(actions.PrecedingEdges, expectedPrecedingEdges);

            std::vector<TId> path_5 = searcher.GetPath(5_eid);
            std::vector<TId> expected_path_5 = {0_eid, 2_eid, 4_eid, 5_eid};
            UNIT_ASSERT_EQUAL(path_5, expected_path_5);

            std::vector<TId> path_3 = searcher.GetPath(3_eid);
            std::vector<TId> expected_path_3 = {0_eid, 1_eid, 3_eid};
            UNIT_ASSERT_EQUAL(path_3, expected_path_3);

            std::vector<TId> path_0 = searcher.GetPath(0_eid);
            std::vector<TId> expected_path_0 = {
                0_eid,
            };
            UNIT_ASSERT_EQUAL(path_0, expected_path_0);

            auto route = searcher.GetRoute({5_eid, 1.0});
            UNIT_ASSERT(route);
            UNIT_ASSERT_EQUAL(path_5, route->Path());

            TPositionOnEdge startPos{0_eid, 0.0};
            TPositionOnEdge finishPos{5_eid, 1.0};
            UNIT_ASSERT_EQUAL(route->StartPosition(), startPos);
            UNIT_ASSERT_EQUAL(route->FinishPosition(), finishPos);
        }
    }
    Y_UNIT_TEST(dijkstra_search_rhombus_not_passable_edges) {
        TGraph graph{CreateRhombusGraphNotPassable()};
        graph.BuildEdgeStorage(32);
        TestSearchActions actions(false);
        NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, actions);
        const auto searchStopReason = searcher.Search(0_eid);
        UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);

        // clang-format on
        std::vector<TEdgeId> expectedEdgeVisitOrder = {0_eid, 1_eid};

        UNIT_ASSERT_EQUAL(actions.EdgeVisitOrder, expectedEdgeVisitOrder);
    }
    Y_UNIT_TEST(get_edges_visited) {
        for (auto with_edge_storage : std::vector<bool>{ true, false }) {
            TGraph graph{CreateRhombusGraph()};
            if (with_edge_storage) {
                graph.BuildEdgeStorage(32);
            }
            TestSearchActions actions(false);
            NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, actions);
            const auto searchStopReason = searcher.Search(0_eid);
            UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);
            UNIT_ASSERT_EQUAL(6, searcher.GetEdgesVisited());
        }
    }

    Y_UNIT_TEST(test_recognize_toll_road) {
        for (auto with_edge_storage : std::vector<bool>{ true, false }) {
            TGraph graph{CreateRhombusGraphWithTollRoad()};
            if (with_edge_storage) {
                graph.BuildEdgeStorage(32);
            }
            TestSearchActions actions(false);
            NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, actions);

            {
                searcher.Search(0_eid);

                const auto routeInfo = searcher.GetRouteInfo({5_eid, 0.0});
                UNIT_ASSERT(routeInfo);
                UNIT_ASSERT(routeInfo->TollRoadPassed);

                const auto anotherRouteInfo = searcher.GetRouteInfo({3_eid, 0.0});
                UNIT_ASSERT(anotherRouteInfo);
                UNIT_ASSERT(!anotherRouteInfo->TollRoadPassed);
            }

            {
                searcher.Search(4_eid);

                const auto routeInfo = searcher.GetRouteInfo({4_eid, 0.0});
                UNIT_ASSERT(routeInfo);
                UNIT_ASSERT(routeInfo->TollRoadPassed);

                const auto anotherRouteInfo = searcher.GetRouteInfo({2_eid, 0.0});
                UNIT_ASSERT(!anotherRouteInfo);
            }

        }
    }

    Y_UNIT_TEST(dijskstra_search_rhombus_path_lengths) {
        for (auto with_edge_storage : std::vector<bool>{true, false}) {
            TGraph graph{CreateRhombusGraph()};
            if (with_edge_storage) {
                graph.BuildEdgeStorage(32);
            }
            TestSearchActions actions(false);
            NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, actions);
            const auto& searchStopReason = searcher.Search(0_eid);
            UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);

            // first - position on edge, second - length of shortest path to this position
            const std::vector<std::pair<TPositionOnEdge, std::optional<TPathGeolength>>> cases = {
                {TPositionOnEdge{1_eid, 0.}, TPathGeolength{0.}},
                {TPositionOnEdge{1_eid, 0.5}, TPathGeolength{0.5}},
                {TPositionOnEdge{1_eid, 1.}, TPathGeolength{1.}},

                {TPositionOnEdge{2_eid, 0.}, TPathGeolength{0.}},
                {TPositionOnEdge{2_eid, 0.5}, TPathGeolength{1.}},
                {TPositionOnEdge{2_eid, 1.}, TPathGeolength{2.}},

                {TPositionOnEdge{3_eid, 0.}, TPathGeolength{1.}},
                {TPositionOnEdge{3_eid, 0.5}, TPathGeolength{2.5}},
                {TPositionOnEdge{3_eid, 1.}, TPathGeolength{4.}},

                {TPositionOnEdge{4_eid, 0.}, TPathGeolength{2.}},
                {TPositionOnEdge{4_eid, 0.5}, TPathGeolength{2.5}},
                {TPositionOnEdge{4_eid, 1.}, TPathGeolength{3.}},

                {TPositionOnEdge{5_eid, 0.}, TPathGeolength{3.}},
                {TPositionOnEdge{5_eid, 0.5}, TPathGeolength{3.5}},
                {TPositionOnEdge{5_eid, 1.}, TPathGeolength{4.}},

                {TPositionOnEdge{666_eid, 1.}, std::nullopt}};

            for (const auto& testCase : cases) {
                const auto& actual = searcher.GetPathLengthInMeters(testCase.first);
                const auto& expected = testCase.second;
                UNIT_ASSERT_OPTIONAL_DOUBLES_EQUAL(actual, expected, 0.0001);
            }
        }
    }

    Y_UNIT_TEST(dijkstra_search_reversed_edges) {
        for (auto with_edge_storage : std::vector<bool>{true, false}) {
            TGraph graph{CreateRhombusGraphReversed()};
            if (with_edge_storage) {
                graph.BuildEdgeStorage(32);
            }

            TestSearchActions actions(true);
            TEdgeSearchSettings settings;
            settings.ReverseEdges = true;

            NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, actions, settings);
            const auto& searchStopReason = searcher.Search(0_eid);
            UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);
            // clang-format off
        std::unordered_map<TEdgeId, TWeight> expectedDiscoveredDistances = {
            {1_eid, 0},
            {2_eid, 0},
            {3_eid, 1},
            {4_eid, 2},
            {5_eid, 4},
        };
        std::unordered_map<TVertexId, TWeight> expectedFinalDistances = {
            {5_vid, 0},
            {0_vid, 0},
            {1_vid, 1},
            {2_vid, 2},
            {3_vid, 3},
            {4_vid, 4},
        };
        std::unordered_map<TVertexId, TId> expectedPrecedingEdges = {
            {0_vid, 0_eid},
            {1_vid, 1_eid},
            {2_vid, 2_eid},
            {3_vid, 4_eid},
            {4_vid, 5_eid},
        };
            // clang-format on
            std::vector<TVertexId> expectedVertexVisitOrder = {1_vid, 2_vid, 3_vid, 4_vid, 4_vid, 5_vid};
            std::vector<TEdgeId> expectedEdgeVisitOrder = {0_eid, 1_eid, 2_eid, 3_eid, 4_eid, 5_eid};

            UNIT_ASSERT_EQUAL(actions.FinalDistances, expectedFinalDistances);
            UNIT_ASSERT_EQUAL(actions.EdgeVisitOrder, expectedEdgeVisitOrder);

            UNIT_ASSERT_EQUAL(actions.DiscoveredEdgeDistances, expectedDiscoveredDistances);
            UNIT_ASSERT_EQUAL(actions.PrecedingEdges, expectedPrecedingEdges);

            std::vector<TId> path_5 = searcher.GetPath(5_eid);
            std::vector<TId> expected_path_5 = {0_eid, 2_eid, 4_eid, 5_eid};
            UNIT_ASSERT_EQUAL(path_5, expected_path_5);

            std::vector<TId> path_3 = searcher.GetPath(3_eid);
            std::vector<TId> expected_path_3 = {0_eid, 1_eid, 3_eid};
            UNIT_ASSERT_EQUAL(path_3, expected_path_3);

            std::vector<TId> path_0 = searcher.GetPath(0_eid);
            std::vector<TId> expected_path_0 = {0_eid};
            UNIT_ASSERT_EQUAL(path_0, expected_path_0);
        }
    }

    Y_UNIT_TEST(dijkstra_search_reversed_rhombus_path_lengths) {
        for (auto with_edge_storage : std::vector<bool>{true, false}) {
            TGraph graph{CreateRhombusGraphReversed()};
            if (with_edge_storage) {
                graph.BuildEdgeStorage(32);
            }

            TestSearchActions actions(true);
            TEdgeSearchSettings settings;
            settings.ReverseEdges = true;

            NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, actions, settings);
            const auto& searchStopReason = searcher.Search(0_eid);
            UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);

            // first - position on edge, second - length of shortest path to this position
            const std::vector<std::pair<TPositionOnEdge, std::optional<double>>> cases = {
                {TPositionOnEdge{1_eid, 1.}, 0.},
                {TPositionOnEdge{1_eid, 0.5}, 0.5},
                {TPositionOnEdge{1_eid, 0.}, 1.},

                {TPositionOnEdge{2_eid, 1.}, 0.},
                {TPositionOnEdge{2_eid, 0.5}, 1.},
                {TPositionOnEdge{2_eid, 0.}, 2.},

                {TPositionOnEdge{3_eid, 1.}, 1.},
                {TPositionOnEdge{3_eid, 0.5}, 2.5},
                {TPositionOnEdge{3_eid, 0.}, 4.},

                {TPositionOnEdge{4_eid, 1.}, 2.},
                {TPositionOnEdge{4_eid, 0.5}, 2.5},
                {TPositionOnEdge{4_eid, 0.}, 3.},

                {TPositionOnEdge{5_eid, 1.}, 3.},
                {TPositionOnEdge{5_eid, 0.5}, 3.5},
                {TPositionOnEdge{5_eid, 0.}, 4.},

                {TPositionOnEdge{666_eid, 1.}, std::nullopt}};

            for (const auto& testCase : cases) {
                const auto& actual = searcher.GetPathLengthInMeters(testCase.first);
                const auto& expected = testCase.second;

                UNIT_ASSERT_OPTIONAL_DOUBLES_EQUAL(actual, expected, 0.0001);
            }
        }
    }

    // Test with standard stop condition
    Y_UNIT_TEST(dijkstra_search_wikipedia_example) {
        for (auto with_edge_storage : std::vector<bool>{true, false}) {
            TGraph graph = BuildGraphForDijkstraFromWikipedia();
            if (with_edge_storage) {
                graph.BuildEdgeStorage(32);
            }

            TestSearchActions actions(false);
            NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, actions);
            const auto& searchStopReason = searcher.Search(0_eid);
            UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);
            // clang-format off
            std::unordered_map<TVertexId, TWeight> expectedFinalDistances = {
                {0_vid, 0},
                {1_vid, 0},
                {2_vid, 7},
                {3_vid, 9},
                {4_vid, 20},
                {5_vid, 11},
                {6_vid, 20},
            };
            std::unordered_map<TEdgeId, TWeight> expectedEdgeFinalDistances = {
                {0_eid, 0},
                {1_eid, 0},
                {2_eid, 0},
                {3_eid, 0},
                {4_eid, 7},
                {5_eid, 7},
                {6_eid, 9},
                {7_eid, 9},
                {8_eid, 20},
                {9_eid, 11},
            };
            std::unordered_map<TVertexId, TId> expectedPrecedingEdges = {
                {1_vid, 0_eid},
                {2_vid, 1_eid},
                {3_vid, 2_eid},
                {4_vid, 6_eid},
                {5_vid, 7_eid},
                {6_vid, 9_eid},
            };
            //std::vector<TVertexId> expectedVertexVisitOrder = {1_vid, 2_vid, 3_vid, 6_vid, 4_vid, 5_vid};
            std::vector<TEdgeId> expectedEdgeVisitOrder = {
                0_eid,
                1_eid,
                2_eid,
                3_eid,
                4_eid,
                5_eid,
                6_eid,
                7_eid,
                9_eid,
                8_eid
            };
            // clang-format on

            Cout << "FinalDistances: "; for (auto [k, v]: actions.FinalDistances) Cout << k.value() << " " << v << ", " << Endl;
            Cout << "EdgeFinalDistances: "; for (auto [k, v]: actions.EdgeFinalDistances) Cout << k.value() << " " << v << ", " << Endl;
            Cout << "PrecedingEdges: "; for (auto [k, v]: actions.PrecedingEdges) Cout << k.value() << " " << v.value() << ", " << Endl;
            Cout << "EdgeVisitOrder: "; for (auto v: actions.EdgeVisitOrder) Cout << v.value() << ", " << Endl;

            UNIT_ASSERT_EQUAL(actions.FinalDistances, expectedFinalDistances);
            UNIT_ASSERT_EQUAL(actions.EdgeFinalDistances, expectedEdgeFinalDistances);
            UNIT_ASSERT_EQUAL(actions.PrecedingEdges, expectedPrecedingEdges);
            UNIT_ASSERT_EQUAL(actions.EdgeVisitOrder, expectedEdgeVisitOrder);

            std::vector<TId> path_5 = searcher.GetPath(5_eid);
            std::vector<TId> expected_path_5 = {0_eid, 1_eid, 5_eid};
            UNIT_ASSERT_EQUAL(path_5, expected_path_5);

            std::vector<TId> path_8 = searcher.GetPath(8_eid);
            std::vector<TId> expected_path_8 = {0_eid, 2_eid, 6_eid, 8_eid};
            UNIT_ASSERT_EQUAL(path_8, expected_path_8);

            std::vector<TId> path_9 = searcher.GetPath(9_eid);
            std::vector<TId> expected_path_9 = {0_eid, 2_eid, 7_eid, 9_eid};
            UNIT_ASSERT_EQUAL(path_9, expected_path_9);
        }
    }

    Y_UNIT_TEST(dijkstra_search_wikipedia_example_path_lengthes) {
        for (auto with_edge_storage : std::vector<bool>{true, false}) {
            TGraph graph = BuildGraphForDijkstraFromWikipedia();
            if (with_edge_storage) {
                graph.BuildEdgeStorage(32);
            }

            TestSearchActions actions(false);
            NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, actions);
            const auto& searchStopReason = searcher.Search(0_eid);
            UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);

            // first - position on edge, second - length of shortest path to this position
            const std::vector<std::pair<TPositionOnEdge, std::optional<double>>> cases = {
                {TPositionOnEdge{1_eid, 0.}, 0.},
                {TPositionOnEdge{1_eid, 0.5}, 3.5},
                {TPositionOnEdge{1_eid, 1.}, 7.},

                {TPositionOnEdge{2_eid, 0.}, 0.},
                {TPositionOnEdge{2_eid, 0.5}, 4.5},
                {TPositionOnEdge{2_eid, 1.}, 9.},

                {TPositionOnEdge{3_eid, 0.}, 0.},
                {TPositionOnEdge{3_eid, 0.5}, 7.},
                {TPositionOnEdge{3_eid, 1.}, 14.},

                {TPositionOnEdge{4_eid, 0.}, 7.},
                {TPositionOnEdge{4_eid, 0.5}, 12.},
                {TPositionOnEdge{4_eid, 1.}, 17.},

                {TPositionOnEdge{5_eid, 0.}, 7.},
                {TPositionOnEdge{5_eid, 0.5}, 14.5},
                {TPositionOnEdge{5_eid, 1.}, 22.},

                {TPositionOnEdge{6_eid, 0.}, 9.},
                {TPositionOnEdge{6_eid, 0.5}, 14.5},
                {TPositionOnEdge{6_eid, 1.}, 20.},

                {TPositionOnEdge{7_eid, 0.}, 9.},
                {TPositionOnEdge{7_eid, 0.5}, 10.},
                {TPositionOnEdge{7_eid, 1.}, 11.},

                {TPositionOnEdge{8_eid, 0.}, 20.},
                {TPositionOnEdge{8_eid, 0.5}, 23.},
                {TPositionOnEdge{8_eid, 1.}, 26.},

                {TPositionOnEdge{9_eid, 0.}, 11.},
                {TPositionOnEdge{9_eid, 0.5}, 15.5},
                {TPositionOnEdge{9_eid, 1.}, 20.},

                {TPositionOnEdge{666_eid, 1.}, std::nullopt}};

            for (const auto& testCase : cases) {
                const auto& actual = searcher.GetPathLengthInMeters(testCase.first);
                const auto& expected = testCase.second;

                UNIT_ASSERT_OPTIONAL_DOUBLES_EQUAL(actual, expected, 0.0001);
            }
        }
    }

    Y_UNIT_TEST(dijkstra_search_stop_by_distance) {
        for (auto with_edge_storage : std::vector<bool>{true, false}) {
            TGraph graph = BuildGraphForDijkstraFromWikipedia();
            if (with_edge_storage) {
                graph.BuildEdgeStorage(32);
            }

            TestSearchActions actions(false);
            TEdgeSearchSettings settings;
            settings.StopCondition = [](const TGraph&, TEdgeId, TWeight currentDistance) {
                return currentDistance >= 8;
            };

            NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, actions, settings);
            searcher.SetIterationsCountPerStopCheck(1);
            const auto& searchStopReason = searcher.Search(0_eid);
            UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::ByStopCondition);

            // clang-format off
        std::unordered_map<TEdgeId, TWeight> expectedEdgeFinalDistances = {
            {0_eid, 0},
            {1_eid, 0},
            {2_eid, 0},
            {3_eid, 0},
            {4_eid, 7},
            {5_eid, 7},
            {6_eid, 9}, // this edge will cause a halt
        };
        std::vector<TEdgeId> expectedEdgeVisitOrder = {
          0_eid,
          1_eid,
          2_eid,
          3_eid,
          4_eid,
          5_eid,
          6_eid,
        };
            // clang-format on

            UNIT_ASSERT_EQUAL(actions.EdgeFinalDistances, expectedEdgeFinalDistances);
            UNIT_ASSERT_EQUAL(actions.EdgeVisitOrder, expectedEdgeVisitOrder);
        }
    }

    Y_UNIT_TEST(dijkstra_search_stop_by_path_length_in_meters) {
        for (auto with_edge_storage : std::vector<bool>{true, false}) {
            TGraph graph = BuildGraphForDijkstraFromWikipedia();
            if (with_edge_storage) {
                graph.BuildEdgeStorage(32);
            }

            TestSearchActions actions(false);
            TEdgeSearchSettings settings;
            settings.MaxPathLengthInMeters = 10.0;

            NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, actions, settings);
            const auto& searchStopReason = searcher.Search(0_eid);
            UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::ByPathGeolength);

            // clang-format off
        std::unordered_map<TEdgeId, TWeight> expectedEdgeFinalDistances = {
            {0_eid, 0},
            {1_eid, 0},
            {2_eid, 0},
            {3_eid, 0},
            {4_eid, 7},
            {5_eid, 7},
            {6_eid, 9},
            {7_eid, 9},
        };
        std::vector<TEdgeId> expectedEdgeVisitOrder = {
          0_eid,
          1_eid,
          2_eid,
          3_eid,
          4_eid,
          5_eid,
          6_eid,
          7_eid,
        };
            // clang-format on

            UNIT_ASSERT_EQUAL(actions.EdgeFinalDistances, expectedEdgeFinalDistances);
            UNIT_ASSERT_EQUAL(actions.EdgeVisitOrder, expectedEdgeVisitOrder);
        }
    }

    Y_UNIT_TEST(dijkstra_search_stop_by_max_discovered_edges) {
        for (auto with_edge_storage : std::vector<bool>{true, false}) {
            TGraph graph = BuildGraphForDijkstraFromWikipedia();
            if (with_edge_storage) {
                graph.BuildEdgeStorage(32);
            }

            TestSearchActions actions(false);
            TEdgeSearchSettings settings;
            settings.MaxVisitedEdges = 5;

            NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, actions, settings);
            searcher.SetIterationsCountPerStopCheck(1);
            const auto& searchStopReason = searcher.Search(0_eid);
            UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::ByStopCondition);

            // clang-format off
        std::unordered_map<TEdgeId, TWeight> expectedEdgeFinalDistances = {
            {0_eid, 0},
            {1_eid, 0},
            {2_eid, 0},
            {3_eid, 0},
            {4_eid, 7},
        };
        std::vector<TEdgeId> expectedEdgeVisitOrder = {
          0_eid,
          1_eid,
          2_eid,
          3_eid,
          4_eid,
        };
            // clang-format on

            UNIT_ASSERT_EQUAL(actions.EdgeFinalDistances, expectedEdgeFinalDistances);
            UNIT_ASSERT_EQUAL(actions.EdgeVisitOrder, expectedEdgeVisitOrder);
        }
    }

    Y_UNIT_TEST(dijkstra_search_stop_condition_always_true) {
        for (auto with_edge_storage : std::vector<bool>{true, false}) {
            TGraph graph = BuildGraphForDijkstraFromWikipedia();
            if (with_edge_storage) {
                graph.BuildEdgeStorage(32);
            }

            TestSearchActions actions(false);
            TEdgeSearchSettings settings;
            settings.MaxVisitedEdges = 0;

            NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, actions, settings);
            const auto& searchStopReason = searcher.Search(0_eid);
            UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::ByStopCondition);
            // just wanted to check that there would be no segfault
        }
    }

    Y_UNIT_TEST(dijkstra_bidirectional_search) {
        // Visualization: https://wiki.yandex-team.ru/taxi/backend/graph/libraries/libtaxigraph/docs/images/Test-na-start-s-neskolkix-reber/
        for (auto with_edge_storage : std::vector<bool>{true, false}) {
            TGraph graph = BuildGraphForMultipleStartEdges();
            if (with_edge_storage) {
                graph.BuildEdgeStorage(32);
            }

            {
                TestSearchActions actions(false);
                TEdgeSearchSettings settings;

                NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, actions, settings);
                const auto& searchStopReason = searcher.Search(TArrayRef<const TEdgeId>{14_eid, 15_eid});
                UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);

                // clang-format off
                std::unordered_map<TEdgeId, TWeight> expectedDiscoveredEdgeDistances = {
                    {0_eid, 4}, {1_eid, 4}, {2_eid, 3}, {3_eid, 3}, {4_eid, 3}, {5_eid, 4}, {6_eid, 4}, {7_eid, 4},
                    {8_eid, 2}, {9_eid, 2}, {10_eid, 2}, {11_eid, 2}, {12_eid, 1}, {13_eid, 1}, {14_eid, 2}, {15_eid, 2},
                };
                std::unordered_map<TEdgeId, TWeight> expectedEdgeFinalDistances = {
                    {0_eid, 4}, {1_eid, 4}, {2_eid, 3}, {3_eid, 3}, {4_eid, 3}, {5_eid, 4}, {6_eid, 4}, {7_eid, 4},
                    {8_eid, 2}, {9_eid, 2}, {10_eid, 2}, {11_eid, 2}, {12_eid, 1}, {13_eid, 1}, {14_eid, 0}, {15_eid, 0},
                };
                std::vector<TEdgeId> expectedEdgeVisitOrder = {
                14_eid, 15_eid, 12_eid, 13_eid, 10_eid, 11_eid, 8_eid, 9_eid, 2_eid, 3_eid, 4_eid, 5_eid, 6_eid, 7_eid, 0_eid, 1_eid,
                };

                // clang-format on

                /* for (auto [k,v]: actions.EdgeFinalDistances) Cout << k.value() << " " << v << Endl; Cout << "-" << Endl;
                for (auto [k,v]: actions.DiscoveredEdgeDistances) Cout << k.value() << " " << v << Endl; Cout << "-" << Endl;
                for (auto v: actions.EdgeVisitOrder) Cout << v.value() << Endl; Cout << "-" << Endl; */

                UNIT_ASSERT_EQUAL(actions.EdgeFinalDistances, expectedEdgeFinalDistances);
                UNIT_ASSERT_EQUAL(actions.DiscoveredEdgeDistances, expectedDiscoveredEdgeDistances);
                UNIT_ASSERT_EQUAL(actions.EdgeVisitOrder, expectedEdgeVisitOrder);
            }
            {
                TestSearchActions actions(true);
                TEdgeSearchSettings settings;
                settings.ReverseEdges = true;

                NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, actions, settings);
                const auto& searchStopReason = searcher.Search(TArrayRef<const TEdgeId>{5_eid, 8_eid});
                UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);

                // clang-format off
                std::unordered_map<TEdgeId, TWeight> expectedDiscoveredEdgeDistances = {
                    {0_eid, 2}, {1_eid, 1}, {2_eid, 2}, {3_eid, 1}, {4_eid, 1}, {5_eid, 2}, {6_eid, 2}, {7_eid, 3},
                    {8_eid, 2}, {9_eid, 2}, {10_eid, 1}, {11_eid, 3}, {12_eid, 1}, {13_eid, 3}, {14_eid, 3}, {15_eid, 2},
                };
                std::unordered_map<TEdgeId, TWeight> expectedEdgeFinalDistances = {
                    {0_eid, 2}, {1_eid, 1}, {2_eid, 2}, {3_eid, 1}, {4_eid, 1}, {5_eid, 0}, {6_eid, 2}, {7_eid, 3},
                    {8_eid, 0}, {9_eid, 2}, {10_eid, 1}, {11_eid, 3}, {12_eid, 1}, {13_eid, 3}, {14_eid, 3}, {15_eid, 2},
                };
                std::vector<TEdgeId> expectedEdgeVisitOrder = {
                    5_eid, 8_eid, 1_eid, 3_eid, 10_eid, 4_eid, 12_eid, 2_eid, 0_eid, 6_eid, 9_eid, 15_eid, 7_eid, 14_eid, 11_eid, 13_eid,
                };

                // clang-format on

                /* for possible debug needs in future */
                /*std::cout << "Edge visit order:";
                for (auto item: actions.EdgeVisitOrder) {
                    std::cout << item << ' ';
                }
                std::cout << std::endl << "DiscoveredEdgeDistances:";
                for (auto item: actions.DiscoveredEdgeDistances) {
                    std::cout << item.first << ' ' << item.second << ", ";
                }
                std::cout << std::endl << "EdgeFinalDistances";
                for (auto item: actions.EdgeFinalDistances) {
                    std::cout << item.first << ' ' << item.second << ", ";
                }
                std::cout << std::endl << "DiscoveredDistances";
                for (auto item: actions.DiscoveredDistances) {
                    std::cout << item.first << ' ' << item.second << ", ";
                }
                std::cout << std::endl << "FinalDistances";
                for (auto item: actions.FinalDistances) {
                    std::cout << item.first << ' ' << item.second << ", ";
                }*/

                UNIT_ASSERT_EQUAL(actions.EdgeFinalDistances, expectedEdgeFinalDistances);
                UNIT_ASSERT_EQUAL(actions.DiscoveredEdgeDistances, expectedDiscoveredEdgeDistances);
                UNIT_ASSERT_EQUAL(actions.EdgeVisitOrder, expectedEdgeVisitOrder);
            }
        }
    }

    Y_UNIT_TEST(dijkstra_straight_search_with_boom_barriers) {
        /*
         *  v0            v1              v2             v3                v4
         *  | >e0 <e3 (1) |  >e2 <e6 (1)  |  >e4 <e9 (2) |  >e7 <e11 (1)   |  >e10 <e12 (1)  |
         *  |<----------->|<-]----------->|<-[--------]->|<-------------[->|<--------------->|
         *  |             |               |              |                 |                 |
         *  |                             |              |                                   |
         *  |        >e1 (5)              |  >e5 (4)     |         >e8 (5)                   |
         *  |---------------------------->|------------->|---------------------------------->|
         *
         *  >eN means edge number N directed from left to right, <eM - edge number M from right to left.
         *  Each bidirectional edge are actually two unidirectional edges.
         *  Lengths of edges are given in brackets.
         *  Square brackets are boom barriers.
         *  Correct optimal route from v0 to v5 is: e0->e2->e5->e7->e10, length is 8.
         *  Route through e4 must be forbidden because of boom barriers.
        */
        for (auto with_edge_storage : std::vector<bool>{true, false}) {
            auto graph = BuildGraphForBoomBarriers(TReverse::No, TBoomBarriersTestCase::BlockTheWay);
            if (with_edge_storage) {
                graph.BuildEdgeStorage(32);
            }

            {
                TestSearchActions actions(false);
                TEdgeSearchSettings settings;

                NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, actions, settings);
                const auto& searchStopReason = searcher.Search(0_eid);
                UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);

                std::unordered_map<TVertexId, TWeight> expectedDiscoveredDistances = {
                    {0_vid, 2},
                    {1_vid, 1},
                    {2_vid, 2},
                    {3_vid, 4},
                    {4_vid, 7},
                    {5_vid, 9},
                };
                std::unordered_map<TVertexId, TWeight> expectedFinalDistances = {
                    {0_vid, 0},
                    {1_vid, 1},
                    {2_vid, 2},
                    {3_vid, 4},
                    {4_vid, 7},
                    {5_vid, 8},
                };

                UNIT_ASSERT_EQUAL(actions.DiscoveredDistances, expectedDiscoveredDistances);
                UNIT_ASSERT_EQUAL(actions.FinalDistances, expectedFinalDistances);
            }

            // But if we ignore boom barriers, the result would be different
            {
                TestSearchActions actions(false);
                TEdgeSearchSettings settings;
                settings.IgnoreBoomBarriers = true;

                NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, actions, settings);
                const auto& searchStopReason = searcher.Search(0_eid);
                UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);

                std::unordered_map<TVertexId, TWeight> expectedDiscoveredDistances = {
                    {0_vid, 2},
                    {1_vid, 1},
                    {2_vid, 2},
                    {3_vid, 4},
                    {4_vid, 5},
                    {5_vid, 9},
                };
                std::unordered_map<TVertexId, TWeight> expectedFinalDistances = {
                    {0_vid, 0},
                    {1_vid, 1},
                    {2_vid, 2},
                    {3_vid, 4},
                    {4_vid, 5},
                    {5_vid, 6},
                };

                UNIT_ASSERT_EQUAL(actions.DiscoveredDistances, expectedDiscoveredDistances);
                UNIT_ASSERT_EQUAL(actions.FinalDistances, expectedFinalDistances);
            }
        }
    }

    Y_UNIT_TEST(dijkstra_reverse_search_with_boom_barriers) {
        /*
         *  The same test as above, but all edges are reversed now
         *
         *  v0            v1              v2             v3                v4
         *  | >e0 <e1 (1) |  >e2 <e4 (1)  |  >e5 <e6 (2) |  >e8 <e9 (1)    |  >e10 <e12 (1)  |
         *  |<----------->|<-]----------->|<-[--------]->|<-------------[->|<--------------->|
         *  |             |               |              |                 |                 |
         *  |                             |              |                                   |
         *  |        <e3 (5)              |  <e7 (4)     |         <e11 (5)                  |
         *  |<----------------------------|<-------------|<----------------------------------|
         *
         *  >eN means edge number N directed from left to right, <eM - edge number M from right to left.
         *  Each bidirectional edge are actually two unidirectional edges.
         *  Lengths of edges are given in brackets.
         *  Square brackets are boom barriers.
         *  Correct optimal route from v0 to v5 has length 8.
        */
        for (auto with_edge_storage : std::vector<bool>{true, false}) {
            auto graph = BuildGraphForBoomBarriers(TReverse::Yes, TBoomBarriersTestCase::BlockTheWay);
            if (with_edge_storage) {
                graph.BuildEdgeStorage(32);
            }

            TestSearchActions actions(true);
            TEdgeSearchSettings settings;
            settings.ReverseEdges = true;

            NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, actions, settings);
            const auto& searchStopReason = searcher.Search(1_eid);
            UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);

            std::unordered_map<TVertexId, TWeight> expectedDiscoveredDistances = {
                {0_vid, 2},
                {1_vid, 1},
                {2_vid, 2},
                {3_vid, 4},
                {4_vid, 7},
                {5_vid, 9},
            };
            std::unordered_map<TVertexId, TWeight> expectedFinalDistances = {
                {0_vid, 0},
                {1_vid, 1},
                {2_vid, 2},
                {3_vid, 4},
                {4_vid, 7},
                {5_vid, 8},
            };

            UNIT_ASSERT_EQUAL(actions.DiscoveredDistances, expectedDiscoveredDistances);
            UNIT_ASSERT_EQUAL(actions.FinalDistances, expectedFinalDistances);
        }
    }

    Y_UNIT_TEST(dijkstra_reverse_path_through_boom_barriers) {
        /*
         *  In this case, the route through boom barriers is permissible and must be found.
         *
         *  v0            v1              v2             v3                v4
         *  | >e0 <e1 (1) |  >e2 <e4 (1)  |  >e5 <e6 (2) |  >e8 <e9 (1)    |  >e10 <e12 (1)  |
         *  |<----------->|<-]----------->|<----------]->|<-------------[->|<--------------->|
         *  |             |               |              |                 |                 |
         *  |                             |              |                                   |
         *  |        <e3 (5)              |  <e7 (4)     |         <e11 (5)                  |
         *  |<----------------------------|<-------------|<----------------------------------|
         *
         *  >eN means edge number N directed from left to right, <eM - edge number M from right to left.
         *  Each bidirectional edge are actually two unidirectional edges.
         *  Lengths of edges are given in brackets.
         *  Square brackets are boom barriers.
         *  Correct optimal route from v0 to v5 has length 6. We don't need to bypass any boom barriers.
        */
        for (auto with_edge_storage : std::vector<bool>{true, false}) {
            auto graph = BuildGraphForBoomBarriers(TReverse::Yes, TBoomBarriersTestCase::WayThrough);
            if (with_edge_storage) {
                graph.BuildEdgeStorage(32);
            }

            TestSearchActions actions(true);
            TEdgeSearchSettings settings;
            settings.ReverseEdges = true;

            NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, actions, settings);
            const auto& searchStopReason = searcher.Search(1_eid);
            UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);

            std::unordered_map<TVertexId, TWeight> expectedDiscoveredDistances = {
                {0_vid, 2},
                {1_vid, 1},
                {2_vid, 2},
                {3_vid, 4},
                {4_vid, 5},
                {5_vid, 9},
            };
            std::unordered_map<TVertexId, TWeight> expectedFinalDistances = {
                {0_vid, 0},
                {1_vid, 1},
                {2_vid, 2},
                {3_vid, 4},
                {4_vid, 5},
                {5_vid, 6},
            };

            UNIT_ASSERT_EQUAL(actions.DiscoveredDistances, expectedDiscoveredDistances);
            UNIT_ASSERT_EQUAL(actions.FinalDistances, expectedFinalDistances);
        }
    }

    Y_UNIT_TEST(dijkstra_way_around_boom_barriers) {
        /*
         *  v0            v1              v2             v3                v4
         *  | >e0 <e1 (1) |  >e2 <e4 (1)  |  >e5 <e6 (2) |  >e8 <e9 (1)    |  >e10 <e12 (1)  |
         *  |<----------->|<-[----------->|<----------]->|<-------------]->|<--------------->|
         *  |             |               |              |                 |                 |
         *  |                             |              |                                   |
         *  |        <e3 (5)              |  <e7 (4)     |         <e11 (5)                  |
         *  |<----------------------------|<-------------|<----------------------------------|
         *
         *  Specific case for the current implementation (for the legend, see tests above).
         *  By the current algorithm, the path e1<-e4<-e7<-e11 of length 11(+1 length of start edge e0)=12 must be found.
         *  That is because after first visiting e6 through e1<-e4 we mark this way as forbidden and don't consider it anymore.
         *  Another possible approach is to consider optimal path e3<-e6<-e9<-e12 of length 9(+1)=10, but currently it's not supported.
        */
        for (auto with_edge_storage : std::vector<bool>{true, false}) {
            auto graph = BuildGraphForBoomBarriers(TReverse::Yes, TBoomBarriersTestCase::WayAround);
            if (with_edge_storage) {
                graph.BuildEdgeStorage(32);
            }

            TestSearchActions actions(true);
            TEdgeSearchSettings settings;
            settings.ReverseEdges = true;

            NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, actions, settings);
            const auto& searchStopReason = searcher.Search(0_eid);
            UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);

            std::unordered_map<TVertexId, TWeight> expectedDiscoveredDistances = {
                {0_vid, 1},
                {1_vid, 2},
                {2_vid, 6},
                {3_vid, 5},
                {4_vid, 8},
                {5_vid, 12},
            };
            std::unordered_map<TVertexId, TWeight> expectedFinalDistances = {
                {0_vid, 1},
                {1_vid, 0},
                {2_vid, 3},
                {3_vid, 5},
                {4_vid, 8},
                {5_vid, 12},
            };

            UNIT_ASSERT_EQUAL(actions.DiscoveredDistances, expectedDiscoveredDistances);
            UNIT_ASSERT_EQUAL(actions.FinalDistances, expectedFinalDistances);
            UNIT_ASSERT_EQUAL(actions.PrecedingEdges[5_vid], 11_eid);
        }
    }

    // Test with standard stop condition
    Y_UNIT_TEST(dijkstra_search_wikipedia_example_reuse_searcher) {
        for (auto with_edge_storage : std::vector<bool>{true, false}) {
            TGraph graph = BuildGraphForDijkstraFromWikipedia();
            if (with_edge_storage) {
                graph.BuildEdgeStorage(32);
            }

            TestSearchActions actions(false);
            NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, actions);
            const auto& searchStopReason = searcher.Search(0_eid);
            UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);
            // clang-format off
            std::unordered_map<TVertexId, TWeight> expectedFinalDistances = {
                {0_vid, 0},
                {1_vid, 0},
                {2_vid, 7},
                {3_vid, 9},
                {4_vid, 20},
                {5_vid, 11},
                {6_vid, 20},
            };
            std::unordered_map<TEdgeId, TWeight> expectedEdgeFinalDistances = {
                {0_eid, 0},
                {1_eid, 0},
                {2_eid, 0},
                {3_eid, 0},
                {4_eid, 7},
                {5_eid, 7},
                {6_eid, 9},
                {7_eid, 9},
                {8_eid, 20},
                {9_eid, 11},
            };
            std::unordered_map<TVertexId, TId> expectedPrecedingEdges = {
                {1_vid, 0_eid},
                {2_vid, 1_eid},
                {3_vid, 2_eid},
                {4_vid, 6_eid},
                {5_vid, 7_eid},
                {6_vid, 9_eid},
            };
            std::vector<TEdgeId> expectedEdgeVisitOrder = {
                0_eid,
                1_eid,
                2_eid,
                3_eid,
                4_eid,
                5_eid,
                6_eid,
                7_eid,
                9_eid,
                8_eid
            };
            // clang-format on

            Cout << "FinalDistances: "; for (auto [k, v]: actions.FinalDistances) Cout << k.value() << " " << v << ", " << Endl;
            Cout << "EdgeFinalDistances: "; for (auto [k, v]: actions.EdgeFinalDistances) Cout << k.value() << " " << v << ", " << Endl;
            Cout << "PrecedingEdges: "; for (auto [k, v]: actions.PrecedingEdges) Cout << k.value() << " " << v.value() << ", " << Endl;
            Cout << "EdgeVisitOrder: "; for (auto v: actions.EdgeVisitOrder) Cout << v.value() << ", " << Endl;

            UNIT_ASSERT_EQUAL(actions.FinalDistances, expectedFinalDistances);
            UNIT_ASSERT_EQUAL(actions.EdgeFinalDistances, expectedEdgeFinalDistances);
            UNIT_ASSERT_EQUAL(actions.PrecedingEdges, expectedPrecedingEdges);
            UNIT_ASSERT_EQUAL(actions.EdgeVisitOrder, expectedEdgeVisitOrder);

            {
                const std::unordered_map<TVertexId, TWeight> expectedFinalDistances = {
                    {5_vid, 14},
                    {6_vid, 23},
                    {1_vid, 0},
                };
                const std::unordered_map<TEdgeId, TWeight> expectedEdgeFinalDistances = {
                    {9_eid, 14},
                    {3_eid, 0}};
                const std::unordered_map<TVertexId, TId> expectedPrecedingEdges = {
                    {5_vid, 3_eid},
                    {6_vid, 9_eid},
                };

                const std::vector<TEdgeId> expectedEdgeVisitOrder = {
                    3_eid,
                    9_eid,
                };
                searcher.Search(3_eid);

                Cout << "FinalDistances: "; for (auto [k, v]: actions.FinalDistances) Cout << k.value() << " " << v << ", " << Endl;
                Cout << "EdgeFinalDistances: "; for (auto [k, v]: actions.EdgeFinalDistances) Cout << k.value() << " " << v << ", " << Endl;
                Cout << "PrecedingEdges: "; for (auto [k, v]: actions.PrecedingEdges) Cout << k.value() << " " << v.value() << ", " << Endl;
                Cout << "EdgeVisitOrder: "; for (auto v: actions.EdgeVisitOrder) Cout << v.value() << ", " << Endl;

                UNIT_ASSERT_EQUAL(actions.FinalDistances, expectedFinalDistances);
                UNIT_ASSERT_EQUAL(actions.EdgeFinalDistances, expectedEdgeFinalDistances);
                UNIT_ASSERT_EQUAL(actions.PrecedingEdges, expectedPrecedingEdges);
                UNIT_ASSERT_EQUAL(actions.EdgeVisitOrder, expectedEdgeVisitOrder);
            }
        }
    }

    Y_UNIT_TEST(dijkstra_search_with_always_stop_search_actions) {
        struct AlwaysStopSearchActions: public IEdgeSearchActions {
            TEdgeDiscoverResult OnDiscoveredEdge(const TGraph&, const TEdge&,
                                                 TWeight, TEdgeId) final {
                return {false, 0};
            }

            TEdgeVisitResult OnVisitedEdge(const TGraph&, TEdgeId, TWeight, double, double) final {
                return {EEdgeVisitState::StopSearch, TWeight{}};
            }

            void InitBeforeSearch() final {
            }
        } actions;

        const TGraph graph = BuildGraphForDijkstraFromWikipedia();
        NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, actions);

        const auto& searchStopReason = searcher.Search(0_eid);
        UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::ByUser);
    }

    Y_UNIT_TEST(dijkstra_search_change_search_settings) {
        for (auto with_edge_storage : std::vector<bool>{true, false}) {
            TGraph graph = CreateRhombusGraph();
            if (with_edge_storage) {
                graph.BuildEdgeStorage(32);
            }
            TestSearchActions actions(false);
            NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, actions);

            {
                const auto& searchStopReason = searcher.Search(0_eid);
                UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);
                const auto& length_for_5_edge = searcher.GetPathLengthInMeters({5_eid, 0.});
                UNIT_ASSERT_OPTIONAL_DOUBLES_EQUAL(length_for_5_edge, std::optional<double>{3.}, 0.0001);
            }

            {
                TEdgeSearchSettings settings;
                settings.StopCondition = [](const TGraph&, TEdgeId, TWeight) {
                    return true;
                };
                searcher.SetSearchSettings(std::move(settings));

                const auto& searchStopReason = searcher.Search(0_eid);
                UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::ByStopCondition);
                const auto& length_for_5_edge = searcher.GetPathLengthInMeters({5_eid, 0.});
                UNIT_ASSERT_OPTIONAL_DOUBLES_EQUAL(length_for_5_edge, std::optional<double>{}, 0.0001);
            }
        }
    }

    Y_UNIT_TEST(dijkstra_search_rhombus_with_passes) {
        for (auto with_edge_storage : std::vector<bool>{true, false}) {
            TGraph graph{CreateRhombusGraphWithComplexPasses()};
            if (with_edge_storage) {
                graph.BuildEdgeStorage(32);
            }
            TestSearchActions actions(false);
            NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, actions);
            // Start not from pass.
            // We could get to edge 4, because we could't drive through passes.
            // Also that why we couldn't get to edge 6, but we could get into passes,
            // that's why edges 2 and 5 are visited.
            searcher.Search(0_eid);

            std::vector<TEdgeId> expectedEdgeVisitOrder = {
                0_eid,
                1_eid,
                2_eid,
                3_eid,
                5_eid};

            UNIT_ASSERT_EQUAL(actions.EdgeVisitOrder, expectedEdgeVisitOrder);
        }
    }

    Y_UNIT_TEST(dijkstra_search_rhombus_with_passes_start_from_pass) {
        for (auto with_edge_storage : std::vector<bool>{true, false}) {
            TGraph graph{CreateRhombusGraphWithComplexPasses()};
            if (with_edge_storage) {
                graph.BuildEdgeStorage(32);
            }
            TestSearchActions actions(false);
            NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, actions);
            // Start from edge in passes.
            // We go out from pass (edge 4) and could enter the pass (edge 5).
            // But we couldn't go through the pass (go to edge 6 after 5).
            searcher.Search(2_eid);

            std::vector<TEdgeId> expectedEdgeVisitOrder = {
                2_eid,
                4_eid,
                5_eid};

            UNIT_ASSERT_EQUAL(actions.EdgeVisitOrder, expectedEdgeVisitOrder);
        }
    }

    Y_UNIT_TEST(dijkstra_search_rhombus_with_passes_disabled_checking) {
        for (auto with_edge_storage : std::vector<bool>{true, false}) {
            TGraph graph{CreateRhombusGraphWithComplexPasses()};
            if (with_edge_storage) {
                graph.BuildEdgeStorage(32);
            }
            TestSearchActions actions(false);

            // Disable checking crossing the passes.
            NTaxi::NGraphSearch2::TEdgeSearchSettings settings;
            settings.DisableResidentialDriveThrough = false;

            NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, actions, settings);

            // From first edge gonna be all edges except 0, 2, 4.
            searcher.Search(1_eid);
            std::vector<TEdgeId> expectedEdgeVisitOrder = {
                1_eid,
                3_eid,
                5_eid,
                6_eid};
            UNIT_ASSERT_EQUAL(actions.EdgeVisitOrder, expectedEdgeVisitOrder);

            // From 0 edge gonna be all edges.
            searcher.Search(0_eid);
            expectedEdgeVisitOrder = {
                0_eid,
                1_eid,
                2_eid,
                3_eid,
                4_eid,
                5_eid,
                6_eid};
            UNIT_ASSERT_EQUAL(actions.EdgeVisitOrder, expectedEdgeVisitOrder);
        }
    }

    Y_UNIT_TEST(dijkstra_search_from_position_on_edge) {
        /*
         *         e0 (5)                   e5 (5)
         *  v0 -----------X-----> v1 <------------------- v2
         *  ^      80%      20%  ^  |                     ^
         *  |                    |  |                     |
         *  |             e3 (2) |  | e4 (2)              |
         *  |e1 (5)              |  |                     |e6 (5)
         *  |                    |  |                     |
         *  |                    |  |                     |
         *  |      e2 (5)        |  v       e7 (5)        |
         *  v3 <----------------- v4 -------------------> v5
         *
        */
        for (auto with_edge_storage : std::vector<bool>{true, false}) {
            auto graph = BuildGraphForStartFromPositionOnEdge();
            if (with_edge_storage) {
                graph.BuildEdgeStorage(32);
            }

            TestSearchActions actions(true);
            TEdgeSearchSettings settings;
            settings.ReverseEdges = true;

            NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, actions, settings);
            searcher.Search({0_eid, 0.8});

            // Check pathes correctness
            {
                std::vector<TEdgeId> actualPath = searcher.GetPath(0_eid);
                std::vector<TEdgeId> expectedPath = {0_eid};
                UNIT_ASSERT_EQUAL(expectedPath, actualPath);

                actualPath = searcher.GetPath(TPositionOnEdge{0_eid, 0.4});
                expectedPath = {0_eid};
                UNIT_ASSERT_EQUAL(expectedPath, actualPath);

                actualPath = searcher.GetPath(TPositionOnEdge{0_eid, 0.9});
                expectedPath = {0_eid, 3_eid, 5_eid, 1_eid, 0_eid};
                UNIT_ASSERT_EQUAL(expectedPath, actualPath);

                actualPath = searcher.GetPath(TPositionOnEdge{0_eid, 0.8});
                expectedPath = {0_eid};
                UNIT_ASSERT_EQUAL(expectedPath, actualPath);

                actualPath = searcher.GetPath(3_eid);
                expectedPath = {0_eid, 3_eid};
                UNIT_ASSERT_EQUAL(expectedPath, actualPath);

                actualPath = searcher.GetPath(TPositionOnEdge{3_eid, 0.0});
                expectedPath = {0_eid, 3_eid};
                UNIT_ASSERT_EQUAL(expectedPath, actualPath);

                actualPath = searcher.GetPath(TPositionOnEdge{3_eid, 1.0});
                expectedPath = {0_eid, 3_eid};
                UNIT_ASSERT_EQUAL(expectedPath, actualPath);
            }

            // Check path lengths
            {
                double actualLength = ToTestDouble(searcher.GetPathLengthInMeters(TPositionOnEdge{0_eid, 0.4}));
                double expectedLength = 2.0;
                UNIT_ASSERT_DOUBLES_EQUAL(expectedLength, actualLength, 0.0001);

                actualLength = ToTestDouble(searcher.GetPathLengthInMeters(TPositionOnEdge{0_eid, 0.9}));
                expectedLength = 16.5;
                UNIT_ASSERT_DOUBLES_EQUAL(expectedLength, actualLength, 0.0001);

                actualLength = ToTestDouble(searcher.GetPathLengthInMeters(TPositionOnEdge{0_eid, 0.8}));
                expectedLength = 0.0;
                UNIT_ASSERT_DOUBLES_EQUAL(expectedLength, actualLength, 0.0001);

                actualLength = ToTestDouble(searcher.GetPathLengthInMeters(TPositionOnEdge{3_eid, 0.0}));
                expectedLength = 9.0;
                UNIT_ASSERT_DOUBLES_EQUAL(expectedLength, actualLength, 0.0001);

                actualLength = ToTestDouble(searcher.GetPathLengthInMeters(TPositionOnEdge{3_eid, 1.0}));
                expectedLength = 4.0;
                UNIT_ASSERT_DOUBLES_EQUAL(expectedLength, actualLength, 0.0001);
            }

            const std::unordered_map<TVertexId, TWeight> expectedFinalDistances = {
                {0_vid, 4},
                {3_vid, 9},
                {4_vid, 14},
                {1_vid, 16},
                {2_vid, 21},
                {5_vid, 26},
            };
            const std::unordered_map<TEdgeId, TWeight> expectedEdgeFinalDistances = {
                {0_eid, 16},
                {1_eid, 14},
                {2_eid, 16},
                {3_eid, 4},
                {4_eid, 16},
                {5_eid, 9},
                {6_eid, 26},
                {7_eid, 21},
            };
            const std::unordered_map<TVertexId, TId> expectedPrecedingEdges = {
                {0_vid, 0_eid},
                {1_vid, 1_eid},
                {2_vid, 2_eid},
                {3_vid, 3_eid},
                {4_vid, 5_eid},
                {5_vid, 7_eid},
            };
            const std::vector<TEdgeId> expectedEdgeVisitOrder = {
                0_eid,
                3_eid,
                5_eid,
                1_eid,
                0_eid,
                2_eid,
                4_eid,
                7_eid,
                6_eid,
            };

            Cout << "FinalDistances: "; for (auto [k, v]: actions.FinalDistances) Cout << k.value() << " " << v << ", " << Endl;
            Cout << "EdgeFinalDistances: "; for (auto [k, v]: actions.EdgeFinalDistances) Cout << k.value() << " " << v << ", " << Endl;
            Cout << "PrecedingEdges: "; for (auto [k, v]: actions.PrecedingEdges) Cout << k.value() << " " << v.value() << ", " << Endl;
            Cout << "EdgeVisitOrder: "; for (auto v: actions.EdgeVisitOrder) Cout << v.value() << ", " << Endl;

            UNIT_ASSERT_EQUAL(actions.FinalDistances, expectedFinalDistances);
            UNIT_ASSERT_EQUAL(actions.EdgeFinalDistances, expectedEdgeFinalDistances);
            UNIT_ASSERT_EQUAL(actions.PrecedingEdges, expectedPrecedingEdges);
            UNIT_ASSERT_EQUAL(actions.EdgeVisitOrder, expectedEdgeVisitOrder);
        }
    }

    Y_UNIT_TEST(dijkstra_search_from_multiple_positions_on_edges) {
        /*
         *         e0 (5)             40%   e5 (5)  60%
         *  v0 -----------------> v1 <-------X----------- v2
         *  ^                    ^  |                     ^
         *  |                    |  | 50%                 |
         *  |             e3 (2) |  |                     |
         *  |e1 (5)              X  X e4 (2)              |e6 (5)
         *  |                    |  |                     |
         *  |                    |  | 50%                 |
         *  |      e2 (5)        |  v       e7 (5)        |
         *  v3 <----------------- v4 -------------------> v5
         *
         *  This time we start searching from the 0.5 of the 3th and 4th edges and from
         *  the 0.6 of the 5th edge simultaneously. Reverse edges option is false.
        */
        for (auto with_edge_storage : std::vector<bool>{true, false}) {
            auto graph = BuildGraphForStartFromPositionOnEdge();
            if (with_edge_storage) {
                graph.BuildEdgeStorage(32);
            }

            TestSearchActions actions(false);
            TEdgeSearchSettings settings;

            NTaxi::NGraphSearch2::TDijkstraEdgeSearcher searcher(graph, actions, settings);
            searcher.Search(TArrayRef<const TPositionOnEdge>{{3_eid, 0.5}, {4_eid, 0.5}, {5_eid, 0.6}});

            // Check paths correctness
            {
                std::vector<TEdgeId> actualPath = searcher.GetPath(0_eid);
                std::vector<TEdgeId> expectedPath = {3_eid, 0_eid};
                UNIT_ASSERT_EQUAL(expectedPath, actualPath);

                actualPath = searcher.GetPath(3_eid);
                expectedPath = {3_eid};
                UNIT_ASSERT_EQUAL(expectedPath, actualPath);

                actualPath = searcher.GetPath(TPositionOnEdge{3_eid, 0.25});
                expectedPath = {5_eid, 3_eid};
                UNIT_ASSERT_EQUAL(expectedPath, actualPath);

                actualPath = searcher.GetPath(TPositionOnEdge{5_eid, 0.8});
                expectedPath = {5_eid};
                UNIT_ASSERT_EQUAL(expectedPath, actualPath);

                actualPath = searcher.GetPath(TPositionOnEdge{5_eid, 0.2});
                expectedPath = {4_eid, 1_eid, 5_eid};
                UNIT_ASSERT_EQUAL(expectedPath, actualPath);
            }

            // Check paths lengths
            {
                double actualLength = ToTestDouble(searcher.GetPathLengthInMeters(TPositionOnEdge{0_eid, 0.4}));
                double expectedLength = 4.5;
                UNIT_ASSERT_DOUBLES_EQUAL(expectedLength, actualLength, 0.0001);

                actualLength = ToTestDouble(searcher.GetPathLengthInMeters(TPositionOnEdge{3_eid, 0.25}));
                expectedLength = 3.25;
                UNIT_ASSERT_DOUBLES_EQUAL(expectedLength, actualLength, 0.0001);

                actualLength = ToTestDouble(searcher.GetPathLengthInMeters(TPositionOnEdge{5_eid, 0.8}));
                expectedLength = 1.0;
                UNIT_ASSERT_DOUBLES_EQUAL(expectedLength, actualLength, 0.0001);

                actualLength = ToTestDouble(searcher.GetPathLengthInMeters(TPositionOnEdge{5_eid, 0.2}));
                expectedLength = 4.0;
                UNIT_ASSERT_DOUBLES_EQUAL(expectedLength, actualLength, 0.0001);
            }

            const std::unordered_map<TVertexId, TWeight> expectedFinalDistances = {
                {0_vid, 3},
                {1_vid, 1},
                {2_vid, 13},
                {3_vid, 2},
                {4_vid, 3},
                {5_vid, 8},
            };
            const std::unordered_map<TVertexId, TId> expectedPrecedingEdges = {
                {0_vid, 3_eid},
                {1_vid, 4_eid},
                {2_vid, 7_eid},
                {3_vid, 5_eid},
                {4_vid, 1_eid},
                {5_vid, 6_eid},
            };
            const std::vector<TEdgeId> expectedEdgeVisitOrder = {
                3_eid,
                4_eid,
                5_eid,
                1_eid,
                3_eid,
                0_eid,
                4_eid,
                5_eid,
                6_eid,
                7_eid,
                2_eid,
            };

            UNIT_ASSERT_EQUAL(actions.PrecedingEdges, expectedPrecedingEdges);
            UNIT_ASSERT_EQUAL(actions.EdgeVisitOrder, expectedEdgeVisitOrder);
            UNIT_ASSERT_EQUAL(actions.FinalDistances, expectedFinalDistances);
        }
    }
}
