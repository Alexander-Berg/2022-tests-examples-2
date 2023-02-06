#pragma once

#include <library/cpp/testing/unittest/env.h>

#include <taxi/graph/libs/graph/graph.h>
#include <taxi/graph/libs/graph/persistent_index.h>
#include <taxi/graph/libs/graph/jams.h>
#include <taxi/graph/libs/graph/graph_data_builder.h>

#include <taxi/graph/libs/graph/types.h>
#include <unordered_map>

namespace NTaxi::NGraph2 {
    class TGraphTestData {
    public:
        enum TReverse {
            Yes,
            No
        };

        enum TBoomBarriersTestCase {
            BlockTheWay,
            WayThrough,
            WayAround
        };

        enum class TWithEdgeStorage {
          Yes,
          No
        };

        struct TEdgeDesc {
            ui32 source = UNDEFINED.value();
            ui32 target = UNDEFINED.value();
            double length = 1.0;
            ::NTaxi::NGraph::TEdgeCategory category = ::NTaxi::NGraph::TEdgeCategory::EC_ROADS;
            double speed = 1.0;
            bool isTollRoad = false;
            TEdgeAccess access = TEdgeAccess::EA_AUTOMOBILE;
            bool isPavedRoad = true;
            bool isInPoorCondition = false;
        };

        struct TTurnInfoDesc {
            ui32 source = UNDEFINED.value();
            ui32 target = UNDEFINED.value();
            bool accessPass = false;
            bool forbidden = false;
            bool countryBorder = false;
        };

        TGraph CreateGraph(size_t num_vertices, const TVector<TEdgeDesc>& edges) {
            auto builder = std::make_unique<TRoadGraphDataBuilder>(num_vertices, edges.size(), 0);
            for (size_t i = 0; i < num_vertices; ++i) {
                double coord = i;
                builder->SetVertexGeometry(maps::road_graph::VertexId(i), {coord, coord});
            }

            for (ui32 i = 0; i < edges.size(); ++i) {
                const auto& edge_desc = edges[i];

                const auto& id = i;
                const auto& source = edge_desc.source;
                const auto& target = edge_desc.target;

                NTaxi::NGraph2::TPolyline fake_polyline;
                double coord1 = source;
                double coord2 = target;
                fake_polyline.AddPoint({coord1, coord1});
                fake_polyline.AddPoint({coord2, coord2});

                auto data = TEdgeData{edge_desc.speed, edge_desc.length};
                data.Category = edge_desc.category;
                data.IsTollRoad = edge_desc.isTollRoad;
                data.Access = edge_desc.access;
                data.IsPavedRoad = edge_desc.isPavedRoad;
                data.IsInPoorCondition = edge_desc.isInPoorCondition;
                builder->SetEdge(TEdge(TEdgeId(id), TVertexId(source), TVertexId(target)), true);
                builder->SetEdgeData(TEdgeId(id), data, fake_polyline);
            }

            builder->Build();
            auto ret = TGraph(std::move(builder));
            if (enableEdgeStorage)
                ret.BuildEdgeStorage(ThreadCount);

            return ret;
        };

        /// Generated EdgeIds may not match to order in edges. edgeMapping
        /// provided to find correct edgeIds
        /// \param vertices array of vertices coords
        /// \param edges array of edges descriptions (from, to, speed, length e.t.c)
        /// \param turninfos
        /// \param edgeMapping mapping of input edge ids to resulting edgeIds
        TGraph CreateRoadGraph(const TVector<TPoint>& vertices,
                               const TVector<TEdgeDesc>& edges,
                               const TVector<TTurnInfoDesc>& turnInfos,
                               std::unordered_map<ui32, TEdgeId>* edgeMappings = nullptr);

