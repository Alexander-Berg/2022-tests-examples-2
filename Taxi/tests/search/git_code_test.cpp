#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <yandex/taxi/graph2/dijkstra_searcher.h>
#include <yandex/taxi/graph2/dijkstra_searcher.h>
#include <yandex/taxi/graph2/graph.h>

#include <unordered_set>
#include <iostream>

using NTaxiExternal::NGraph2::TContainerView;
using NTaxiExternal::NGraph2::TEdge;
using NTaxiExternal::NGraph2::TEdgeData;
using NTaxiExternal::NGraph2::TEdgeAccess;
using NTaxiExternal::NGraph2::TEdgeCategory;
using NTaxiExternal::NGraph2::TGraph;
using NTaxiExternal::NGraph2::TRoadGraphFileLoader;
using NTaxiExternal::NGraph2::TId;
using NTaxiExternal::NGraph2::TObjectIndex;
using NTaxiExternal::NGraph2::TPoint;
using NTaxiExternal::NGraph2::TPolyline;
using NTaxiExternal::NGraph2::TPositionOnEdge;
using NTaxiExternal::NGraphSearch2::IFastObjectSearchActions;
using NTaxiExternal::NGraphSearch2::TWeight;
using NTaxiExternal::NGraphSearch2::TEdgeSearchSettings;
using NTaxiExternal::NGraphSearch2::IEdgeStopCondition;
using NTaxiExternal::NGraphSearch2::EStopReason;
using NTaxiExternal::NGraphSearch2::TDriversOnEdgeInfo;
using NTaxiExternal::NGraph2::TRoadGraphBuilder;

namespace {
        struct TEdgeDesc {
            ui32 source = 0;
            ui32 target = 0;
            double length = 1.0;
            TEdgeCategory category = TEdgeCategory::EC_ROADS;
            double speed = 1.0;
            bool isTollRoad = false;
            TEdgeAccess access = TEdgeAccess::EA_AUTOMOBILE;
        };

        inline TId operator""_eid(unsigned long long int value) {
            return static_cast<TId>(value);
        }

        TGraph& CreateGraph(size_t num_vertices, const TVector<TEdgeDesc>& edges) {
            static std::unique_ptr<TGraph> graph;
            if (graph)
                return *graph;

            auto builder = TRoadGraphBuilder::Create(num_vertices, edges.size(), 0);
            for (size_t i = 0; i < num_vertices; ++i) {
                double coord = i;
                builder->SetVertexGeometry(TId(i), {coord, coord});
            }

            for (ui32 i = 0; i < edges.size(); ++i) {
                const auto& edge_desc = edges[i];

                const auto& id = i;
                const auto& source = edge_desc.source;
                const auto& target = edge_desc.target;

                TPolyline fake_polyline;
                double coord1 = source;
                double coord2 = target;
                fake_polyline.AddPoint({coord1, coord1});
                fake_polyline.AddPoint({coord2, coord2});

                auto data = TEdgeData{};
                data.Speed = edge_desc.speed;
                data.Length = edge_desc.length;
                data.Category = edge_desc.category;
                data.IsTollRoad = edge_desc.isTollRoad;
                data.Access = edge_desc.access;
                builder->SetEdge(TEdge{TId(id), TId(source), TId(target)}, true);
                builder->SetEdgeData(TId(id), data, fake_polyline);
            }

            builder->Build();

            auto ret = new TGraph{std::move(builder)};
            ret->BuildEdgeStorage(32);

            graph.reset(ret);
            return *graph;
        }

        TGraph& CreateCycleGraph(size_t edgeScale = 1) {
            return CreateGraph(3, {
                                      {0, 1, 1.0 * edgeScale},
                                      {1, 2, 1.0 * edgeScale},
                                      {2, 0, 1.0 * edgeScale},
                                  }
                               );
        }

    const TGraph& GetGiantCycleGraph() {
        return CreateCycleGraph(1000);
    }

    class TestSearchActionsCodeAsInGit: public IFastObjectSearchActions {
    public:
        using SearchState = NTaxiExternal::NGraphSearch2::SearchState;
        TestSearchActionsCodeAsInGit(const TObjectIndex& obj_index)
          : obj_index_(obj_index)
        {
        }

    public:
        SearchState OnFoundObjects(TWeight currentDistance, TWeight edgeWeight, double targetPosition,
                const TContainerView<TObjectIndex::TObjectPosition>& objsOnEdge) final {
            for (const auto& pos : objsOnEdge) {
                const auto& edge_pos = pos.Position;
                TWeight distance =
                    currentDistance + edgeWeight * fabs(edge_pos.Position - targetPosition);
                distances[pos.Uuid] = distance;
            }

            return SearchState::ContinueState;
        }

        SearchState OnFoundObjects(TWeight currentDistance, TWeight edgeWeight, TDriversOnEdgeInfo, double targetPosition,
                const TContainerView<TObjectIndex::TObjectPosition>& objsOnEdge) final {
            return OnFoundObjects(currentDistance, edgeWeight, targetPosition, objsOnEdge);
        }

        auto GetDistances() const {
            return distances;
        }

