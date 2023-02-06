#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <taxi/graph/libs/graph/graph_data_builder.h>
#include <taxi/graph/libs/search/dijkstra_searcher.h>

#include <iostream>

#include <taxi/graph/libs/graph-test/graph_test_data.h>

using NTaxi::NGraph2::TEdge;
using NTaxi::NGraph2::TEdgeData;
using NTaxi::NGraph2::TEdgeId;
using NTaxi::NGraph2::TGraph;
using NTaxi::NGraph2::TId;
using NTaxi::NGraph2::TPersistentEdgeId;
using NTaxi::NGraph2::TVertexId;
using NTaxi::NGraphSearch2::TSearchSettings;
using NTaxi::NGraphSearch2::TWeight;

using namespace NTaxi::NGraph2Literals;

namespace {
    struct TestSearchActions: public NTaxi::NGraphSearch2::ISearchActions {
        TestSearchActions(bool reverseEdges)
            : reverseEdges(reverseEdges)
        {
        }

        using TEdgeDiscoverResult = NTaxi::NGraphSearch2::TEdgeDiscoverResult;
        TEdgeDiscoverResult OnDiscoveredEdge(const TGraph& graph, const TEdge& discoveredEdge,
                                             const TWeight& currentDistance, const TEdge& precedingEdge) override {
            std::ignore = precedingEdge;

            const auto& edgeData = graph.GetEdgeData(discoveredEdge.Id);
            const auto& edgeWeight = static_cast<TWeight>(edgeData.Length / edgeData.Speed);

            const auto& discoveredVertexId = reverseEdges ? discoveredEdge.Source : discoveredEdge.Target;

            discovered_distances.insert({discoveredVertexId, currentDistance + edgeWeight});

            return {false, edgeWeight};
        }

        void OnPassedEdge(const TGraph& graph, const TEdge& edge, const TWeight& currentDistance) override {
            std::ignore = graph;

            const auto& vertexId = reverseEdges ? edge.Source : edge.Target;
            vertex_visit_order.push_back(vertexId);
            final_distances[vertexId] = currentDistance;
            preceding_edges[vertexId] = edge.Id;
        }

        void Clear() {
            discovered_distances.clear();
            final_distances.clear();
            preceding_edges.clear();
            vertex_visit_order.clear();
        }

        bool reverseEdges;
        std::unordered_map<TVertexId, TWeight> discovered_distances;
        std::unordered_map<TVertexId, TWeight> final_distances;
        std::unordered_map<TVertexId, TId> preceding_edges;
        std::vector<TVertexId> vertex_visit_order;
    };
}

class TGraphDijkstraSearchFixture: public ::NUnitTest::TBaseTestCase, public NTaxi::NGraph2::TGraphTestData {
};