        ///    vertices      edges
        ///       0            x
        ///       |            |
        ///       |            |0
        ///       1            x
        ///      / \         1/ \2
        ///     /   \        /   \
        ///    2     3      x     x
        ///     \   /        \   /
        ///      \ /         3\ /4 (len=1)
        ///       4            x
        ///       |            |
        ///       |            |5 (len=1)
        ///       5            x
        TGraph CreateRhombusGraph() {
            return CreateGraph(6, {
                                      {0, 1, 0},
                                      {1, 2, 1},
                                      {1, 3, 2},
                                      {2, 4, 3},
                                      {3, 4, 1},
                                      {4, 5, 1},
                                  }
                               );
        };
        TGraph CreateRhombusGraphReversed() {
            return CreateGraph(6, {
                                      {0, 5, 0},
                                      {1, 0, 1},
                                      {2, 0, 2},
                                      {3, 1, 3},
                                      {3, 2, 1},
                                      {4, 3, 1},
                                  }
                               );
        };

        /// Same as CreateRhombusGraph but some edges are toll roads
        ///  vertices      edges
        ///       0            x
        ///       |            |
        ///       |            |0
        ///       1            x
        ///      / \         1/ \2
        ///     /   \        /   \
        ///    2     3      x     x
        ///     \   /        \   /
        ///      \ /         3\ /4<-toll road!
        ///       4            x
        ///       |            |
        ///       |            |5
        ///       5            x
        TGraph CreateRhombusGraphWithTollRoad() {
            return CreateGraph(6, {
                                      {0, 1, 0},
                                      {1, 2, 1},
                                      {1, 3, 2},
                                      {2, 4, 3},
                                      {3, 4, 1, ::NTaxi::NGraph::TEdgeCategory::EC_ROADS, 1.0, true},
                                      {4, 5, 1},
                                  }
                               );
        };

        ///  vertices      edges
        ///       0            x
        ///       |            |
        ///       |            |0
        ///       1            x
        ///       |            |
        ///       |            |1
        ///       2            x
        ///       |            |
        ///       |            |2<-toll road
        ///       3            x
        ///       |            |
        ///       |            |4
        ///       4            x
        TGraph CreateGraphWithTollRoad() {
            auto graph = CreateGraph(5, {
                                      {0, 1, 1},
                                      {1, 2, 1},
                                      {2, 3, 1, ::NTaxi::NGraph::TEdgeCategory::EC_ROADS, 1.0, true},
                                      {3, 4, 1},
                                  }
                               );
            graph.BuildEdgeStorage(ThreadCount);
            return graph;
        };

        ///  vertices      edges
        ///       0            x
        ///       |            |
        ///       |            |0<-toll road
        ///       1            x
        ///       |            |
        ///       |            |1<-toll road
        ///       2            x
        ///       |            |
        ///       |            |2
        ///       3            x
        ///       |            |
        ///       |            |4
        ///       4            x
        TGraph CreateGraphWithTollRoads() {
            auto graph = CreateGraph(5, {
                                      {0, 1, 1},
                                      {1, 2, 1},
                                      {2, 3, 1, ::NTaxi::NGraph::TEdgeCategory::EC_ROADS, 1.0, true},
                                      {3, 4, 1, ::NTaxi::NGraph::TEdgeCategory::EC_ROADS, 1.0, true},
                                  }
                               );
            graph.BuildEdgeStorage(ThreadCount);
            return graph;
        };

        /// Same as CreateRhombusGraph but with some edges with EC_PASSES
        ///    vertices      edges
        ///       0            x
        ///       |            |  pass
        ///       |            |0
        ///       1            x
        ///      / \         1/ \2 pass
        ///     /   \        /   \
        ///    2     3      x     x
        ///     \   /        \   /
        ///      \ /    pass 3\ /4
        ///       4            x
        ///       |            |
        ///       |            |5 pass
        ///       5            x
        TGraph CreateRhombusGraphWithPasses() {
            return CreateGraph(6, {
                                      {0, 1, 0, TEdgeCategory::EC_PASSES},
                                      {1, 2, 1},
                                      {1, 3, 2, TEdgeCategory::EC_PASSES},
                                      {2, 4, 3, TEdgeCategory::EC_PASSES},
                                      {3, 4, 1},
                                      {4, 5, 1, TEdgeCategory::EC_PASSES},
                                  }
                               );
        };