        const TObjectIndex& obj_index_;
        std::unordered_map<ui64, double> distances;
    };

Y_UNIT_TEST_SUITE(external_fast_dijkstra_searcher_eta_test) {
    Y_UNIT_TEST(TestEtaCommon) {
        const auto& graph = GetGiantCycleGraph();
        const auto& uuid = 1ull;
        ::NTaxiExternal::NGraph2::TObjectIndex objIndex(graph);
        objIndex.Insert(uuid, TPositionOnEdge{1_eid, 0.5});

        TestSearchActionsCodeAsInGit searchActions(objIndex);
        TEdgeSearchSettings settings;
        settings.SetMaxVisitedEdges(10'000u);
        settings.SetTrackPaths(false);

        auto startPos = TPositionOnEdge{0_eid, 0.5};
        ::NTaxiExternal::NGraphSearch2::TDijkstraSearcher searcher(graph, searchActions, settings, objIndex);
        searcher.Search(startPos);

        UNIT_ASSERT(searchActions.GetDistances()[uuid] == 2000.0);
    }
    Y_UNIT_TEST(TestEtaSameEdge) {
        const auto& graph = GetGiantCycleGraph();
        const auto& uuid = 1ull;
        ::NTaxiExternal::NGraph2::TObjectIndex objIndex(graph);
        objIndex.Insert(uuid, TPositionOnEdge{0_eid, 0.2});

        TestSearchActionsCodeAsInGit searchActions(objIndex);
        TEdgeSearchSettings settings;
        settings.SetMaxVisitedEdges(10'000u);
        settings.SetTrackPaths(false);

        auto startPos = TPositionOnEdge{0_eid, 0.4};
        ::NTaxiExternal::NGraphSearch2::TDijkstraSearcher searcher(graph, searchActions, settings, objIndex);
        searcher.Search(startPos);

        UNIT_ASSERT(searchActions.GetDistances()[uuid] == 200.0);
    }
    Y_UNIT_TEST(TestEtaSameEdgeDriversOnCorners) {
        const auto& graph = GetGiantCycleGraph();
        const auto& uuid = 1ull;
        ::NTaxiExternal::NGraph2::TObjectIndex objIndex(graph);
        objIndex.Insert(uuid, TPositionOnEdge{0_eid, 0.0});
        objIndex.Insert(uuid + 1, TPositionOnEdge{0_eid, 1.0});

        TestSearchActionsCodeAsInGit searchActions(objIndex);
        TEdgeSearchSettings settings;
        settings.SetMaxVisitedEdges(10'000u);
        settings.SetTrackPaths(false);

        auto startPos = TPositionOnEdge{0_eid, 0.4};
        ::NTaxiExternal::NGraphSearch2::TDijkstraSearcher searcher(graph, searchActions, settings, objIndex);
        searcher.Search(startPos);

        UNIT_ASSERT(searchActions.GetDistances()[uuid] == 400.0);
        UNIT_ASSERT(searchActions.GetDistances()[uuid + 1] == 2400.0);
    }
    Y_UNIT_TEST(TestEtaStartFromTheEndOfEdge) {
        const auto& graph = GetGiantCycleGraph();
        const auto& uuid = 1ull;
        ::NTaxiExternal::NGraph2::TObjectIndex objIndex(graph);
        objIndex.Insert(uuid, TPositionOnEdge{0_eid, 1.0});
        objIndex.Insert(uuid + 1, TPositionOnEdge{0_eid, 0.0});
        objIndex.Insert(uuid + 2, TPositionOnEdge{2_eid, 0.2});

        TestSearchActionsCodeAsInGit searchActions(objIndex);
        TEdgeSearchSettings settings;
        settings.SetMaxVisitedEdges(10'000u);
        settings.SetTrackPaths(false);

        auto startPos = TPositionOnEdge{0_eid, 1.0};
        ::NTaxiExternal::NGraphSearch2::TDijkstraSearcher searcher(graph, searchActions, settings, objIndex);
        searcher.Search(startPos);

        UNIT_ASSERT(searchActions.GetDistances()[uuid] == 0.0);
        UNIT_ASSERT(searchActions.GetDistances()[uuid + 1] == 1000.0);
        UNIT_ASSERT(searchActions.GetDistances()[uuid + 2] == 1800.0);
    }
    Y_UNIT_TEST(TestEtaStartFromTheStartOfEdge) {
        const auto& graph = GetGiantCycleGraph();
        const auto& uuid = 1ull;
        ::NTaxiExternal::NGraph2::TObjectIndex objIndex(graph);
        objIndex.Insert(uuid, TPositionOnEdge{0_eid, 1.0});
        objIndex.Insert(uuid + 1, TPositionOnEdge{0_eid, 0.0});
        objIndex.Insert(uuid + 2, TPositionOnEdge{2_eid, 0.2});

        TestSearchActionsCodeAsInGit searchActions(objIndex);
        TEdgeSearchSettings settings;
        settings.SetMaxVisitedEdges(10'000u);
        settings.SetTrackPaths(false);

        auto startPos = TPositionOnEdge{0_eid, 0.0};
        ::NTaxiExternal::NGraphSearch2::TDijkstraSearcher searcher(graph, searchActions, settings, objIndex);
        searcher.Search(startPos);

        UNIT_ASSERT(searchActions.GetDistances()[uuid] == 2000.0);
        UNIT_ASSERT(searchActions.GetDistances()[uuid + 1] == 0.0);
        UNIT_ASSERT(searchActions.GetDistances()[uuid + 2] == 800.0);
    }
}

}