Y_UNIT_TEST_SUITE_F(graph_dijkstra_search, TGraphDijkstraSearchFixture) {
    Y_UNIT_TEST(dijkstra_search_rhombus) {
        TGraph graph{CreateRhombusGraph()};

        TestSearchActions actions(false);
        NTaxi::NGraphSearch2::TDijkstraSearcher searcher(graph, actions);
        searcher.Search(0_eid);
        // clang-format off
        std::unordered_map<TVertexId, TWeight> expected_discovered_distances = {
            {2_vid, 1},
            {3_vid, 2},
            {4_vid, 4},
            {5_vid, 4},
        };
        std::unordered_map<TVertexId, TWeight> expected_final_distances = {
            {1_vid, 0},
            {2_vid, 1},
            {3_vid, 2},
            {4_vid, 3},
            {5_vid, 4},
        };
        std::unordered_map<TVertexId, TId> expected_preceding_edges = {
            {1_vid, 0_eid},
            {2_vid, 1_eid},
            {3_vid, 2_eid},
            {4_vid, 4_eid},
            {5_vid, 5_eid},
        };
        // clang-format on
        std::vector<TVertexId> expected_vertex_visit_order = {1_vid, 2_vid, 3_vid, 4_vid, 5_vid};

        UNIT_ASSERT_EQUAL(actions.discovered_distances, expected_discovered_distances);
        UNIT_ASSERT_EQUAL(actions.final_distances, expected_final_distances);
        UNIT_ASSERT_EQUAL(actions.preceding_edges, expected_preceding_edges);
        UNIT_ASSERT_EQUAL(actions.vertex_visit_order, expected_vertex_visit_order);

        std::vector<TId> path_5 = searcher.GetPath(5_eid);
        std::vector<TId> expected_path_5 = {0_eid, 2_eid, 4_eid, 5_eid};
        UNIT_ASSERT_EQUAL(path_5, expected_path_5);

        std::vector<TId> path_3 = searcher.GetPath(3_eid);
        std::vector<TId> expected_path_3 = {0_eid, 1_eid, 3_eid};
        UNIT_ASSERT_EQUAL(path_3, expected_path_3);

        std::vector<TId> path_0 = searcher.GetPath(0_eid);
        std::vector<TId> expected_path_0 = {};
        UNIT_ASSERT_EQUAL(path_0, expected_path_0);
    }

    Y_UNIT_TEST(dijkstra_search_reversed_edges) {
        TGraph graph{CreateRhombusGraphReversed()};

        TestSearchActions actions(true);
        TSearchSettings settings;
        settings.ReverseEdges = true;

        NTaxi::NGraphSearch2::TDijkstraSearcher searcher(graph, actions, settings);
        searcher.Search(0_eid);
        // clang-format off
        std::unordered_map<TVertexId, TWeight> expected_discovered_distances = {
            {1_vid, 1},
            {2_vid, 2},
            {3_vid, 4},
            {4_vid, 4},
        };
        std::unordered_map<TVertexId, TWeight> expected_final_distances = {
            {0_vid, 0},
            {1_vid, 1},
            {2_vid, 2},
            {3_vid, 3},
            {4_vid, 4},
        };
        std::unordered_map<TVertexId, TId> expected_preceding_edges = {
            {0_vid, 0_eid},
            {1_vid, 1_eid},
            {2_vid, 2_eid},
            {3_vid, 4_eid},
            {4_vid, 5_eid},
        };
        // clang-format on
        std::vector<TVertexId> expected_vertex_visit_order = {0_vid, 1_vid, 2_vid, 3_vid, 4_vid};

        UNIT_ASSERT_EQUAL(actions.discovered_distances, expected_discovered_distances);
        UNIT_ASSERT_EQUAL(actions.final_distances, expected_final_distances);
        UNIT_ASSERT_EQUAL(actions.preceding_edges, expected_preceding_edges);
        UNIT_ASSERT_EQUAL(actions.vertex_visit_order, expected_vertex_visit_order);

        std::vector<TId> path_5 = searcher.GetPath(5_eid);
        std::vector<TId> expected_path_5 = {0_eid, 2_eid, 4_eid, 5_eid};
        UNIT_ASSERT_EQUAL(path_5, expected_path_5);

        std::vector<TId> path_3 = searcher.GetPath(3_eid);
        std::vector<TId> expected_path_3 = {0_eid, 1_eid, 3_eid};
        UNIT_ASSERT_EQUAL(path_3, expected_path_3);

        std::vector<TId> path_0 = searcher.GetPath(0_eid);
        std::vector<TId> expected_path_0 = {};
        UNIT_ASSERT_EQUAL(path_0, expected_path_0);
    }

    // Test with standard stop condition
    Y_UNIT_TEST(dijkstra_search_wikipedia_example) {
        const TGraph graph = BuildGraphForDijkstraFromWikipedia();

        TestSearchActions actions(false);
        NTaxi::NGraphSearch2::TDijkstraSearcher searcher(graph, actions);
        searcher.Search(0_eid);
        // clang-format off
        std::unordered_map<TVertexId, TWeight> expected_discovered_distances = {
            {2_vid, 7},
            {3_vid, 9},
            {4_vid, 22},
            {5_vid, 14},
            {6_vid, 20},
        };
        std::unordered_map<TVertexId, TWeight> expected_final_distances = {
            {1_vid, 0},
            {2_vid, 7},
            {3_vid, 9},
            {4_vid, 20},
            {5_vid, 11},
            {6_vid, 20},
        };
        std::unordered_map<TVertexId, TId> expected_preceding_edges = {
            {1_vid, 0_eid},
            {2_vid, 1_eid},
            {3_vid, 2_eid},
            {4_vid, 6_eid},
            {5_vid, 7_eid},
            {6_vid, 9_eid},
        };
        // clang-format on
        std::vector<TVertexId> expected_vertex_visit_order = {1_vid, 2_vid, 3_vid, 5_vid, 4_vid, 6_vid};

        UNIT_ASSERT_EQUAL(actions.discovered_distances, expected_discovered_distances);
        UNIT_ASSERT_EQUAL(actions.final_distances, expected_final_distances);
        UNIT_ASSERT_EQUAL(actions.preceding_edges, expected_preceding_edges);
        UNIT_ASSERT_EQUAL(actions.vertex_visit_order, expected_vertex_visit_order);

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

    Y_UNIT_TEST(dijkstra_search_stop_by_distance) {
        const TGraph graph = BuildGraphForDijkstraFromWikipedia();

        TestSearchActions actions(false);
        TSearchSettings settings;
        settings.StopCondition = [](const TGraph&, TVertexId, TWeight currentDistance) {
            return currentDistance >= 10;
        };

        NTaxi::NGraphSearch2::TDijkstraSearcher searcher(graph, actions, settings);
        searcher.Search(0_eid);

        // clang-format off
        std::unordered_map<TVertexId, TWeight> expected_discovered_distances = {
            {2_vid, 7},
            {3_vid, 9},
            {4_vid, 22},
            {5_vid, 14},
        };
        std::unordered_map<TVertexId, TWeight> expected_final_distances = {
            {1_vid, 0},
            {2_vid, 7},
            {3_vid, 9},
        };
        std::unordered_map<TVertexId, TId> expected_preceding_edges = {
            {1_vid, 0_eid},
            {2_vid, 1_eid},
            {3_vid, 2_eid},
        };
        // clang-format on
        std::vector<TVertexId> expected_vertex_visit_order = {1_vid, 2_vid, 3_vid};

        UNIT_ASSERT_EQUAL(actions.discovered_distances, expected_discovered_distances);
        UNIT_ASSERT_EQUAL(actions.final_distances, expected_final_distances);
        UNIT_ASSERT_EQUAL(actions.preceding_edges, expected_preceding_edges);
        UNIT_ASSERT_EQUAL(actions.vertex_visit_order, expected_vertex_visit_order);
    }

    Y_UNIT_TEST(dijkstra_search_stop_by_max_discovered_edges) {
        const TGraph graph = BuildGraphForDijkstraFromWikipedia();

        TestSearchActions actions(false);
        TSearchSettings settings;
        settings.MaxDiscoveredEdges = 5;

        NTaxi::NGraphSearch2::TDijkstraSearcher searcher(graph, actions, settings);
        searcher.Search(0_eid);

        // clang-format off
        std::unordered_map<TVertexId, TWeight> expected_discovered_distances = {
            {2_vid, 7},
            {3_vid, 9},
            {4_vid, 22},
            {5_vid, 14},
        };
        std::unordered_map<TVertexId, TWeight> expected_final_distances = {
            {1_vid, 0},
            {2_vid, 7},
        };
        std::unordered_map<TVertexId, TId> expected_preceding_edges = {
            {1_vid, 0_eid},
            {2_vid, 1_eid},
        };
        // clang-format on
        std::vector<TVertexId> expected_vertex_visit_order = {1_vid, 2_vid};

        UNIT_ASSERT_EQUAL(actions.discovered_distances, expected_discovered_distances);
        UNIT_ASSERT_EQUAL(actions.final_distances, expected_final_distances);
        UNIT_ASSERT_EQUAL(actions.preceding_edges, expected_preceding_edges);
        UNIT_ASSERT_EQUAL(actions.vertex_visit_order, expected_vertex_visit_order);
    }

    Y_UNIT_TEST(dijkstra_search_stop_condition_always_true) {
        const TGraph graph = BuildGraphForDijkstraFromWikipedia();

        TestSearchActions actions(false);
        TSearchSettings settings;
        settings.MaxDiscoveredEdges = 0;

        NTaxi::NGraphSearch2::TDijkstraSearcher searcher(graph, actions, settings);
        searcher.Search(0_eid);

        std::unordered_map<TVertexId, TWeight> expected_discovered_distances = {};
        std::unordered_map<TVertexId, TWeight> expected_final_distances = {};
        std::unordered_map<TVertexId, TId> expected_preceding_edges = {};
        std::vector<TVertexId> expected_vertex_visit_order = {};

        UNIT_ASSERT_EQUAL(actions.discovered_distances, expected_discovered_distances);
        UNIT_ASSERT_EQUAL(actions.final_distances, expected_final_distances);
        UNIT_ASSERT_EQUAL(actions.preceding_edges, expected_preceding_edges);
        UNIT_ASSERT_EQUAL(actions.vertex_visit_order, expected_vertex_visit_order);
    }

    // Search again from differenr edge
    Y_UNIT_TEST(dijkstra_search_reuse_searcher) {
        const TGraph graph = BuildGraphForDijkstraFromWikipedia();

        TestSearchActions actions(false);
        NTaxi::NGraphSearch2::TDijkstraSearcher searcher(graph, actions);
        searcher.Search(0_eid);
        // clang-format off
        std::unordered_map<TVertexId, TWeight> expected_discovered_distances = {
            {2_vid, 7},
            {3_vid, 9},
            {4_vid, 22},
            {5_vid, 14},
            {6_vid, 20},
        };
        std::unordered_map<TVertexId, TWeight> expected_final_distances = {
            {1_vid, 0},
            {2_vid, 7},
            {3_vid, 9},
            {4_vid, 20},
            {5_vid, 11},
            {6_vid, 20},
        };
        std::unordered_map<TVertexId, TId> expected_preceding_edges = {
            {1_vid, 0_eid},
            {2_vid, 1_eid},
            {3_vid, 2_eid},
            {4_vid, 6_eid},
            {5_vid, 7_eid},
            {6_vid, 9_eid},
        };
        // clang-format on
        std::vector<TVertexId> expected_vertex_visit_order = {1_vid, 2_vid, 3_vid, 5_vid, 4_vid, 6_vid};

        UNIT_ASSERT_EQUAL(actions.discovered_distances, expected_discovered_distances);
        UNIT_ASSERT_EQUAL(actions.final_distances, expected_final_distances);
        UNIT_ASSERT_EQUAL(actions.preceding_edges, expected_preceding_edges);
        UNIT_ASSERT_EQUAL(actions.vertex_visit_order, expected_vertex_visit_order);

        {
            const std::unordered_map<TVertexId, TWeight> expected_discovered_distances = {
                {6_vid, 9},
            };
            const std::unordered_map<TVertexId, TWeight> expected_final_distances = {
                {6_vid, 9},
                {5_vid, 0},
            };
            const std::unordered_map<TVertexId, TId> expected_preceding_edges = {
                {6_vid, 9_eid},
                {5_vid, 3_eid},
            };
            const std::vector<TVertexId> expected_vertex_visit_order = {
                5_vid,
                6_vid};
            actions.Clear();
            searcher.Search(3_eid);

            UNIT_ASSERT_EQUAL(actions.discovered_distances, expected_discovered_distances);
            UNIT_ASSERT_EQUAL(actions.final_distances, expected_final_distances);
            UNIT_ASSERT_EQUAL(actions.preceding_edges, expected_preceding_edges);
            UNIT_ASSERT_EQUAL(actions.vertex_visit_order, expected_vertex_visit_order);
        }
    }
}