        /// Same as CreateRhombusGraph but with field road behind passes
        ///    vertices      edges
        ///       0            x
        ///       |            |  
        ///       |            |0
        ///       1            x
        ///      / \         1/ \2
        ///     /   \        /   \
        ///    2     3      x     x
        ///     \   /        \   /
        ///      \ /    pass 3\ /4 pass
        ///       4            x
        ///       |            |
        ///       |            |5 field road
        ///       5            x
        TGraph CreateRhombusGraphWithFieldRoad() {
            auto graph = CreateGraph(6, {
                                      {0, 1, 0},
                                      {1, 2, 1},
                                      {1, 3, 2},
                                      {2, 4, 3, TEdgeCategory::EC_PASSES},
                                      {3, 4, 1, TEdgeCategory::EC_PASSES},
                                      {4, 5, 1, TEdgeCategory::EC_FIELD_ROADS},
                                  }
                               );
            graph.BuildEdgeStorage(ThreadCount);
            return graph;
        };

        /// Graph for testing route through a field road with yard near it
        ///
        ///        e0         e1
        ///  0---------->1---------->9     
        ///              |
        ///        field | e2    6
        ///             \|/ e6  / \e8
        ///              2<----5   7
        ///              | pass \ /e9
        ///     field e3 |       8
        ///             \|/
        ///  3---------->4---------->10
        ///      e4           e5
        ///
        TGraph CreateGraphWithFieldBetweenStreets() {
            auto graph = CreateGraph(11, {
                                      {0, 1, 1}, // e0
                                      {1, 9, 1}, // e1
                                      {1, 2, 1, TEdgeCategory::EC_FIELD_ROADS}, // e2
                                      {2, 4, 1, TEdgeCategory::EC_FIELD_ROADS}, // e3
                                      {3, 4, 1}, // e4
                                      {4, 10, 1}, // e5
                                      {5, 2, 1, TEdgeCategory::EC_PASSES}, // e6
                                      {5, 6, 1, TEdgeCategory::EC_PASSES}, // e7
                                      {6, 7, 1, TEdgeCategory::EC_PASSES}, // e8
                                      {7, 8, 1, TEdgeCategory::EC_PASSES}, // e9
                                      {8, 5, 1, TEdgeCategory::EC_PASSES}, // e10
                                    }
                               );
            graph.BuildEdgeStorage(ThreadCount);
            return graph;
        };

        /// Another graph for testing route through a field road
        ///
        ///                    5
        ///                    |
        ///                    |e5
        ///                    |
        ///    pass     field \|/ field    pass
        ///  0------->1------->2------->3-------->4------>6
        ///     e0       e1        e2       e3       e4
        ///
        TGraph CreateGraphWithFieldBetweenYards() {
            auto graph = CreateGraph(7, {
                                      {0, 1, 1, TEdgeCategory::EC_PASSES}, // e0
                                      {1, 2, 1, TEdgeCategory::EC_FIELD_ROADS}, // e1
                                      {2, 3, 1, TEdgeCategory::EC_FIELD_ROADS}, // e2
                                      {3, 4, 1, TEdgeCategory::EC_PASSES}, // e3
                                      {4, 6, 1}, // e4
                                      {5, 2, 1}, // e5
                                    }
                               );
            graph.BuildEdgeStorage(ThreadCount);
            return graph;
        };

        ///
        ///            non-paved poor cond
        ///  0------->1------->2------->3-------->4------>5
        ///     e0       e1        e2       e3       e4
        ///
        TGraph CreateGraphWithNonPavedRoads() {
            auto graph = CreateGraph(6, {
                                      {0, 1, 1}, // e0
                                      {1, 2, 1, TEdgeCategory::EC_ROADS, 1.0, false, TEdgeAccess::EA_AUTOMOBILE, false, false}, // e1
                                      {2, 3, 1, TEdgeCategory::EC_ROADS, 1.0, false, TEdgeAccess::EA_AUTOMOBILE, true, true}, // e2
                                      {3, 4, 1}, // e3
                                      {4, 5, 1}, // e4
                                    }
                               );
            graph.BuildEdgeStorage(ThreadCount);
            return graph;
        };

