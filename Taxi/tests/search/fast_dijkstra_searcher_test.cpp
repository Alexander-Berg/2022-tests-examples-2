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
using NTaxiExternal::NGraphSearch2::IFastObjectSearchActions;
using NTaxiExternal::NGraphSearch2::TWeight;
using NTaxiExternal::NGraphSearch2::TEdgeSearchSettings;
using NTaxiExternal::NGraphSearch2::IEdgeStopCondition;
using NTaxiExternal::NGraphSearch2::EStopReason;
using NTaxiExternal::NGraphSearch2::TDriversOnEdgeInfo;

namespace {
    TString GraphPath(const TStringBuf& str) {
        static const TString prefix = "taxi/graph/data/graph3/";
        return BinaryPath(prefix + str);
    }

    const TGraph& GetTestGraph() {
        static TGraph graph(TRoadGraphFileLoader::Create(
            GraphPath("road_graph.fb").c_str(),
            GraphPath("rtree.fb").c_str()));
        graph.BuildEdgeStorage(4);
        return graph;
    }

    class TestSearchActions: public IFastObjectSearchActions {
    public:
        using SearchState = NTaxiExternal::NGraphSearch2::SearchState;
        TestSearchActions()
        {
        }

    public:
        SearchState OnFoundObjects(TWeight currentDistance, TWeight edgeWeight, double targetPosition,
                const TContainerView<TObjectIndex::TObjectPosition>& objsOnEdge) final {
            std::ignore = currentDistance;
            std::ignore = edgeWeight;
            std::ignore = targetPosition;
            for (const auto& pos : objsOnEdge) {
                EdgeIds.insert(pos.Position.EdgeId);
            }

            return SearchState::ContinueState;
        }

