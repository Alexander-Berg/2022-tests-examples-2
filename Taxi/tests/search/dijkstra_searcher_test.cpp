#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <yandex/taxi/graph2/dijkstra_searcher.h>
#include <yandex/taxi/graph2/graph.h>

#include <unordered_set>

using NTaxiExternal::NGraph2::TContainerView;
using NTaxiExternal::NGraph2::TEdgeData;
using NTaxiExternal::NGraph2::TGraph;
using NTaxiExternal::NGraph2::TRoadGraphFileLoader;
using NTaxiExternal::NGraph2::TId;
using NTaxiExternal::NGraph2::TObjectIndex;
using NTaxiExternal::NGraph2::TPoint;
using NTaxiExternal::NGraph2::TPositionOnEdge;
using NTaxiExternal::NGraphSearch2::IObjectSearchActions;
using NTaxiExternal::NGraphSearch2::TWeight;
using NTaxiExternal::NGraphSearch2::TEdgeSearchSettings;
using NTaxiExternal::NGraphSearch2::IEdgeStopCondition;
using NTaxiExternal::NGraphSearch2::EStopReason;

namespace {
    TString GraphPath(const TStringBuf& str) {
        static const TString prefix = "taxi/graph/data/graph3/";
        return BinaryPath(prefix + str);
    }

    const TGraph& GetTestGraph() {
        static TGraph graph(TRoadGraphFileLoader::Create(
            GraphPath("road_graph.fb").c_str(),
            GraphPath("rtree.fb").c_str()));
        return graph;
    }

    class TestSearchActions: public IObjectSearchActions {
    public:
        TestSearchActions(const TObjectIndex& objectIndex)
            : IObjectSearchActions(objectIndex)
        {
        }

    public:
        SearchState OnFoundObjects(TWeight currentDistance, TWeight edgeWeight,
                const TContainerView<TObjectIndex::TObjectPosition>& objsOnEdge) final {
            std::ignore = currentDistance;
            std::ignore = edgeWeight;
            for (const auto& pos : objsOnEdge) {
                EdgeIds.insert(pos.Position.EdgeId);
            }

            return SearchState::ContinueState;
        }

        SearchState OnFoundObjects(TWeight currentDistance, double, TWeight edgeWeight,
                const TContainerView<TObjectIndex::TObjectPosition>& objsOnEdge) final {
            return OnFoundObjects(currentDistance, edgeWeight, objsOnEdge);
        }

        std::unordered_set<TId> GetEdgeIds() const {
            return EdgeIds;
        }

    private:
        std::unordered_set<TId> EdgeIds;
    };

    struct AlwaysStopStopCondition : public IEdgeStopCondition {
        bool operator()(TId, TWeight) noexcept final {
            return true;
        }
    } ALWAYS_STOP_STOP_CONDITION;

}

Y_UNIT_TEST_SUITE(external_dijkstra_searcher_test) {
    Y_UNIT_TEST(TestObjectRulesEdgeLimit) {
        const auto& graph = GetTestGraph();
        const auto& uuid = 1ull;
        ::NTaxiExternal::NGraph2::TObjectIndex objIndex(graph);
        UNIT_ASSERT(objIndex.Insert(uuid, TPoint{37.676062, 55.748181}));
        UNIT_ASSERT(objIndex.Insert(uuid + 1, TPoint{37.684551, 55.746956}));
        UNIT_ASSERT(objIndex.Insert(uuid + 3, TPoint{37.586798, 55.653567}));

        const auto& edgeId = objIndex.GetPosition(uuid).EdgeId;
        const auto& edgeId2 = objIndex.GetPosition(uuid + 1).EdgeId;

        TestSearchActions searchActions(objIndex);
        TEdgeSearchSettings settings;
        settings.SetMaxVisitedEdges(10'000u);

        ::NTaxiExternal::NGraphSearch2::TDijkstraSearcher searcher(graph, searchActions, settings);
        searcher.Search(edgeId);
        const auto searchStopReason = searcher.GetSearchStopReason();
        UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::ByStopCondition);

        std::unordered_set<TId> res{edgeId, edgeId2};
        UNIT_ASSERT_EQUAL(searchActions.GetEdgeIds(), res);

        const auto& pos = objIndex.GetPosition(uuid + 1);
        const auto& length = searcher.GetPathLengthInMeters(pos);
        UNIT_ASSERT(length.isInitialized);
        UNIT_ASSERT_DOUBLES_EQUAL(
            length.value,
            4720.03,
            0.1
        );

        const auto& route = searcher.GetRoute(pos);
        UNIT_ASSERT(!route.Path.Empty());
    }

    Y_UNIT_TEST(TestSearchStopReason) {
        const auto& graph = GetTestGraph();
        ::NTaxiExternal::NGraph2::TObjectIndex objIndex(graph);
        TestSearchActions searchActions(objIndex);

        ::NTaxiExternal::NGraphSearch2::TDijkstraSearcher searcher(graph, searchActions);
        const TId someEdgeId = 54319;

        {
            searcher.Search(someEdgeId);
            UNIT_ASSERT_EQUAL(searcher.GetSearchStopReason(), EStopReason::Done);
        }

        {
            TEdgeSearchSettings settings;
            settings.SetStopCondition(ALWAYS_STOP_STOP_CONDITION);
            searcher.SetSearchSettings(settings);

            searcher.Search(someEdgeId);
            UNIT_ASSERT_EQUAL(searcher.GetSearchStopReason(), EStopReason::ByStopCondition);
        }
    }

    Y_UNIT_TEST(TestVisualization) {
        const auto& graph = GetTestGraph();
        ::NTaxiExternal::NGraph2::TObjectIndex objIndex(graph);
        TestSearchActions searchActions(objIndex);

        TEdgeSearchSettings searchSettings;
        searchSettings.SetMaxVisitedEdges(100);

        ::NTaxiExternal::NGraphSearch2::TDijkstraSearcher searcher(graph, searchActions, searchSettings, NTaxiExternal::NGraphSearch2::TVisualizationEnabler{});

        {
            const TId someEdgeId = 54319;
            searcher.Search(someEdgeId);
            UNIT_ASSERT(searcher.GetVisualizationData() != nullptr);
            UNIT_ASSERT(strlen(searcher.GetVisualizationData()) > 0);
        }

    }

    Y_UNIT_TEST(TestSearchSettingsConstructor) {
        const auto& graph = GetTestGraph();
        ::NTaxiExternal::NGraph2::TObjectIndex objIndex(graph);
        TestSearchActions searchActions(objIndex);
        const TEdgeSearchSettings settings{2'000'000'000ull, ALWAYS_STOP_STOP_CONDITION};

        ::NTaxiExternal::NGraphSearch2::TDijkstraSearcher searcher(graph, searchActions, settings);
        const TId someEdgeId = 54319;

        searcher.Search(someEdgeId);
        UNIT_ASSERT_EQUAL(searcher.GetSearchStopReason(), EStopReason::ByStopCondition);
    }
}