        ///           non-paved poor cond
        ///     pass     pass     pass     pass
        ///  0------->1------->2------->3-------->4------>5
        ///     e0       e1        e2       e3       e4
        ///
        TGraph CreateGraphWithNonPavedRoadsInsideYard() {
            auto graph = CreateGraph(6, {
                                      {0, 1, 1, TEdgeCategory::EC_PASSES}, // e0
                                      {1, 2, 1, TEdgeCategory::EC_PASSES, 1.0, false, TEdgeAccess::EA_AUTOMOBILE, false, false}, // e1
                                      {2, 3, 1, TEdgeCategory::EC_PASSES, 1.0, false, TEdgeAccess::EA_AUTOMOBILE, true, true}, // e2
                                      {3, 4, 1, TEdgeCategory::EC_PASSES}, // e3
                                      {4, 5, 1}, // e4
                                    }
                               );
            graph.BuildEdgeStorage(ThreadCount);
            return graph;
        };

        ///    vertices      edges
        ///       0            x
        ///       |            |
        ///       |            |0
        ///       1            x
        ///      / \         1/ \2 pass
        ///     /   \        /   \
        ///    2     3      x     x
        ///     \   /        \   /
        ///      \ /         3\ /4
        ///       4            x
        ///       |            |  pass
        ///       |            |5
        ///       5            x
        ///       |            |
        ///       |            |6
        ///       6            x
        TGraph CreateRhombusGraphWithComplexPasses() {
            return CreateGraph(7,
                               {{0, 1, 0},
                                {1, 2, 1},
                                {1, 3, 1, TEdgeCategory::EC_PASSES},
                                {2, 4, 3},
                                {3, 4, 1},
                                {4, 5, 1, TEdgeCategory::EC_PASSES},
                                {5, 6, 1}}
                               );
        };

        /// Same as CreateRhombusGraph but some edges aren't passable for taxi
        ///    vertices      edges
        ///       0            x
        ///       |            |
        ///       |            |0
        ///       1            x
        ///      / \         1/  2           (edges 2, 3 are not passable)
        ///     /   \        /    
        ///    2     3      x     x
        ///     \   /            /
        ///      \ /         3  /4
        ///       4            x
        ///       |            |
        ///       |            |5
        ///       5            x
        TGraph CreateRhombusGraphNotPassable() {
            return CreateGraph(6, {
                                      {0, 1, 0},
                                      {1, 2, 1},
                                      {1, 3, 2, TEdgeCategory::EC_ROADS, 1.0, false, TEdgeAccess::EA_BICYCLE},
                                      {2, 4, 3, TEdgeCategory::EC_ROADS, 1.0, false, TEdgeAccess::EA_PEDESTRIAN},
                                      {3, 4, 1},
                                      {4, 5, 1},
                                  }
                               );
        };
        
        ///    vertices      edges
        ///       0            x
        ///       |            |
        ///       |            |0
        ///       1            x
        ///      / \         1/ \2
        ///     /   \        /   \
        ///    2     3      x     x
        ///     \   /        \   /
        ///      \ /         3\ /4
        ///       4            x
        ///       |            |
        ///       |            |5
        ///       5            x
        TGraph CreateGiantRhombusGraph() {
            return CreateGraph(6, {
                                      {0, 1, 1000},
                                      {1, 2, 1000},
                                      {1, 3, 2000},
                                      {2, 4, 3000},
                                      {3, 4, 1000},
                                      {4, 5, 1000},
                                  }
                               );
        };
        TGraph CreateGiantRhombusGraphReversed() {
            return CreateGraph(6, {
                                      {0, 5, 1000},
                                      {1, 0, 1000},
                                      {2, 0, 2000},
                                      {3, 1, 3000},
                                      {3, 2, 1000},
                                      {4, 3, 1000},
                                  }
                               );
        };