        SearchState OnFoundObjects(TWeight currentDistance, TWeight edgeWeight, TDriversOnEdgeInfo driversInfo, double targetPosition,
                const TContainerView<TObjectIndex::TObjectPosition>& objsOnEdge) final {
            std::ignore = driversInfo;
            return OnFoundObjects(currentDistance, edgeWeight, targetPosition, objsOnEdge);
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

    class TestRouteInfoSearchActions: public IFastObjectSearchActions {
    public:
        using SearchState = NTaxiExternal::NGraphSearch2::SearchState;

        void SetSearcher(NTaxiExternal::NGraphSearch2::TDijkstraSearcher* searcher) {
          Searcher = searcher;
        }

    public:
        SearchState OnFoundObjects(TWeight currentDistance, TWeight edgeWeight, double targetPosition,
                const TContainerView<TObjectIndex::TObjectPosition>& objsOnEdge) final {
            std::ignore = currentDistance;
            std::ignore = edgeWeight;
            std::ignore = targetPosition;
            UNIT_ASSERT(Searcher != nullptr);
            for (const auto& pos : objsOnEdge) {
              UNIT_ASSERT(Searcher->GetRouteInfo(pos.Position).isInitialized);
            }

            return SearchState::ContinueState;
        }

        SearchState OnFoundObjects(TWeight currentDistance, TWeight edgeWeight, TDriversOnEdgeInfo driversInfo, double targetPosition,
                const TContainerView<TObjectIndex::TObjectPosition>& objsOnEdge) final {
            std::ignore = driversInfo;
            return OnFoundObjects(currentDistance, edgeWeight, targetPosition, objsOnEdge);
        }

    private:
        NTaxiExternal::NGraphSearch2::TDijkstraSearcher* Searcher{nullptr};
    };

    class TestChangingSearchSettingRestrictionsActions: public IFastObjectSearchActions {
    public:
        using SearchState = NTaxiExternal::NGraphSearch2::SearchState;

        void SetSearcher(NTaxiExternal::NGraphSearch2::TDijkstraSearcher* searcher) {
          Searcher = searcher;
        }

        void SetNewSettings(const TEdgeSearchSettings* settings) {
            NewSettings = settings;
        }

        bool IsSettingsChanged() const {
            return LastSetSettingResult;
        }

        size_t GetObjectCounter() const {
            return ObjectCounter;
        }

        void Reset() {
            ObjectCounter = 0;
            LastSetSettingResult = false;
            NewSettings = nullptr;
        }

    public:
        SearchState OnFoundObjects(TWeight currentDistance, TWeight edgeWeight, double targetPosition,
                const TContainerView<TObjectIndex::TObjectPosition>& objsOnEdge) final {
            std::ignore = currentDistance;
            std::ignore = edgeWeight;
            std::ignore = targetPosition;
            std::ignore = objsOnEdge;

            ObjectCounter += objsOnEdge.size();
            LastSetSettingResult = Searcher->SetSearchSettings(*NewSettings);

            return SearchState::ContinueState;
        }

        SearchState OnFoundObjects(TWeight currentDistance, TWeight edgeWeight, TDriversOnEdgeInfo driversInfo, double targetPosition,
                const TContainerView<TObjectIndex::TObjectPosition>& objsOnEdge) final {
            std::ignore = driversInfo;
            return OnFoundObjects(currentDistance, edgeWeight, targetPosition, objsOnEdge);
        }

    private:
        NTaxiExternal::NGraphSearch2::TDijkstraSearcher* Searcher{nullptr};
        size_t ObjectCounter = 0;
        const TEdgeSearchSettings* NewSettings{nullptr};
        bool LastSetSettingResult = false;
    };
}

Y_UNIT_TEST_SUITE(external_fast_dijkstra_searcher_test) {
    Y_UNIT_TEST(TestObjectRulesEdgeLimit) {
        const auto& graph = GetTestGraph();
        const auto& uuid = 1ull;
        ::NTaxiExternal::NGraph2::TObjectIndex objIndex(graph);
        UNIT_ASSERT(objIndex.Insert(uuid, TPoint{37.676062, 55.748181}));
        UNIT_ASSERT(objIndex.Insert(uuid + 1, TPoint{37.684551, 55.746956}));
        UNIT_ASSERT(objIndex.Insert(uuid + 3, TPoint{37.586798, 55.653567}));

        const auto& edgeId = objIndex.GetPosition(uuid).EdgeId;
        const auto& edgeId2 = objIndex.GetPosition(uuid + 1).EdgeId;

        TestSearchActions searchActions;
        TEdgeSearchSettings settings;
        settings.SetTrackPaths(true);
        settings.SetMaxVisitedEdges(10'000u);

        ::NTaxiExternal::NGraphSearch2::TDijkstraSearcher searcher(graph, searchActions, settings, objIndex);
        searcher.Search(edgeId);
        const auto searchStopReason = searcher.GetSearchStopReason();
        UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);

        std::unordered_set<TId> res{edgeId, edgeId2};
        Cout << "visited edge ids with drivers: ";
        for(auto edgeId : searchActions.GetEdgeIds()) {
          Cout << edgeId << ", ";
        }
        Cout << Endl;
        UNIT_ASSERT_EQUAL(searchActions.GetEdgeIds(), res);

        const auto& pos = objIndex.GetPosition(uuid + 1);
        const auto& length = searcher.GetPathLengthInMeters(pos);
        UNIT_ASSERT(length.isInitialized);
        UNIT_ASSERT_DOUBLES_EQUAL(
            length.value,
            739.2, /*unlike test for previous edge searcher, here is reverse search*/
            0.1
        );

        const auto& route = searcher.GetRoute(pos);
        UNIT_ASSERT(!route.Path.Empty());
    }

    Y_UNIT_TEST(TestSearchStopReason) {
        const auto& graph = GetTestGraph();
        ::NTaxiExternal::NGraph2::TObjectIndex objIndex(graph);
        TestSearchActions searchActions;
        TEdgeSearchSettings settings;
        settings.SetMaxVisitedEdges(10'000u);

        ::NTaxiExternal::NGraphSearch2::TDijkstraSearcher searcher(graph, searchActions, settings, objIndex);
        const TId someEdgeId = 54319;

        {
            searcher.Search(someEdgeId);
            UNIT_ASSERT_EQUAL(searcher.GetSearchStopReason(), EStopReason::Done);
        }

        {
            TEdgeSearchSettings settings;
            settings.SetStopCondition(ALWAYS_STOP_STOP_CONDITION);
            settings.SetMaxVisitedEdges(20'000u);
            searcher.SetSearchSettings(settings);

            searcher.Search(someEdgeId);
            UNIT_ASSERT_EQUAL(searcher.GetSearchStopReason(), EStopReason::ByStopCondition);
        }
    }

    Y_UNIT_TEST(TestVisualization) {
        const auto& graph = GetTestGraph();
        ::NTaxiExternal::NGraph2::TObjectIndex objIndex(graph);
        TestSearchActions searchActions;

        TEdgeSearchSettings searchSettings;
        searchSettings.SetMaxVisitedEdges(100);
        searchSettings.SetEnableVisualization(true);

        ::NTaxiExternal::NGraphSearch2::TDijkstraSearcher searcher(graph, searchActions, searchSettings, objIndex);

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
        TestSearchActions searchActions;
        const TEdgeSearchSettings settings{2'000'000'000ull, ALWAYS_STOP_STOP_CONDITION};

        ::NTaxiExternal::NGraphSearch2::TDijkstraSearcher searcher(graph, searchActions, settings, objIndex);
        const TId someEdgeId = 54319;

        searcher.Search(someEdgeId);
        Cout << "search stop reason: " << static_cast<int>(searcher.GetSearchStopReason()) << Endl;
        UNIT_ASSERT_EQUAL(searcher.GetSearchStopReason(), EStopReason::ByStopCondition);
    }

    Y_UNIT_TEST(TestSearchTrackPathsEnabled) {
        const auto& graph = GetTestGraph();
        const auto& uuid = 1ull;
        ::NTaxiExternal::NGraph2::TObjectIndex objIndex(graph);
        UNIT_ASSERT(objIndex.Insert(uuid, TPoint{37.676062, 55.748181}));
        UNIT_ASSERT(objIndex.Insert(uuid + 1, TPoint{37.684551, 55.746956}));
        UNIT_ASSERT(objIndex.Insert(uuid + 3, TPoint{37.586798, 55.653567}));

        const auto& edgeId = objIndex.GetPosition(uuid).EdgeId;

        TestSearchActions searchActions;
        TEdgeSearchSettings settings;
        settings.SetMaxVisitedEdges(10'000u);
        settings.SetTrackPaths(true);

        ::NTaxiExternal::NGraphSearch2::TDijkstraSearcher searcher(graph, searchActions, settings, objIndex);
        searcher.Search(edgeId);


        const auto& pos = objIndex.GetPosition(uuid + 1);
        const auto& route = searcher.GetRoute(pos);
        UNIT_ASSERT(!route.Path.Empty());
    }

    Y_UNIT_TEST(TestSearchTrackPathsDisabled) {
        const auto& graph = GetTestGraph();
        const auto& uuid = 1ull;
        ::NTaxiExternal::NGraph2::TObjectIndex objIndex(graph);
        UNIT_ASSERT(objIndex.Insert(uuid, TPoint{37.676062, 55.748181}));
        UNIT_ASSERT(objIndex.Insert(uuid + 1, TPoint{37.684551, 55.746956}));
        UNIT_ASSERT(objIndex.Insert(uuid + 3, TPoint{37.586798, 55.653567}));

        const auto& edgeId = objIndex.GetPosition(uuid).EdgeId;

        TestSearchActions searchActions;
        TEdgeSearchSettings settings;
        settings.SetMaxVisitedEdges(10'000u);
        settings.SetTrackPaths(false);

        ::NTaxiExternal::NGraphSearch2::TDijkstraSearcher searcher(graph, searchActions, settings, objIndex);
        searcher.Search(edgeId);


        const auto& pos = objIndex.GetPosition(uuid + 1);
        const auto& route = searcher.GetRoute(pos);
        UNIT_ASSERT(route.Path.Empty());
    }

    Y_UNIT_TEST(TestSearchChangeSettings) {
        const auto& graph = GetTestGraph();
        const auto& uuid = 1ull;
        ::NTaxiExternal::NGraph2::TObjectIndex objIndex(graph);
        UNIT_ASSERT(objIndex.Insert(uuid, TPoint{37.676062, 55.748181}));
        UNIT_ASSERT(objIndex.Insert(uuid + 1, TPoint{37.684551, 55.746956}));
        UNIT_ASSERT(objIndex.Insert(uuid + 3, TPoint{37.586798, 55.653567}));

        const auto& edgeId = objIndex.GetPosition(uuid).EdgeId;

        TestSearchActions searchActions;
        TEdgeSearchSettings settings;
        settings.SetMaxVisitedEdges(10'000u);
        settings.SetTrackPaths(false);

        ::NTaxiExternal::NGraphSearch2::TDijkstraSearcher searcher(graph, searchActions, settings, objIndex);
        searcher.Search(edgeId);

        const auto& pos = objIndex.GetPosition(uuid + 1);
        const auto& route = searcher.GetRoute(pos);
        UNIT_ASSERT(route.Path.Empty());

        // now change settings and search again
        settings.SetTrackPaths(true);
        UNIT_ASSERT(searcher.SetSearchSettings(settings));
        searcher.Search(edgeId);
        const auto& route2 = searcher.GetRoute(pos);
        UNIT_ASSERT(!route2.Path.Empty());
    }

    class TestChangeSettingsSearchActions: public IFastObjectSearchActions {
    public:
        using SearchState = NTaxiExternal::NGraphSearch2::SearchState;
        TestChangeSettingsSearchActions():
          Searcher(nullptr)
        {
        }

        void SetSearcher(::NTaxiExternal::NGraphSearch2::TDijkstraSearcher& searcher) {
          Searcher = &searcher;
        }

    public:
        SearchState OnFoundObjects(TWeight , TWeight , double ,
                const TContainerView<TObjectIndex::TObjectPosition>& ) final {
          TEdgeSearchSettings newSettings;
          newSettings.SetTrackPaths(true);
          UNIT_ASSERT(Searcher != nullptr);
          UNIT_ASSERT(!Searcher->SetSearchSettings(newSettings));
          return SearchState::ContinueState;
        }

        SearchState OnFoundObjects(TWeight , TWeight , TDriversOnEdgeInfo , double ,
                const TContainerView<TObjectIndex::TObjectPosition>& ) final {
          TEdgeSearchSettings newSettings;
          newSettings.SetTrackPaths(true);
          UNIT_ASSERT(Searcher != nullptr);
          UNIT_ASSERT(!Searcher->SetSearchSettings(newSettings));
          return SearchState::ContinueState;
        }

    private:
        ::NTaxiExternal::NGraphSearch2::TDijkstraSearcher* Searcher{nullptr};
    };

    Y_UNIT_TEST(TestSearchChangeSettingsProhibited) {
        const auto& graph = GetTestGraph();
        const auto& uuid = 1ull;
        ::NTaxiExternal::NGraph2::TObjectIndex objIndex(graph);
        UNIT_ASSERT(objIndex.Insert(uuid, TPoint{37.676062, 55.748181}));
        UNIT_ASSERT(objIndex.Insert(uuid + 1, TPoint{37.684551, 55.746956}));
        UNIT_ASSERT(objIndex.Insert(uuid + 3, TPoint{37.586798, 55.653567}));

        const auto& edgeId = objIndex.GetPosition(uuid).EdgeId;

        TestChangeSettingsSearchActions searchActions;
        TEdgeSearchSettings settings;
        settings.SetMaxVisitedEdges(10'000u);
        settings.SetTrackPaths(false);

        ::NTaxiExternal::NGraphSearch2::TDijkstraSearcher searcher(graph, searchActions, settings, objIndex);
        searchActions.SetSearcher(searcher);
        searcher.Search(edgeId);

        const auto& pos = objIndex.GetPosition(uuid + 1);
        const auto& route = searcher.GetRoute(pos);
        UNIT_ASSERT(route.Path.Empty());
    }

    Y_UNIT_TEST(TestGetRouteInfo) {
        const auto& graph = GetTestGraph();
        const auto& uuid = 1ull;
        ::NTaxiExternal::NGraph2::TObjectIndex objIndex(graph);
        UNIT_ASSERT(objIndex.Insert(uuid, TPoint{37.676062, 55.748181}));
        UNIT_ASSERT(objIndex.Insert(uuid + 1, TPoint{37.684551, 55.746956}));
        UNIT_ASSERT(objIndex.Insert(uuid + 3, TPoint{37.586798, 55.653567}));

        const auto& edgeId = objIndex.GetPosition(uuid).EdgeId;

        TestRouteInfoSearchActions searchActions;
        TEdgeSearchSettings settings;
        settings.SetMaxVisitedEdges(10'000u);
        settings.SetTrackPaths(false);

        ::NTaxiExternal::NGraphSearch2::TDijkstraSearcher searcher(graph, searchActions, settings, objIndex);
        searchActions.SetSearcher(&searcher);
        searcher.Search(edgeId);


        const auto& pos = objIndex.GetPosition(uuid + 1);
        const auto& routeInfo = searcher.GetRouteInfo(pos);
        UNIT_ASSERT(routeInfo.isInitialized);
    }

    Y_UNIT_TEST(TestMaxTime) {
        const auto& graph = GetTestGraph();
        const auto& uuid = 1ull;
        ::NTaxiExternal::NGraph2::TObjectIndex objIndex(graph);
        UNIT_ASSERT(objIndex.Insert(uuid, TPoint{37.676062, 55.748181}));
        UNIT_ASSERT(objIndex.Insert(uuid + 1, TPoint{37.684551, 55.746956}));
        UNIT_ASSERT(objIndex.Insert(uuid + 3, TPoint{37.586798, 55.653567}));

        const auto& edgeId = objIndex.GetPosition(uuid).EdgeId;

        TestRouteInfoSearchActions searchActions;
        TEdgeSearchSettings settings;
        settings.SetMaxTime(10);

        ::NTaxiExternal::NGraphSearch2::TDijkstraSearcher searcher(graph, searchActions, settings, objIndex);
        searchActions.SetSearcher(&searcher);
        searcher.Search(edgeId);
        const auto searchStopReason = searcher.GetSearchStopReason();
        UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);

        UNIT_ASSERT(searcher.GetSkippedEdgesByTimeOrDistance() > 0);
    }

    Y_UNIT_TEST(TestMaxDistance) {
        const auto& graph = GetTestGraph();
        const auto& uuid = 1ull;
        ::NTaxiExternal::NGraph2::TObjectIndex objIndex(graph);
        UNIT_ASSERT(objIndex.Insert(uuid, TPoint{37.676062, 55.748181}));
        UNIT_ASSERT(objIndex.Insert(uuid + 1, TPoint{37.684551, 55.746956}));
        UNIT_ASSERT(objIndex.Insert(uuid + 3, TPoint{37.586798, 55.653567}));

        const auto& edgeId = objIndex.GetPosition(uuid).EdgeId;

        TestRouteInfoSearchActions searchActions;
        TEdgeSearchSettings settings;
        settings.SetMaxPathLengthInMeters(10);

        ::NTaxiExternal::NGraphSearch2::TDijkstraSearcher searcher(graph, searchActions, settings, objIndex);
        searchActions.SetSearcher(&searcher);
        searcher.Search(edgeId);
        const auto searchStopReason = searcher.GetSearchStopReason();
        UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);

        UNIT_ASSERT(searcher.GetSkippedEdgesByTimeOrDistance() > 0);
    }

    Y_UNIT_TEST(TestMaxTimeChanging) {
        const auto& graph = GetTestGraph();
        const auto& uuid = 1ull;
        ::NTaxiExternal::NGraph2::TObjectIndex objIndex(graph);
        UNIT_ASSERT(objIndex.Insert(uuid, TPoint{37.676062, 55.748181}));
        UNIT_ASSERT(objIndex.Insert(uuid + 1, TPoint{37.684551, 55.746956}));
        UNIT_ASSERT(objIndex.Insert(uuid + 3, TPoint{37.586798, 55.653567}));

        const auto& edgeId = objIndex.GetPosition(uuid).EdgeId;

        TEdgeSearchSettings defaultSettings;
        TEdgeSearchSettings shortMaxTimeSettings;
        shortMaxTimeSettings.SetMaxTime(100);

        TestChangingSearchSettingRestrictionsActions searchActions;
        searchActions.SetNewSettings(&shortMaxTimeSettings);

        ::NTaxiExternal::NGraphSearch2::TDijkstraSearcher searcher(graph, searchActions, defaultSettings, objIndex);
        searchActions.SetSearcher(&searcher);
        searcher.Search(edgeId);
        auto searchStopReason = searcher.GetSearchStopReason();
        UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);

        UNIT_ASSERT(searchActions.IsSettingsChanged() == true);
        UNIT_ASSERT(searchActions.GetObjectCounter() == 2);

        searchActions.Reset();
        searcher.SetSearchSettings(shortMaxTimeSettings);
        searchActions.SetNewSettings(&defaultSettings);
        searcher.Search(edgeId);
        searchStopReason = searcher.GetSearchStopReason();
        UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);

        UNIT_ASSERT(searchActions.IsSettingsChanged() == false);
        UNIT_ASSERT(searchActions.GetObjectCounter() == 2);
    }

    Y_UNIT_TEST(TestMaxDistanceChanging) {
        const auto& graph = GetTestGraph();
        const auto& uuid = 1ull;
        ::NTaxiExternal::NGraph2::TObjectIndex objIndex(graph);
        UNIT_ASSERT(objIndex.Insert(uuid, TPoint{37.676062, 55.748181}));
        UNIT_ASSERT(objIndex.Insert(uuid + 1, TPoint{37.684551, 55.746956}));
        UNIT_ASSERT(objIndex.Insert(uuid + 3, TPoint{37.586798, 55.653567}));

        const auto& edgeId = objIndex.GetPosition(uuid).EdgeId;

        TEdgeSearchSettings defaultSettings;
        TEdgeSearchSettings shortMaxDistanceSettings;
        shortMaxDistanceSettings.SetMaxPathLengthInMeters(1000);

        TestChangingSearchSettingRestrictionsActions searchActions;
        searchActions.SetNewSettings(&shortMaxDistanceSettings);

        ::NTaxiExternal::NGraphSearch2::TDijkstraSearcher searcher(graph, searchActions, defaultSettings, objIndex);
        searchActions.SetSearcher(&searcher);
        searcher.Search(edgeId);
        auto searchStopReason = searcher.GetSearchStopReason();
        UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);

        UNIT_ASSERT(searchActions.IsSettingsChanged() == true);
        UNIT_ASSERT(searchActions.GetObjectCounter() == 2);

        searchActions.Reset();
        searcher.SetSearchSettings(shortMaxDistanceSettings);
        searchActions.SetNewSettings(&defaultSettings);
        searcher.Search(edgeId);
        searchStopReason = searcher.GetSearchStopReason();
        UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);

        UNIT_ASSERT(searchActions.IsSettingsChanged() == false);
        UNIT_ASSERT(searchActions.GetObjectCounter() == 2);
    }
}