        ///    vertices      edges
        ///       0            x
        ///       |            |
        ///       |            |0
        ///       1            x
        ///      / \         1/ \2
        ///     /   \        /   \
        ///    2     3      x     x
        ///     \   /        \   /
        ///      \ /         3\ /4
        ///       4            x
        ///       |            |
        ///       |            |5
        ///       5            x
        TGraph CreateRhombusRoadGraph(
            const TVector<TTurnInfoDesc>& turnInfos = {},
            std::unordered_map<ui32, TId>* mapping = nullptr) {
            const TVector<TPoint> vertices = {
                {0.0, 2.0},
                {0.0, 1.0},
                {-1.0, 0.0},
                {1.0, 0.0},
                {0.0, -1.0},
                {0.0, -2.0},
            };
            const TVector<TEdgeDesc> edges = {
                {0, 1, 1.0},
                {1, 2, 1.0},
                {1, 3, 2.0},
                {2, 4, 3.0},
                {3, 4, 1.0},
                {4, 5, 1.0},
            };
            return CreateRoadGraph(vertices, edges, turnInfos, mapping);
        };

        ///    vertices      edges
        ///
        ///       2
        ///      / \         coords: v0 - (0.0; 0.0)
        ///   e2/   \e1              v1 - (0.0; 2.0)
        ///    /     \               v2 - (1.0; 1.0)
        ///   0-------1
        ///       e0
        ///
        TGraph CreateTriangleRoadGraph(
            const TVector<TTurnInfoDesc>& turnInfos = {},
            std::unordered_map<ui32, TId>* mapping = nullptr) {
            const TVector<TPoint> vertices = {
                {0.0, 0.0},
                {2.0, 0.0},
                {1.0, 1.0},
            };
            const TVector<TEdgeDesc> edges = {
                {0, 1, 2.0},
                {1, 2, 1.0},
                {2, 0, 1.0},
            };
            return CreateRoadGraph(vertices, edges, turnInfos, mapping);
        };

        /// @{
        ///    vertices      edges
        ///       0            x
        ///      / ^         0/ ^2
        ///    |/_  \       |/_  \
        ///    1---->2      x--1->x
        TGraph CreateCycleGraph(size_t edgeScale = 1) {
            return CreateGraph(3, {
                                      {0, 1, 1.0 * edgeScale},
                                      {1, 2, 1.0 * edgeScale},
                                      {2, 0, 1.0 * edgeScale},
                                  }
                               );
        };
        TGraph CreateGiantCycleGraph() {
            return CreateCycleGraph(1000);
        }
        /// @}

        TPersistentIndex CreateRhombusPersistentIndex() {
            auto builder = TPersistentIndexBuilder();
            for (ui32 i = 0; i < 6u; ++i) {
                builder.Add(TPersistentEdgeId{(1ull << 40) + static_cast<unsigned long>(i)}, TEdgeId{i});
            }

            char filename[]{"persistent_index.XXXXXX"};
            int fd = mkstemp(filename);
            Y_VERIFY(fd != -1);
            // filename now contains actual filename

            return TPersistentIndex(builder.Build(filename));
        }

        TPersistentIndex CreateCyclePersistentIndex() {
            auto builder = TPersistentIndexBuilder();
            for (ui32 i = 0; i < 3u; ++i) {
                builder.Add(TPersistentEdgeId{(1ull << 40) + static_cast<unsigned long>(i)}, TEdgeId{i});
            }

            char filename[]{"persistent_index.XXXXXX"};
            int fd = mkstemp(filename);
            Y_VERIFY(fd != -1);
            // filename now contains actual filename

            return TPersistentIndex(builder.Build(filename));
        }

        TPersistentIndex CreatePersistentIndexForGraphFromWikipedia() {
            auto builder = TPersistentIndexBuilder();
            for (ui32 i = 0; i < 10u; ++i) {
                builder.Add(TPersistentEdgeId{(1ull << 40) + static_cast<unsigned long>(i)}, TEdgeId{i});
            }

            char filename[]{"persistent_index.XXXXXX"};
            int fd = mkstemp(filename);
            Y_VERIFY(fd != -1);
            // filename now contains actual filename

            return TPersistentIndex(builder.Build(filename));
        }

        TGraph BuildGraphForDijkstraFromWikipedia() {
            return CreateGraph(7, {
                                      {0, 1, 0},
                                      {1, 2, 7},
                                      {1, 3, 9},
                                      {1, 5, 14},
                                      {2, 3, 10},
                                      {2, 4, 15},
                                      {3, 4, 11},
                                      {3, 5, 2},
                                      {4, 6, 6},
                                      {5, 6, 9},
                                  }
                                );
        }

        TGraph BuildGraphForMultipleStartEdges() {
            return CreateGraph(7, {
                                      {0, 1, 1},
                                      {0, 2, 1},
                                      {1, 0, 1},
                                      {1, 2, 1},
                                      {1, 3, 1},
                                      {2, 0, 1},
                                      {2, 1, 1},
                                      {2, 4, 2},
                                      {3, 1, 1},
                                      {3, 5, 1},
                                      {4, 2, 2},
                                      {4, 6, 2},
                                      {5, 3, 1},
                                      {5, 6, 1},
                                      {6, 4, 2},
                                      {6, 5, 1},
                                  }
                               );
        }

        /*
         *         e0 (5)                   e2 (5)
         *  v0 -----------------> v1 <------------------- v2
         *  ^                    ^  |                     ^
         *  |                    |  |                     |
         *  |             e4 (2) |  | e1 (2)              |
         *  |e3 (5)              |  |                     |e7 (5)
         *  |                    |  |                     |
         *  |                    |  |                     |
         *  |      e5 (5)        |  v       e6 (5)        |
         *  v3 <----------------- v4 -------------------> v5
         *
        */
        TGraph BuildGraphForStartFromPositionOnEdge() {
            return CreateGraph(6, {
                                      {0, 1, 5}, // e0
                                      {1, 4, 2}, // e1
                                      {2, 1, 5},
                                      {3, 0, 5},
                                      {4, 1, 2}, // e4
                                      {4, 3, 5}, // e5
                                      {4, 5, 5},
                                      {5, 2, 5},
                                  }
                               );
        }

        TGraph BuildGraphForBoomBarriers(TReverse reverse, TBoomBarriersTestCase testcase) {
            auto builder = std::make_unique<TRoadGraphDataBuilder>(6, 13, 0);
            for (size_t i = 0; i < 6; ++i) {
                builder->SetVertexGeometry(TVertexId(i), {37.0 + 0.1 * i, 55.0});
            }

            struct EdgeInfo {
                ui32 source;
                ui32 target;
                double length;
            };

            std::vector<EdgeInfo> edges = {
                {0, 1, 1.}, // number  0 when reverse==no and number  1 else
                {0, 2, 5.}, // number  1 when reverse==no and number  3 else
                {1, 2, 1.}, // number  2 when reverse==no and number  4 else
                {1, 0, 1.}, // number  3 when reverse==no and number  0 else
                {2, 3, 2.}, // number  4 when reverse==no and number  6 else
                {2, 3, 4.}, // number  5 when reverse==no and number  7 else
                {2, 1, 1.}, // number  6 when reverse==no and number  2 else
                {3, 4, 1.}, // number  7 when reverse==no and number  9 else
                {3, 5, 5.}, // number  8 when reverse==no and number 11 else
                {3, 2, 2.}, // number  9 when reverse==no and number  5 else
                {4, 5, 1.}, // number 10 when reverse==no and number 12 else
                {4, 3, 1.}, // number 11 when reverse==no and number  8 else
                {5, 4, 1.}, // number 12 when reverse==no and number 10 else
            };

            // strange maps requirement: edge sources array must be a continuous increasing sequence
            if (reverse == TReverse::Yes) {
                std::stable_sort(edges.begin(), edges.end(),
                                 [](const auto& x, const auto& y) { return x.target < y.target; });
            }

            const std::set<ui32> reverse_edge_ids =
                (reverse == TReverse::No) ? std::set<ui32>{3, 6, 9, 11, 12} : std::set<ui32>{1, 4, 6, 9, 12};

            // divine beauty, isn't it?
            const ui32 EdgeInfo::*source = (reverse == TReverse::No) ? &EdgeInfo::source : &EdgeInfo::target;
            const ui32 EdgeInfo::*target = (reverse == TReverse::No) ? &EdgeInfo::target : &EdgeInfo::source;

            for (ui32 i = 0; i < edges.size(); ++i) {
                NTaxi::NGraph2::TPolyline polyline;
                polyline.AddPoint({37.0 + 0.1 * edges[i].*source, 55.0});
                polyline.AddPoint({37.0 + 0.1 * edges[i].*target, 55.0});

                builder->SetEdge(TEdge{TEdgeId(i), TVertexId(edges[i].*source), TVertexId(edges[i].*target)}, true);

                // edge data shouldn't be specified for reverse edges
                if (reverse_edge_ids.count(i))
                    continue;
                builder->SetEdgeData(TEdgeId(i), TEdgeData{1., edges[i].length}, polyline);
            }

            // and now not a beauty
            if (reverse == TReverse::No) {
                builder->AddReverseEdge(TEdgeId(0), TEdgeId(3));
                builder->AddReverseEdge(TEdgeId(6), TEdgeId(2));
                builder->AddReverseEdge(TEdgeId(4), TEdgeId(9));
                builder->AddReverseEdge(TEdgeId(7), TEdgeId(11));
                builder->AddReverseEdge(TEdgeId(10), TEdgeId(12));

                builder->AddAccessPass(TEdgeId(11), TEdgeId(9));

                if (testcase == TBoomBarriersTestCase::WayAround) {
                    builder->AddAccessPass(TEdgeId(12), TEdgeId(11));
                    builder->AddAccessPass(TEdgeId(0), TEdgeId(2));
                    builder->AddAccessPass(TEdgeId(4), TEdgeId(8));
                } else {
                    builder->AddAccessPass(TEdgeId(6), TEdgeId(3));
                    builder->AddAccessPass(TEdgeId(7), TEdgeId(10));
                }

                if (testcase == TBoomBarriersTestCase::BlockTheWay) {
                    builder->AddAccessPass(TEdgeId(2), TEdgeId(4));
                }

            } else {
                builder->AddReverseEdge(TEdgeId(0), TEdgeId(1));
                builder->AddReverseEdge(TEdgeId(2), TEdgeId(4));
                builder->AddReverseEdge(TEdgeId(5), TEdgeId(6));
                builder->AddReverseEdge(TEdgeId(8), TEdgeId(9));
                builder->AddReverseEdge(TEdgeId(10), TEdgeId(12));

                builder->AddAccessPass(TEdgeId(9), TEdgeId(6));

                if (testcase == TBoomBarriersTestCase::WayAround) {
                    builder->AddAccessPass(TEdgeId(0), TEdgeId(2));
                    builder->AddAccessPass(TEdgeId(12), TEdgeId(9));
                    builder->AddAccessPass(TEdgeId(11), TEdgeId(6));
                } else {
                    builder->AddAccessPass(TEdgeId(4), TEdgeId(1));
                    builder->AddAccessPass(TEdgeId(8), TEdgeId(10));
                }

                if (testcase == TBoomBarriersTestCase::BlockTheWay) {
                    builder->AddAccessPass(TEdgeId(2), TEdgeId(5));
                }
            }

            builder->Build();
            return TGraph(std::move(builder));
        }

        TString GraphPath(const TStringBuf& str) {
            static const TString prefix = "taxi/graph/data/graph3/";
            return BinaryPath(prefix + str);
        }

        TString GraphPath() {
            static const TString prefix = "taxi/graph/data/graph3/";
            return BinaryPath(prefix);
        }

        const TGraph& GetTestGraph(TWithEdgeStorage withEdgeStorage = TWithEdgeStorage::No) {
            return GetTestRoadGraph(withEdgeStorage);
        }

        const TGraph& GetTestRoadGraph(TWithEdgeStorage withEdgeStorage = TWithEdgeStorage::No) {
            static TGraph graph(std::make_unique<NTaxi::NGraph2::TRoadGraphDataStorage>(
                GraphPath().c_str(),
                EMappingMode::Precharged));
            static TGraph graphWithEdgeStorage(
              [this]() {
                TGraph result(std::make_unique<NTaxi::NGraph2::TRoadGraphDataStorage>(
                GraphPath().c_str(),
                EMappingMode::Precharged));
                result.BuildEdgeStorage(32);
                return result;
                }()
              );
            if(withEdgeStorage == TWithEdgeStorage::Yes) {
              return graphWithEdgeStorage;
            }
            return graph;
        }

        const TPersistentIndex& GetPersistentIndex() {
            static TPersistentIndex index(
                GraphPath("edges_persistent_index.fb").data());
            return index;
        }

        const TJams* GetJams() {
            static bool isNeedInit = true;
            static TJams jams(GetPersistentIndex());
            if (isNeedInit) {
                jams.Load(GraphPath("jams/yandex-maps-jams-speeds:1of12.pb").c_str());
                jams.Load(GraphPath("jams/yandex-maps-jams-speeds:2of12.pb").c_str());
                jams.Load(GraphPath("jams/yandex-maps-jams-speeds:3of12.pb").c_str());
                jams.Load(GraphPath("jams/yandex-maps-jams-speeds:4of12.pb").c_str());
                jams.Load(GraphPath("jams/yandex-maps-jams-speeds:5of12.pb").c_str());
                jams.Load(GraphPath("jams/yandex-maps-jams-speeds:6of12.pb").c_str());
                jams.Load(GraphPath("jams/yandex-maps-jams-speeds:7of12.pb").c_str());
                jams.Load(GraphPath("jams/yandex-maps-jams-speeds:8of12.pb").c_str());
                jams.Load(GraphPath("jams/yandex-maps-jams-speeds:9of12.pb").c_str());
                jams.Load(GraphPath("jams/yandex-maps-jams-speeds:10of12.pb").c_str());
                jams.Load(GraphPath("jams/yandex-maps-jams-speeds:11of12.pb").c_str());
                jams.Load(GraphPath("jams/yandex-maps-jams-speeds:12of12.pb").c_str());
                isNeedInit = false;
            }

            return &jams;
        }

        TGraph CreateRhombusRoadGraphWithPasses(
            const TVector<TTurnInfoDesc>& turnInfos = {},
            std::unordered_map<ui32, TId>* mapping = nullptr) {
            const TVector<TPoint> vertices = {
                {0, 2},
                {0, 1},
                {-1, 0},
                {1, 0},
                {0, -1},
                {0, -2},
            };
            const TVector<TEdgeDesc> edges =
                {
                    {0, 1, 0, TEdgeCategory::EC_PASSES, 3},
                    {1, 2, 1, TEdgeCategory::EC_ROADS, 18},
                    {1, 3, 2, TEdgeCategory::EC_PASSES, 2},
                    {2, 4, 3, TEdgeCategory::EC_PASSES, 1},
                    {3, 4, 1, TEdgeCategory::EC_ROADS, 16},
                    {4, 5, 1, TEdgeCategory::EC_PASSES, 2},
                };
            auto ret = CreateRoadGraph(vertices, edges, turnInfos, mapping);
            if (enableEdgeStorage)
                ret.BuildEdgeStorage(ThreadCount);
            return ret;
        };

        /// Enable building edge storage for graphs created
        void setEnableEdgeStorage(bool enable = true) {
            enableEdgeStorage = enable;
        }

    private:
        static const constexpr size_t ThreadCount = 32;
        bool enableEdgeStorage = false;
    };
}
