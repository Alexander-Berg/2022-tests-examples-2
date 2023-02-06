#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <taxi/graph/libs/graph/graph_data_builder.h>
#include <taxi/graph/libs/search2/dijkstra_edge_searcher.h>
#include <taxi/graph/libs/search2/object_index_edge_processor.h>
#include <taxi/graph/libs/search2/transformator.h>

#include <iostream>
#include <optional>

#include <taxi/graph/libs/graph-test/graph_test_data.h>

#include <util/stream/file.h>

#include "common.h"

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
using NTaxi::NGraphSearch2::DirectionizedEdgePastEnd;
using NTaxi::NGraphSearch2::DirectionizedEdgeStart;
using NTaxi::NGraphSearch2::SearchState;
using NTaxi::NGraphSearch2::TDirectionizedPosition;
using NTaxi::NGraphSearch2::TDistance;
using NTaxi::NGraphSearch2::TFastDijkstraEdgeSearcherDefinitions;
using NTaxi::NGraphSearch2::TFastSearchSettings;
using NTaxi::NGraphSearch2::TRouteInfo;
using NTaxi::NGraphSearch2::TTime;

using namespace NTaxi::NGraph2Literals;

namespace {
    using TTestObjectIndex = NTaxi::NGraph2::TObjectIndex<ui64>;

    [[maybe_unused]] void PrintEdgeIds(const TArrayRef<const TEdgeId>& edges) {
        for (auto id : edges) {
            Cout << id.value() << ", ";
        }
        Cout << Endl;
    }
    [[maybe_unused]] std::string PrintRouteInfo(const std::optional<TRouteInfo>& routeInfo) {
        if (routeInfo) {
            return std::to_string(routeInfo->PathLengthInMeters.value());
        } else {
            return std::string{"nullopt"};
        }
    };

    template <typename TSearchTraits>
    struct TTestCallback {
        using TEdgeObjectsRange = typename TTestObjectIndex::TEdgeObjectsRange;
        using TAdditionalEdgeInfo = typename TFastDijkstraEdgeSearcherDefinitions<TSearchTraits>::TAdditionalEdgeInfo;
        /// This is helper method to correctly find distance to given object
        inline auto GetObjectWeight(TTime currentDistance, TDirectionizedPosition edgeStart, TTime edgeTime, const TDirectionizedPosition pos) const noexcept {
            return currentDistance + edgeTime * fabs((pos - edgeStart).value());
        }

        template <typename TSearcher>
        SearchState operator()(TTime timeToEdge, TTime timeOfEdge, TAdditionalEdgeInfo additionalInfo,
                               TDirectionizedPosition fromPosition, TDirectionizedPosition toPosition,
                               TEdgeObjectsRange&& objsOnEdge, const TSearcher& searcher) {
            for (const auto& key_pos : objsOnEdge) {
                const auto pos = key_pos.second;
                UNIT_ASSERT(toPosition > fromPosition);
                const TDirectionizedPosition normalizedPos = TSearchTraits::TDirectionControl::MapPositionToDirection(pos.Position);
                if (!(normalizedPos >= fromPosition && normalizedPos < toPosition)) {
                    // pos is out of designated range
                    continue;
                }
                EdgeWeights.push_back(timeOfEdge.count());

                EdgeIds.push_back(pos.GetEdgeId());
                UniqueEdgeIds.insert(pos.GetEdgeId());
                DistancesToFinalEdgesFromStart.push_back(timeToEdge.count());

                i32 leeway = NTaxi::NGraphSearch2::NFastDijkstraDetail::INF_LEEWAY;
                if constexpr (TSearchTraits::TrackEdgeLeeway) {
                    leeway = additionalInfo.Leeway;
                }
                EdgeLeeways[pos.GetEdgeId()] = leeway;

                // We calc distance same way in git/geograph
                TTime distance = GetObjectWeight(timeToEdge, fromPosition, timeOfEdge, normalizedPos);
                DistancesToObjects[key_pos.first] = distance.count();

                {
                    auto fit = RouteInfos.find(key_pos.first);
                    UNIT_ASSERT(fit == RouteInfos.end()); // no duplicates
                    RouteInfos[key_pos.first] = searcher.GetRouteInfo(pos);
                }
            }

            return SearchState::ContinueState;
        }

        template <typename TSearcher>
        SearchState operator()(TTime timeToEdge, TTime timeOfEdge, TAdditionalEdgeInfo additionalInfo,
                               TEdgeObjectsRange&& objsOnEdge, const TSearcher& searcher) {
            return (*this)(timeToEdge,
                           timeOfEdge,
                           additionalInfo,
                           DirectionizedEdgeStart,
                           DirectionizedEdgePastEnd,
                           std::move(objsOnEdge),
                           searcher);
        }

        std::vector<TId> GetEdgeIds() const {
            return EdgeIds;
        }

        std::unordered_set<TEdgeId> GetUniqueEdgeIds() const {
            return UniqueEdgeIds;
        }

        std::vector<double> GetEdgeWeights() const {
            return EdgeWeights;
        }

        auto GetEdgeLeeways() const {
            return EdgeLeeways;
        }

        std::vector<double> GetDistancesFromStart() const {
            return DistancesToFinalEdgesFromStart;
        }

        // yes, it is not const auto&. Easier to write operator[] in tests
        // this way
        auto GetDistancesToObjects() const {
            return DistancesToObjects;
        }

        const auto& GetRouteInfos() const {
            return RouteInfos;
        }

        void PrintEdgeIds() const {
            Cout << "Edge ids:" << Endl;
            ::PrintEdgeIds(EdgeIds);
        }

        void Reset() {
            EdgeIds.clear();
            EdgeWeights.clear();
            DistancesToFinalEdgesFromStart.clear();
            DistancesToObjects.clear();
            RouteInfos.clear();
            UniqueEdgeIds.clear();
            EdgeLeeways.clear();
        }

    private:
        std::vector<TId> EdgeIds;
        std::vector<double> EdgeWeights;
        std::vector<double> DistancesToFinalEdgesFromStart;
        std::unordered_map<ui64, double> DistancesToObjects;
        std::unordered_map<ui64, std::optional<NTaxi::NGraphSearch2::TRouteInfo>> RouteInfos;
        std::unordered_set<TEdgeId> UniqueEdgeIds;
        std::unordered_map<TId, i32> EdgeLeeways;
    };

    template <typename TSearchTraits>
    struct TTestSettingsChangingCallback {
        using TEdgeObjectsRange = typename TTestObjectIndex::TEdgeObjectsRange;
        using TAdditionalEdgeInfo = typename TFastDijkstraEdgeSearcherDefinitions<TSearchTraits>::TAdditionalEdgeInfo;

        template <typename TSearcher>
        SearchState operator()(TTime timeToEdge, TTime timeOfEdge, TAdditionalEdgeInfo additionalInfo,
                               TDirectionizedPosition fromPosition, TDirectionizedPosition toPosition,
                               TEdgeObjectsRange&& objsOnEdge, const TSearcher& searcher) {
            ObjectCounter += objsOnEdge.size();

            LastSetSettingResult = const_cast<TSearcher&>(searcher).SetSearchSettings(NewSettings);

            return SearchState::ContinueState;
        }

        template <typename TSearcher>
        SearchState operator()(TTime timeToEdge, TTime timeOfEdge, TAdditionalEdgeInfo additionalInfo,
                               TEdgeObjectsRange&& objsOnEdge, const TSearcher& searcher) {
            return (*this)(timeToEdge,
                           timeOfEdge,
                           additionalInfo,
                           DirectionizedEdgeStart,
                           DirectionizedEdgePastEnd,
                           std::move(objsOnEdge),
                           searcher);
        }

        void SetNewSettings(TFastSearchSettings settings) {
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
            NewSettings = {};
            LastSetSettingResult = false;
        }

    private:
        size_t ObjectCounter = 0;
        TFastSearchSettings NewSettings{};
        bool LastSetSettingResult = false;
    };

    struct TestImmediateStopCallback {
        using TEdgeObjectsRange = typename TTestObjectIndex::TEdgeObjectsRange;
        template <typename... Args>
        SearchState operator()(Args&&...) {
            return SearchState::BreakState;
        }
    };

    template <typename TSearchTraits>
    struct TestContinueSearchCallback {
        using TEdgeObjectsRange = typename TTestObjectIndex::TEdgeObjectsRange;
        using TAdditionalEdgeInfo = typename TFastDijkstraEdgeSearcherDefinitions<TSearchTraits>::TAdditionalEdgeInfo;

        template <typename TSearcher>
        SearchState operator()(TTime, TTime, TAdditionalEdgeInfo,
                               TDirectionizedPosition, TDirectionizedPosition,
                               TEdgeObjectsRange&&, const TSearcher&) {
            return SearchState::ContinueState;
        }

        template <typename TSearcher>
        SearchState operator()(TTime, TTime, TAdditionalEdgeInfo,
                               TEdgeObjectsRange&& objsOnEdge, const TSearcher&) {
            lastFoundEdges = std::nullopt;
            if (objsOnEdge.size()) {
                lastFoundEdges = objsOnEdge;
                return SearchState::BreakState;
            }
            return SearchState::ContinueState;
        }

        std::optional<TEdgeObjectsRange> lastFoundEdges = std::nullopt;
    };

    const TFastSearchSettings TEST_SETTINGS{
        [] {
            TFastSearchSettings result;
            result.MaxVisitedEdgesCount = 10'000u;
            return result;
        }()};

    template <typename TSearchTraits, typename TCallback>
    struct TTestFastDijkstraEdgeSearcher {
        TTestFastDijkstraEdgeSearcher(const NTaxi::NGraph2::TGraph& graph,
                                      const TFastSearchSettings& settings,
                                      const TTestObjectIndex& objectIndex,
                                      TCallback& callback,
                                      const NTaxi::NGraph2::TJams* jamsPtr = nullptr,
                                      const NTaxi::NGraph2::TClosures* closuresPtr = nullptr)
            : Graph(graph)
            , EdgeProcessor(objectIndex, callback)
            , Searcher({graph, graph.GetEdgeStorage()}, settings, EdgeProcessor, jamsPtr, closuresPtr)
        {
        }

        template <typename... Args>
        auto Search(Args&&... args) {
            return Searcher.Search(std::forward<Args>(args)...);
        }

        auto Search(TEdgeId edge) {
            TVector<TPositionOnEdge> startEdges;
            startEdges.push_back(TPositionOnEdge{edge, TSearcher::TSearchTraits::TDirectionControl::UnmapDirectionizedPosition(DirectionizedEdgeStart)});
            return Search(startEdges);
        }
        auto Search(TArrayRef<const TEdgeId> edges) {
            TVector<TPositionOnEdge> startEdges;
            for (auto edge : edges) {
                startEdges.push_back(TPositionOnEdge{edge, TSearcher::TSearchTraits::TDirectionControl::UnmapDirectionizedPosition(DirectionizedEdgeStart)});
            }
            return Search(startEdges);
        }
        auto Search(TPositionOnEdge posOnEdge) {
            TVector<TPositionOnEdge> startEdges;
            startEdges.push_back(posOnEdge);
            return Search(startEdges);
        }

        auto ContinueSearch() {
            return Searcher.ContinueSearch();
        }

        template <typename... Args>
        auto GetPath(Args&&... args) const {
            return Searcher.GetPath(std::forward<Args>(args)...);
        }

        bool SetSearchSettings(TFastSearchSettings settings) {
            return Searcher.SetSearchSettings(settings);
        }

        const TGraph& Graph;

        using TTestEdgeProcessor =
            NTaxi::NGraphSearch2::TObjectIndexExtendedEdgeProcessor<
                TSearchTraits,
                TTestObjectIndex,
                TCallback>;

        TTestEdgeProcessor EdgeProcessor;

        using TSearcher =
            NTaxi::NGraphSearch2::TFastDijkstraEdgeSearcher<
                NTaxi::NGraph2::TGraphFacadeCommon,
                TSearchTraits,
                TTestEdgeProcessor>;
        TSearcher Searcher;
    };

    template <typename Traits>
    struct TTestObjectIndexSearcher {
        using MyTraits = Traits;
        using MyCallback = TestImmediateStopCallback;
        using MyEdgeProcessor = NTaxi::NGraphSearch2::TObjectIndexEdgeProcessor<
            MyTraits,
            TTestObjectIndex,
            MyCallback>;
        using MySearcher = NTaxi::NGraphSearch2::TFastDijkstraEdgeSearcher<
            NTaxi::NGraph2::TGraphFacadeCommon,
            MyTraits,
            MyEdgeProcessor,
            NTaxi::NGraphSearch2::DijkstraSearchNoDebugHandlers>;

        static constexpr unsigned char MyFlags = Traits::MyFlags;

        MyEdgeProcessor Processor;
        MySearcher Searcher;

        TTestObjectIndexSearcher(const TGraph& graph, const TFastSearchSettings& settings, 
                            const TTestObjectIndex& objectIndex, MyCallback& callback,
                            const TJams* jamsPtr, const TClosures* closuresPtr)
            : Processor(objectIndex, callback)
            , Searcher({graph, graph.GetEdgeStorage()}, settings, Processor, jamsPtr, closuresPtr, {})
        {
        }
    };

    class TTestObjectIndexSearcherCreator {
    private:
        TestImmediateStopCallback& Callback;
        const TTestObjectIndex& ObjIndex;

    public:
        TTestObjectIndexSearcherCreator(TestImmediateStopCallback& callback, const NTaxi::NGraph2::TObjectIndex<std::uint64_t>& objIndex)
            : Callback(callback)
            , ObjIndex(objIndex)
        {
        }

        template<typename TTarget>
        auto operator()(
                const TGraph& graph,
                const TFastSearchSettings& settings,
                const TJams* jamsPtr,
                const TClosures* closuresPtr) const {
            return std::make_unique<TTarget>(graph, settings, ObjIndex, Callback, jamsPtr, closuresPtr);
        };
    };

    template<typename TTraits>
    using TObjectIndexTarget = TTestObjectIndexSearcher<TTraits>;

    using TTestObjectIndexTransformator = NTaxi::NGraphSearch2::TTransformator<
        TTestSearchTraitsFlags,
        TTestSearchTraitsToFlagsConverter,
        TTestSearchTraitsWithFlags,
        TObjectIndexTarget>;
}

class TGraphObjectsSearchFixture: public ::NUnitTest::TBaseTestCase, public NTaxi::NGraph2::TGraphTestData {
};

Y_UNIT_TEST_SUITE_F(graph_objects_search, TGraphObjectsSearchFixture) {
    Y_UNIT_TEST(TestObjectRulesEdgeLimit) {
        const auto& graph = GetTestGraph(TWithEdgeStorage::Yes);
        const auto& uuid = 1ull;
        TTestObjectIndex objIndex(graph);
        UNIT_ASSERT(objIndex.Insert(uuid, NTaxi::NGraph2::TPoint{37.676062, 55.748181}));
        UNIT_ASSERT(objIndex.Insert(uuid + 1, NTaxi::NGraph2::TPoint{37.684551, 55.746956}));
        UNIT_ASSERT(objIndex.Insert(uuid + 3, NTaxi::NGraph2::TPoint{37.586798, 55.653567}));

        const auto& edgeId = objIndex.GetPosition(uuid).GetEdgeId();
        const auto& edgeId2 = objIndex.GetPosition(uuid + 1).GetEdgeId();

        TTestCallback<TTestForwardSearchTraits> foundCallback;

        TTestFastDijkstraEdgeSearcher<TTestForwardSearchTraits, TTestCallback<TTestForwardSearchTraits>> searcher(graph, TEST_SETTINGS, objIndex, foundCallback);
        searcher.Search(edgeId);

        std::vector<TId> res{edgeId, edgeId2};
        foundCallback.PrintEdgeIds();
        Cout << "Reference: (size: " << res.size() << ")" << Endl;
        PrintEdgeIds(res);
        UNIT_ASSERT_EQUAL(foundCallback.GetEdgeIds(), res);
    } // Y_UNIT_TEST(TestObjectRulesEdgeLimit)

    Y_UNIT_TEST(TestContinueSearch) {
        const auto& graph = GetTestGraph(TWithEdgeStorage::Yes);
        const auto& uuid = 1ull;
        TTestObjectIndex objIndex(graph);
        UNIT_ASSERT(objIndex.Insert(uuid, NTaxi::NGraph2::TPoint{37.676062, 55.748181}));
        UNIT_ASSERT(objIndex.Insert(uuid + 1, NTaxi::NGraph2::TPoint{37.684551, 55.746956}));
        UNIT_ASSERT(objIndex.Insert(uuid + 2, NTaxi::NGraph2::TPoint{37.684000, 55.746000}));
        UNIT_ASSERT(objIndex.Insert(uuid + 3, NTaxi::NGraph2::TPoint{37.586798, 55.653567}));

        const auto& edgeId = objIndex.GetPosition(uuid).GetEdgeId();

        TestContinueSearchCallback<TTestForwardSearchTraits> continueSearchCallback;

        TTestFastDijkstraEdgeSearcher<TTestForwardSearchTraits, TestContinueSearchCallback<TTestForwardSearchTraits>> searcher(graph, TEST_SETTINGS, objIndex, continueSearchCallback);

        // Init search and first ContinueSearch()
        auto stopReason = searcher.Search(edgeId);
        UNIT_ASSERT_EQUAL(stopReason, NTaxi::NGraphSearch2::EStopReason::ByUser);
        UNIT_ASSERT(continueSearchCallback.lastFoundEdges);
        auto edgeId1 = continueSearchCallback.lastFoundEdges->begin()->first;
        Cout << "Search! StartEdge: " << edgeId << Endl;
        for (auto it = continueSearchCallback.lastFoundEdges->begin(); it != continueSearchCallback.lastFoundEdges->end(); ++it) {
            Cout << "EdgeId: " << it->first.value() << Endl;
        }

        // Second ContinueSearch()
        stopReason = searcher.ContinueSearch();
        UNIT_ASSERT_EQUAL(stopReason, NTaxi::NGraphSearch2::EStopReason::ByUser);
        UNIT_ASSERT(continueSearchCallback.lastFoundEdges);
        auto edgeId2 = continueSearchCallback.lastFoundEdges->begin()->first;
        Cout << "ContinueSearch!" << Endl;
        for (auto it = continueSearchCallback.lastFoundEdges->begin(); it != continueSearchCallback.lastFoundEdges->end(); ++it) {
            Cout << "EdgeId: " << it->first.value() << Endl;
        }

        // Check that search finds different edges
        UNIT_ASSERT(edgeId1 != edgeId2);

        // Here the search stops due to reaching the stop conditions
        stopReason = searcher.ContinueSearch();
        UNIT_ASSERT_EQUAL(stopReason,  NTaxi::NGraphSearch2::EStopReason::Done);
    } // Y_UNIT_TEST(TestContinueSearch)

    Y_UNIT_TEST(TestObjectRulesStopImmediately) {
        const auto& graph = GetTestGraph(TWithEdgeStorage::Yes);
        const auto& uuid = 1ull;
        TTestObjectIndex objIndex(graph);
        UNIT_ASSERT(objIndex.Insert(uuid, NTaxi::NGraph2::TPoint{37.676062, 55.748181}));

        const auto& edgeId = objIndex.GetPosition(uuid).GetEdgeId();

        TestImmediateStopCallback foundCallback;
        TTestFastDijkstraEdgeSearcher<TTestForwardSearchTraits, TestImmediateStopCallback> searcher(graph, TEST_SETTINGS, objIndex, foundCallback);
        searcher.Search(edgeId);

        UNIT_ASSERT(searcher.Searcher.GetVisitedEdgesCount() <= 1);
    } // Y_UNIT_TEST(TestObjectRulesStopImmediately)

    Y_UNIT_TEST(TestCountObjectsOnlyOnce) {
        TGraph graph{CreateCycleGraph()};
        graph.BuildEdgeStorage(5);
        TPersistentIndex index{CreateCyclePersistentIndex()};
        TJams jams(index);

        const auto& uuid = 1ull;
        const auto& positionsOnEdge = std::vector<TPositionOnEdge>{
            {0_eid, 0.5},
            {0_eid, 0.0},
            {0_eid, 1.0},
        };
        // forward
        size_t caseNum{0};
        for (const auto& posOnEdge : positionsOnEdge) {
            Cout << "Case number: " << caseNum << Endl;
            caseNum++;

            TTestObjectIndex objIndex(graph);
            objIndex.Insert(uuid, posOnEdge);

            TTestCallback<TTestForwardSearchTraits> foundCallback;
            TTestFastDijkstraEdgeSearcher<TTestForwardSearchTraits, TTestCallback<TTestForwardSearchTraits>> searcher(graph, TEST_SETTINGS, objIndex, foundCallback);
            searcher.Search(posOnEdge);

            UNIT_ASSERT_EQUAL(foundCallback.GetUniqueEdgeIds().size(), 1);
        }
        // reverse
        for (const auto& posOnEdge : positionsOnEdge) {
            TTestObjectIndex objIndex(graph);
            objIndex.Insert(uuid, posOnEdge);

            TTestCallback<TTestReverseSearchTraits> foundCallback;
            TTestFastDijkstraEdgeSearcher<TTestReverseSearchTraits, TTestCallback<TTestReverseSearchTraits>> searcher(graph, TEST_SETTINGS, objIndex, foundCallback);
            searcher.Search(posOnEdge);

            UNIT_ASSERT_EQUAL(foundCallback.GetUniqueEdgeIds().size(), 1);
        }
    } // Y_UNIT_TEST(TestCountObjectsOnlyOnce)

    Y_UNIT_TEST(TestObjectRulesEmptyJams) {
        TGraph graph{CreateRhombusGraph()};
        graph.BuildEdgeStorage(5);
        TPersistentIndex index{CreateRhombusPersistentIndex()};
        TJams jams(index);

        const auto& uuid = 1ull;
        TTestObjectIndex objIndex(graph);
        objIndex.Insert(uuid, TPositionOnEdge{3_eid, 0.5});
        objIndex.Insert(uuid + 1, TPositionOnEdge{4_eid, 0.5});

        TTestCallback<TTestForwardSearchTraits> foundCallback;
        TTestFastDijkstraEdgeSearcher<TTestForwardSearchTraits, TTestCallback<TTestForwardSearchTraits>> searcher(graph, TEST_SETTINGS, objIndex, foundCallback);
        searcher.Search(0_eid);

        std::vector<TId> res{3_eid, 4_eid};
        std::vector<double> expWeights{3, 1};
        UNIT_ASSERT_EQUAL(foundCallback.GetEdgeIds(), res);
        UNIT_ASSERT_EQUAL(foundCallback.GetEdgeWeights(), expWeights);
    } // Y_UNIT_TEST(TestObjectRulesEmptyJams)

    Y_UNIT_TEST(TestObjectRulesStartFromPositionOnEdge) {
        TGraph graph{CreateGiantRhombusGraph()};
        graph.BuildEdgeStorage(5);
        TPersistentIndex index{CreateRhombusPersistentIndex()};
        TJams jams(index);

        const auto& uuid = 1ull;
        TTestObjectIndex objIndex(graph);
        objIndex.Insert(uuid, TPositionOnEdge{3_eid, 0.5});
        objIndex.Insert(uuid + 1, TPositionOnEdge{4_eid, 0.5});

        TTestCallback<TTestForwardSearchTraits> foundCallback;
        TTestFastDijkstraEdgeSearcher<TTestForwardSearchTraits, TTestCallback<TTestForwardSearchTraits>> searcher(graph, TEST_SETTINGS, objIndex, foundCallback);
        searcher.Search(TPositionOnEdge{0_eid, 0.5});

        std::vector<TId> res{3_eid, 4_eid};
        std::vector<double> expDistancesFromStart{1500, 2500};
        UNIT_ASSERT_EQUAL(foundCallback.GetEdgeIds(), res);
        UNIT_ASSERT_EQUAL(foundCallback.GetDistancesFromStart(), expDistancesFromStart);
        Cout << "uuid 1 distance: " << foundCallback.GetDistancesToObjects()[uuid] << Endl;
        Cout << "uuid 2 distance: " << foundCallback.GetDistancesToObjects()[uuid + 1] << Endl;
        UNIT_ASSERT_EQUAL(foundCallback.GetDistancesToObjects()[uuid], 3000);
        UNIT_ASSERT_EQUAL(foundCallback.GetDistancesToObjects()[uuid + 1], 3000);
    } // Y_UNIT_TEST(TestObjectRulesStartFromPositionOnEdge)

    Y_UNIT_TEST(TestObjectRulesStartFromPositionOnEdgeReverse) {
        TGraph graph{CreateGiantRhombusGraphReversed()};
        graph.BuildEdgeStorage(5);
        TPersistentIndex index{CreateRhombusPersistentIndex()};
        TJams jams(index);

        const auto& uuid = 1ull;
        TTestObjectIndex objIndex(graph);
        objIndex.Insert(uuid, TPositionOnEdge{3_eid, 0.5});
        objIndex.Insert(uuid + 1, TPositionOnEdge{4_eid, 0.5});

        TTestCallback<TTestReverseSearchTraits> foundCallback;
        TTestFastDijkstraEdgeSearcher<TTestReverseSearchTraits, TTestCallback<TTestReverseSearchTraits>> searcher(graph, TEST_SETTINGS, objIndex, foundCallback);
        searcher.Search(TPositionOnEdge{0_eid, 0.5});

        std::vector<TId> res{3_eid, 4_eid};
        std::vector<double> expDistancesFromStart{1500, 2500};
        UNIT_ASSERT_EQUAL(foundCallback.GetEdgeIds(), res);
        UNIT_ASSERT_EQUAL(foundCallback.GetDistancesFromStart(), expDistancesFromStart);
        Cout << "uuid 1 distance: " << foundCallback.GetDistancesToObjects()[uuid] << Endl;
        Cout << "uuid 2 distance: " << foundCallback.GetDistancesToObjects()[uuid + 1] << Endl;
        UNIT_ASSERT_EQUAL(foundCallback.GetDistancesToObjects()[uuid], 3000);
        UNIT_ASSERT_EQUAL(foundCallback.GetDistancesToObjects()[uuid + 1], 3000);
    } // Y_UNIT_TEST(TestObjectRulesStartFromPositionOnEdgeReverse)

    Y_UNIT_TEST(TestObjectRulesStartSameEdge) {
        TGraph graph{CreateGiantCycleGraph()};
        graph.BuildEdgeStorage(5);
        TPersistentIndex index{CreateCyclePersistentIndex()};
        TJams jams(index);

        const auto& uuid = 1ull;
        TTestObjectIndex objIndex(graph);
        objIndex.Insert(uuid, TPositionOnEdge{0_eid, 0.1});
        objIndex.Insert(uuid + 1, TPositionOnEdge{0_eid, 0.6});
        objIndex.Insert(uuid + 2, TPositionOnEdge{2_eid, 0.4});

        TTestCallback<TTestForwardSearchTraits> foundCallback;
        TTestFastDijkstraEdgeSearcher<TTestForwardSearchTraits, TTestCallback<TTestForwardSearchTraits>> searcher(graph, TEST_SETTINGS, objIndex, foundCallback);
        searcher.Search(TPositionOnEdge{0_eid, 0.3});

        Cout << "uuid 1 distance: " << foundCallback.GetDistancesToObjects()[uuid] << Endl;
        Cout << "uuid 2 distance: " << foundCallback.GetDistancesToObjects()[uuid + 1] << Endl;
        Cout << "uuid 3 distance: " << foundCallback.GetDistancesToObjects()[uuid + 2] << Endl;
        UNIT_ASSERT_DOUBLES_EQUAL(foundCallback.GetDistancesToObjects()[uuid], 2800, 1e-2);
        UNIT_ASSERT_DOUBLES_EQUAL(foundCallback.GetDistancesToObjects()[uuid + 1], 300, 1e-2);
        UNIT_ASSERT_DOUBLES_EQUAL(foundCallback.GetDistancesToObjects()[uuid + 2], 2100, 1e-2);
    } // Y_UNIT_TEST(TestObjectRulesStartSameEdge)

    /// Same, but on small cycle, with edge length == 1. This will test
    /// that we don't loose precision due to fringe being unsigned-int-based
    Y_UNIT_TEST(TestObjectRulesStartSameEdge2) {
        TGraph graph{CreateCycleGraph()};
        graph.BuildEdgeStorage(5);
        TPersistentIndex index{CreateCyclePersistentIndex()};
        TJams jams(index);

        const auto& uuid = 1ull;
        TTestObjectIndex objIndex(graph);
        objIndex.Insert(uuid, TPositionOnEdge{0_eid, 0.1});
        objIndex.Insert(uuid + 1, TPositionOnEdge{0_eid, 0.6});
        objIndex.Insert(uuid + 2, TPositionOnEdge{2_eid, 0.4});

        TTestCallback<TTestForwardSearchTraits> foundCallback;
        TTestFastDijkstraEdgeSearcher<TTestForwardSearchTraits, TTestCallback<TTestForwardSearchTraits>> searcher(graph, TEST_SETTINGS, objIndex, foundCallback);
        searcher.Search(TPositionOnEdge{0_eid, 0.3});

        Cout << "uuid 1 distance: " << foundCallback.GetDistancesToObjects()[uuid] << Endl;
        Cout << "uuid 2 distance: " << foundCallback.GetDistancesToObjects()[uuid + 1] << Endl;
        Cout << "uuid 3 distance: " << foundCallback.GetDistancesToObjects()[uuid + 2] << Endl;
        UNIT_ASSERT_DOUBLES_EQUAL(foundCallback.GetDistancesToObjects()[uuid], 2.8, 1e-2);
        UNIT_ASSERT_DOUBLES_EQUAL(foundCallback.GetDistancesToObjects()[uuid + 1], 0.3, 1e-2);
        UNIT_ASSERT_DOUBLES_EQUAL(foundCallback.GetDistancesToObjects()[uuid + 2], 2.1, 1e-2);
    } // Y_UNIT_TEST(TestObjectRulesStartSameEdge2)

    Y_UNIT_TEST(TestObjectRulesStartSameEdgeReverse) {
        TGraph graph{CreateGiantCycleGraph()};
        graph.BuildEdgeStorage(5);
        TPersistentIndex index{CreateCyclePersistentIndex()};
        TJams jams(index);

        const auto& uuid = 1ull;
        TTestObjectIndex objIndex(graph);
        objIndex.Insert(uuid, TPositionOnEdge{0_eid, 0.1});
        objIndex.Insert(uuid + 1, TPositionOnEdge{0_eid, 0.6});
        objIndex.Insert(uuid + 2, TPositionOnEdge{2_eid, 0.4});

        TTestCallback<TTestReverseSearchTraits> foundCallback;
        TTestFastDijkstraEdgeSearcher<TTestReverseSearchTraits, TTestCallback<TTestReverseSearchTraits>> searcher(graph, TEST_SETTINGS, objIndex, foundCallback);
        searcher.Search(TPositionOnEdge{0_eid, 0.3});

        Cout << "uuid 1 distance: " << foundCallback.GetDistancesToObjects()[uuid] << Endl;
        Cout << "uuid 1 distance: " << foundCallback.GetDistancesToObjects()[uuid] << Endl;
        Cout << "uuid 2 distance: " << foundCallback.GetDistancesToObjects()[uuid + 1] << Endl;
        Cout << "uuid 3 distance: " << foundCallback.GetDistancesToObjects()[uuid + 2] << Endl;
        UNIT_ASSERT_DOUBLES_EQUAL(foundCallback.GetDistancesToObjects()[uuid], 200, 1e-2); // should be 200, but lost 1 to rounding error
        UNIT_ASSERT_DOUBLES_EQUAL(foundCallback.GetDistancesToObjects()[uuid + 1], 2700, 1e-2);
        UNIT_ASSERT_DOUBLES_EQUAL(foundCallback.GetDistancesToObjects()[uuid + 2], 900, 1e-2);
    } // Y_UNIT_TEST(TestObjectRulesStartSameEdgeReverse)

    Y_UNIT_TEST(TestObjectRulesStartFromClosedByClosureEdge) {
        TGraph graph{CreateRhombusGraph()};
        graph.BuildEdgeStorage(5);
        TPersistentIndex index{CreateRhombusPersistentIndex()};
        const auto& now = std::chrono::system_clock::now();
        const auto& some_future_moment = now + std::chrono::hours(10);
        const auto& some_past_moment = now - std::chrono::hours(10);
        TClosures closures(index, now);

        const auto& uuid = 1ull;
        TTestObjectIndex objIndex(graph);
        objIndex.Insert(uuid, TPositionOnEdge{3_eid, 0.5});
        objIndex.Insert(uuid + 1, TPositionOnEdge{4_eid, 0.5});

        // add closure to 0 and 1 edge
        const int kRegion = 0;
        closures.AddClosure(0_eid, kRegion, some_past_moment, some_future_moment);
        closures.AddClosure(1_eid, kRegion, some_past_moment, some_future_moment);

        UNIT_ASSERT(closures.IsClosedAtMoment(0_eid, now));
        UNIT_ASSERT(closures.IsClosedAtMoment(1_eid, now));

        TTestCallback<TTestForwardSearchTraits> foundCallback;
        TTestFastDijkstraEdgeSearcher<TTestForwardSearchTraits, TTestCallback<TTestForwardSearchTraits>> searcher(graph, TEST_SETTINGS, objIndex, foundCallback, nullptr, &closures);
        searcher.Search(0_eid);

        // because closures on start edges 0 and 1 not considered,
        // that's why we found all drivers like without closures.
        UNIT_ASSERT_DOUBLES_EQUAL(foundCallback.GetDistancesToObjects()[uuid], 2.5, 1e-2);
        UNIT_ASSERT_DOUBLES_EQUAL(foundCallback.GetDistancesToObjects()[uuid + 1], 2.5, 1e-2);
    } // Y_UNIT_TEST(TestObjectRulesStartFromClosedByClosureEdge)

    Y_UNIT_TEST(TestObjectRulesWithYards) {
        TGraph graph{CreateRhombusGraphWithPasses()};
        graph.BuildEdgeStorage(5);
        TPersistentIndex index{CreateRhombusPersistentIndex()};

        const auto& uuid = 1ull;
        TTestObjectIndex objIndex(graph);

        objIndex.Insert(uuid, TPositionOnEdge{2_eid, 0.5});
        objIndex.Insert(uuid + 1, TPositionOnEdge{5_eid, 0.5});

        // Both drivers in yards
        {
            TTestCallback<TTestForwardSearchTraits> foundCallback;
            TTestFastDijkstraEdgeSearcher<TTestForwardSearchTraits, TTestCallback<TTestForwardSearchTraits>> searcher(graph, TEST_SETTINGS, objIndex, foundCallback);
            searcher.Search(2_eid);

            const TVector<TId> expectedRes{2_eid, 5_eid};
            const auto& res = foundCallback.GetEdgeIds();
            UNIT_ASSERT_EQUAL(res, expectedRes);

            const auto& stats = searcher.Searcher.GetStatistics();
            // we started from yard, so this yard is not counted
            UNIT_ASSERT_EQUAL(1u, stats.YardsVisitedCount);
            UNIT_ASSERT_EQUAL(0u, stats.YardsSkippedCount);
        }

        // Remove driver from from edge 5
        objIndex.Remove(uuid + 1);
        {
            TTestCallback<TTestForwardSearchTraits> foundCallback;
            TTestFastDijkstraEdgeSearcher<TTestForwardSearchTraits, TTestCallback<TTestForwardSearchTraits>> searcher(graph, TEST_SETTINGS, objIndex, foundCallback);
            searcher.Search(2_eid);

            const TVector<TId> expectedRes{2_eid};
            const auto& res = foundCallback.GetEdgeIds();
            UNIT_ASSERT_EQUAL(res, expectedRes);

            const auto& stats = searcher.Searcher.GetStatistics();
            // we started from yard, so this yard no counted
            UNIT_ASSERT_EQUAL(0u, stats.YardsVisitedCount);
            // skip yard without any drivers
            UNIT_ASSERT_EQUAL(1u, stats.YardsSkippedCount);
        }
    } // Y_UNIT_TEST(TestObjectRulesWithYards)

    Y_UNIT_TEST(TestObjectRulesLooseFieldRoad) {
        TGraph graph{CreateRhombusGraphWithFieldRoad()};

        const auto& uuid = 1ull;
        TObjectIndex<ui64> objIndex(graph);

        objIndex.Insert(uuid, TPositionOnEdge{1_eid, 0.5});

        TTestCallback<TTestReverseSearchTraits> foundCallback;
        TTestFastDijkstraEdgeSearcher<TTestReverseSearchTraits, TTestCallback<TTestReverseSearchTraits>> searcher(graph, TEST_SETTINGS, objIndex, foundCallback);
        searcher.Search(5_eid);

        // Should find the driver because field road must be labeled as yard
        const TVector<TId> expectedRes{1_eid};
        const auto& res = foundCallback.GetEdgeIds();
        UNIT_ASSERT_EQUAL(res, expectedRes);

        const auto& stats = searcher.Searcher.GetStatistics();
        UNIT_ASSERT_EQUAL(0u, stats.YardsVisitedCount);
        UNIT_ASSERT_EQUAL(0u, stats.YardsSkippedCount);
    } // Y_UNIT_TEST(TestObjectRulesLooseFieldRoad)

    Y_UNIT_TEST(TestObjectRulesFieldBetweenHighways) {
        TGraph graph{CreateGraphWithFieldBetweenStreets()};

        const auto& uuid = 1ull;
        TObjectIndex<ui64> objIndex(graph);

        objIndex.Insert(uuid, TPositionOnEdge{0_eid, 0.5});

        TTestCallback<TTestReverseSearchTraits> foundCallback;
        TTestFastDijkstraEdgeSearcher<TTestReverseSearchTraits, TTestCallback<TTestReverseSearchTraits>> searcher(graph, TEST_SETTINGS, objIndex, foundCallback);
        searcher.Search({5_eid, 0.5});

        // Should find the driver because field road is not part of yard now
        const TVector<TId> expectedRes{0_eid};
        const auto& res = foundCallback.GetEdgeIds();
        UNIT_ASSERT_EQUAL(res, expectedRes);

        const auto& stats = searcher.Searcher.GetStatistics();
        // Yard must be skipped because it is empty
        UNIT_ASSERT_EQUAL(0u, stats.YardsVisitedCount);
        UNIT_ASSERT_EQUAL(1u, stats.YardsSkippedCount);
    } // Y_UNIT_TEST(TestObjectRulesFieldBetweenHighways)

    Y_UNIT_TEST(TestObjectRulesFieldBetweenYards) {
        TGraph graph{CreateGraphWithFieldBetweenYards()};

        const auto& uuid = 1ull;
        TObjectIndex<ui64> objIndex(graph);

        objIndex.Insert(uuid, TPositionOnEdge{0_eid, 0.5});
        objIndex.Insert(uuid + 1, TPositionOnEdge{5_eid, 0.5});

        {
            TTestCallback<TTestReverseSearchTraits> foundCallback;
            TTestFastDijkstraEdgeSearcher<TTestReverseSearchTraits, TTestCallback<TTestReverseSearchTraits>> searcher(graph, TEST_SETTINGS, objIndex, foundCallback);

            searcher.Search({4_eid, 0.5});

            // Shouldn't find anybody because an empty yard is on the way, field is not part of the yard
            const auto& res = foundCallback.GetEdgeIds();
            UNIT_ASSERT_EQUAL(res.size(), 0);

            const auto& stats = searcher.Searcher.GetStatistics();
            // Yard must be skipped because it is empty
            UNIT_ASSERT_EQUAL(0u, stats.YardsVisitedCount);
            UNIT_ASSERT_EQUAL(1u, stats.YardsSkippedCount);
        }
        {
            TTestCallback<TTestReverseSearchTraits> foundCallback;
            TTestFastDijkstraEdgeSearcher<TTestReverseSearchTraits, TTestCallback<TTestReverseSearchTraits>> searcher(graph, TEST_SETTINGS, objIndex, foundCallback);

            searcher.Search({3_eid, 0.5});

            // Now should find both drivers because starting from yard
            const auto& res = foundCallback.GetEdgeIds();
            UNIT_ASSERT_EQUAL(res.size(), 2);

            const auto& stats = searcher.Searcher.GetStatistics();
            // Yard must be visited
            UNIT_ASSERT_EQUAL(1u, stats.YardsVisitedCount);
            UNIT_ASSERT_EQUAL(0u, stats.YardsSkippedCount);
        }
    } // Y_UNIT_TEST(TestObjectRulesFieldBetweenYards)

    Y_UNIT_TEST(TestObjectRulesLeewayCounting) {
        TGraph graph{CreateRhombusGraphReversed()};
        graph.BuildEdgeStorage(5);
        TPersistentIndex index{CreateRhombusPersistentIndex()};
        const auto& now = std::chrono::system_clock::now();
        NTaxi::NGraph2::TClosures closures(index, now);

        const auto& uuid = 1ull;
        // One driver on each edge, needed for OnFoundObjects to be called at every edge
        TTestObjectIndex objIndex(graph);
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

        const i32 INF = NTaxi::NGraphSearch2::NFastDijkstraDetail::INF_LEEWAY;

        // Test with enabled leeway counting
        {
            TTestCallback<TTestReverseSearchTraitsLeewayEnable> foundCallback;
            TTestFastDijkstraEdgeSearcher<TTestReverseSearchTraitsLeewayEnable, TTestCallback<TTestReverseSearchTraitsLeewayEnable>> searcher(graph, TEST_SETTINGS, objIndex, foundCallback, nullptr, &closures);
            searcher.Search(0_eid);

            const auto actualLeeways = foundCallback.GetEdgeLeeways();
            for (auto [k, v] : actualLeeways)
                std::cout << k << ' ' << v << '\n';

            std::unordered_map<TId, i32> expectedLeeways = {{0_eid, INF}, {1_eid, INF}, {2_eid, 0}, {3_eid, 1}, {4_eid, -1}, {5_eid, -2}};
            UNIT_ASSERT_EQUAL(foundCallback.GetEdgeLeeways(), expectedLeeways);
        }
        // Test with disabled leeway counting, all leeways must be INF
        {
            TTestCallback<TTestReverseSearchTraits> foundCallback;
            TTestFastDijkstraEdgeSearcher<TTestReverseSearchTraits, TTestCallback<TTestReverseSearchTraits>> searcher(graph, TEST_SETTINGS, objIndex, foundCallback, nullptr, &closures);
            searcher.Search(0_eid);

            const auto actualLeeways = foundCallback.GetEdgeLeeways();

            std::unordered_map<TId, i32> expectedLeeways = {{0_eid, INF}, {1_eid, INF}, {2_eid, INF}, {3_eid, INF}, {4_eid, INF}, {5_eid, INF}};
            UNIT_ASSERT_EQUAL(foundCallback.GetEdgeLeeways(), expectedLeeways);
        }
    } // Y_UNIT_TEST(TestObjectRulesLeewayCounting)

    Y_UNIT_TEST(TestObjectRulesLeewayCountStartFromClosure) {
        TGraph graph{BuildGraphForDijkstraFromWikipedia()};
        graph.BuildEdgeStorage(10);
        TPersistentIndex index{CreatePersistentIndexForGraphFromWikipedia()};
        const auto& now = std::chrono::system_clock::now();
        TClosures closures(index, now);

        const auto& uuid = 1ull;
        // One driver on each edge, needed for OnFoundObjects to be called at every edge
        TTestObjectIndex objIndex(graph);
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

        TTestCallback<TTestReverseSearchTraitsLeewayEnable> foundCallback;
        TTestFastDijkstraEdgeSearcher<TTestReverseSearchTraitsLeewayEnable, TTestCallback<TTestReverseSearchTraitsLeewayEnable>> searcher(graph, TEST_SETTINGS, objIndex, foundCallback, nullptr, &closures);
        searcher.Search(9_eid);

        const i32 INF = NTaxi::NGraphSearch2::NFastDijkstraDetail::INF_LEEWAY;
        const auto actualLeeways = foundCallback.GetEdgeLeeways();

        std::unordered_map<TId, i32> expectedLeeways = {{0_eid, -5}, {1_eid, -4}, {2_eid, -5}, {3_eid, INF}, {4_eid, INF}, {7_eid, INF}, {9_eid, INF}};

        for (auto [k, v] : expectedLeeways)
            std::cout << k << ' ' << v << '\n';
        std::cout << '\n';
        for (auto [k, v] : actualLeeways)
            std::cout << k << ' ' << v << '\n';

        std::cout << std::endl;
        UNIT_ASSERT_EQUAL(foundCallback.GetEdgeLeeways(), expectedLeeways);
    } // Y_UNIT_TEST(TestObjectRulesLeewayCountStartFromClosure)

    Y_UNIT_TEST(TestObjectRulesLeewayCountChainOfClosuresWithBeginningInStartAndOpenedAdjacentEdge) {
        ///
        /// Part of graph around start edge looks like this
        ///                          .
        ///                          .
        ///                          .
        ///                          |
        ///                          |
        ///                          |
        ///                          | (Closed edge)
        ///                          |
        ///                          |
        ///                          v
        ///    ...---------X-------->*---------X-------->...
        ///          (Closed edge)       (Closed edge)
        ///                           (Start search here)
        ///
        ///
        /// In this case, we should say that leeways of next not closed edges are INF
        ///

        TGraph graph{BuildGraphForDijkstraFromWikipedia()};
        graph.BuildEdgeStorage(10);
        TPersistentIndex index{CreatePersistentIndexForGraphFromWikipedia()};
        const auto& now = std::chrono::system_clock::now();
        TClosures closures(index, now);

        const auto& uuid = 1ull;
        // One driver on each edge, needed for OnFoundObjects to be called at every edge
        TTestObjectIndex objIndex(graph);
        for (size_t i = 0; i < 10; ++i) {
            objIndex.Insert(uuid + i, TPositionOnEdge{TEdgeId(i), 0.5});
        }
        // add closure to edges
        const int kRegion = 0;
        closures.AddClosure(9_eid, kRegion, now - std::chrono::seconds(10), now + std::chrono::seconds(5));
        closures.AddClosure(7_eid, kRegion, now - std::chrono::seconds(10), now + std::chrono::seconds(5));
        closures.AddClosure(3_eid, kRegion, now - std::chrono::seconds(10), now + std::chrono::seconds(5));

        TTestCallback<TTestReverseSearchTraitsLeewayEnable> foundCallback;
        TTestFastDijkstraEdgeSearcher<TTestReverseSearchTraitsLeewayEnable, TTestCallback<TTestReverseSearchTraitsLeewayEnable>> searcher(graph, TEST_SETTINGS, objIndex, foundCallback, nullptr, &closures);
        searcher.Search(9_eid);

        const i32 INF = NTaxi::NGraphSearch2::NFastDijkstraDetail::INF_LEEWAY;
        const auto actualLeeways = foundCallback.GetEdgeLeeways();

        std::unordered_map<TId, i32> expectedLeeways = {{0_eid, INF}, {1_eid, INF}, {2_eid, INF}, {3_eid, INF}, {4_eid, INF}, {7_eid, INF}, {9_eid, INF}};

        for (auto [k, v] : expectedLeeways)
            std::cout << k << ' ' << v << '\n';
        std::cout << '\n';
        for (auto [k, v] : actualLeeways)
            std::cout << k << ' ' << v << '\n';

        std::cout << std::endl;
        UNIT_ASSERT_EQUAL(foundCallback.GetEdgeLeeways(), expectedLeeways);
    } // Y_UNIT_TEST(TestObjectRulesLeewayCountChainOfClosuresWithBeginningInStartAndOpenedAdjacentEdge)

    Y_UNIT_TEST(TestObjectRulesLeewayCountOnlyStartEdgeWithClosureReachable) {
        ///
        /// Part of graph around start edge looks like this
        ///                          .
        ///                          .
        ///                          .
        ///                          |
        ///                          |
        ///                          |
        ///                          X (Closed edge)
        ///                          |
        ///                          |
        ///                          |
        ///                          v
        ///    ...---------X-------->*----------------->...
        ///          (Closed edge)    (Not closed edge yet)
        ///                           (Start search here)
        ///
        ///
        /// In this case, we should say that there is leeway only for start edge and its equals to initial number
        ///

        TGraph graph{BuildGraphForDijkstraFromWikipedia()};
        graph.BuildEdgeStorage(10);
        TPersistentIndex index{CreatePersistentIndexForGraphFromWikipedia()};
        const auto& now = std::chrono::system_clock::now();
        TClosures closures(index, now);

        const auto& uuid = 1ull;
        // One driver on each edge, needed for OnFoundObjects to be called at every edge
        TTestObjectIndex objIndex(graph);
        for (size_t i = 0; i < 10; ++i) {
            objIndex.Insert(uuid + i, TPositionOnEdge{TEdgeId(i), 0.5});
        }
        // add closure to edges
        const int kRegion = 0;
        const i32 leeway = 10;
        closures.AddClosure(9_eid, kRegion, now + std::chrono::seconds(leeway), now + std::chrono::seconds(leeway + 15));
        closures.AddClosure(7_eid, kRegion, now - std::chrono::seconds(10), now + std::chrono::seconds(5));
        closures.AddClosure(3_eid, kRegion, now - std::chrono::seconds(10), now + std::chrono::seconds(5));

        TTestCallback<TTestReverseSearchTraitsLeewayEnable> foundCallback;
        TTestFastDijkstraEdgeSearcher<TTestReverseSearchTraitsLeewayEnable, TTestCallback<TTestReverseSearchTraitsLeewayEnable>> searcher(graph, TEST_SETTINGS, objIndex, foundCallback, nullptr, &closures);
        searcher.Search(9_eid);

        const auto actualLeeways = foundCallback.GetEdgeLeeways();

        std::unordered_map<TId, i32> expectedLeeways = {{9_eid, leeway}};

        for (auto [k, v] : expectedLeeways)
            std::cout << k << ' ' << v << '\n';
        std::cout << '\n';
        for (auto [k, v] : actualLeeways)
            std::cout << k << ' ' << v << '\n';

        std::cout << std::endl;
        UNIT_ASSERT_EQUAL(foundCallback.GetEdgeLeeways(), expectedLeeways);
    } // Y_UNIT_TEST(TestObjectRulesLeewayCountOnlyStartEdgeWithClosureReachable)

    Y_UNIT_TEST(TestObjectRulesLeewayCountStartFromFutureClosure) {
        TGraph graph{CreateRhombusGraphReversed()};
        graph.BuildEdgeStorage(5);
        TPersistentIndex index{CreateRhombusPersistentIndex()};
        const auto& now = std::chrono::system_clock::now();
        TClosures closures(index, now);

        const auto& uuid = 1ull;
        // One driver on each edge, needed for OnFoundObjects to be called at every edge
        TTestObjectIndex objIndex(graph);
        objIndex.Insert(uuid, TPositionOnEdge{0_eid, 0.5});
        objIndex.Insert(uuid + 1, TPositionOnEdge{1_eid, 0.5});
        objIndex.Insert(uuid + 2, TPositionOnEdge{2_eid, 0.5});
        objIndex.Insert(uuid + 3, TPositionOnEdge{3_eid, 0.5});
        objIndex.Insert(uuid + 4, TPositionOnEdge{4_eid, 0.5});
        objIndex.Insert(uuid + 5, TPositionOnEdge{5_eid, 0.5});
        // add closure to edges
        const int kRegion = 0;
        const i32 leeway = 10;
        closures.AddClosure(0_eid, kRegion, now + std::chrono::seconds(leeway), now + std::chrono::seconds(leeway + 15));

        TTestCallback<TTestReverseSearchTraitsLeewayEnable> foundCallback;
        TTestFastDijkstraEdgeSearcher<TTestReverseSearchTraitsLeewayEnable, TTestCallback<TTestReverseSearchTraitsLeewayEnable>> searcher(graph, TEST_SETTINGS, objIndex, foundCallback, nullptr, &closures);
        searcher.Search(0_eid);

        const auto actualLeeways = foundCallback.GetEdgeLeeways();

        std::unordered_map<TId, i32> expectedLeeways = {{0_eid, leeway}, {1_eid, leeway - 1}, {2_eid, leeway - 2}, {3_eid, leeway - 1 - 3}, {4_eid, leeway - 2 - 1}, {5_eid, leeway - 2 - 1 - 1}};

        for (auto [k, v] : expectedLeeways)
            std::cout << k << ' ' << v << '\n';
        std::cout << '\n';
        for (auto [k, v] : actualLeeways)
            std::cout << k << ' ' << v << '\n';

        std::cout << std::endl;
        UNIT_ASSERT_EQUAL(foundCallback.GetEdgeLeeways(), expectedLeeways);
    } // Y_UNIT_TEST(TestObjectRulesLeewayCountStartFromFutureClosure)

    struct TRouteInfoTestCase {
        TPositionOnEdge Position;
        std::optional<NTaxi::NGraphSearch2::TRouteInfo> ExpectedRouteInfo;
    };

    // This one goies in REVERSE
    Y_UNIT_TEST(TestObjectRulesGetRouteInfoCase1) {
        TGraph graph{CreateGiantCycleGraph()};
        graph.BuildEdgeStorage(5);
        TPersistentIndex index{CreateCyclePersistentIndex()};
        TJams jams(index);

        auto createRouteInfo = [](double distance) {
            return NTaxi::NGraphSearch2::TRouteInfo{TDistance{distance}};
        };

        // Remember - REVERSE search
        std::vector<TRouteInfoTestCase> cases = {
            {TPositionOnEdge{0_eid, 1.0}, createRouteInfo(2400)},
            {TPositionOnEdge{0_eid, .75}, createRouteInfo(2650)},
            {TPositionOnEdge{0_eid, 0.4}, createRouteInfo(0)},
            {TPositionOnEdge{0_eid, 0.15}, createRouteInfo(250)},
            {TPositionOnEdge{0_eid, 0.0}, createRouteInfo(400)},
            {TPositionOnEdge{2_eid, 1.0}, createRouteInfo(400)},
            {TPositionOnEdge{2_eid, .75}, createRouteInfo(650)},
            {TPositionOnEdge{2_eid, 0.5}, createRouteInfo(900)},
            {TPositionOnEdge{2_eid, 0.25}, createRouteInfo(1150)},
            {TPositionOnEdge{2_eid, 0.0}, createRouteInfo(1400)},
            {TPositionOnEdge{1_eid, 1.0}, createRouteInfo(1400)},
            {TPositionOnEdge{1_eid, 0.5}, createRouteInfo(1900)},
            {TPositionOnEdge{1_eid, 0.0}, createRouteInfo(2400)},
        };

        TTestObjectIndex objIndex(graph);

        for (size_t uuid = 0; uuid < cases.size(); ++uuid) {
            const auto& test_case = cases[uuid];
            objIndex.Insert(uuid, test_case.Position);
        }

        TTestCallback<TTestReverseSearchTraits> foundCallback;
        TTestFastDijkstraEdgeSearcher<TTestReverseSearchTraits, TTestCallback<TTestReverseSearchTraits>> searcher(graph, TEST_SETTINGS, objIndex, foundCallback);
        searcher.Search(TPositionOnEdge{0_eid, 0.4});

        for (size_t uuid = 0; uuid < cases.size(); ++uuid) {
            const auto& test_case = cases[uuid];
            auto fit = foundCallback.GetRouteInfos().find(uuid);
            UNIT_ASSERT(fit != foundCallback.GetRouteInfos().end());
            UNIT_ASSERT(fit->second == test_case.ExpectedRouteInfo);
            UNIT_ASSERT_DOUBLES_EQUAL(foundCallback.GetDistancesToObjects()[uuid], test_case.ExpectedRouteInfo->PathLengthInMeters.value(), 1e-2);
        }
    } // Y_UNIT_TEST(TestObjectRulesGetRouteInfoCase1)

    Y_UNIT_TEST(TestRealtimeChangingSearchDistanceRestrictions) {
        TGraph graph{CreateGiantRhombusGraph()};
        graph.BuildEdgeStorage(5);

        TPositionOnEdge startPosition{5_eid, 0.5};

        const auto& uuid = 1ull;
        TObjectIndex<ui64> objIndex(graph);

        objIndex.Insert(uuid, TPositionOnEdge{0_eid, 0.5});
        objIndex.Insert(uuid + 1, TPositionOnEdge{2_eid, 0.5});
        objIndex.Insert(uuid + 2, TPositionOnEdge{4_eid, 0.5});

        TFastSearchSettings defaultSettings = TEST_SETTINGS;
        TFastSearchSettings zeroMaxDistanceSettings = TEST_SETTINGS;
        zeroMaxDistanceSettings.MaxDistance = TDistance(3000);
        TTestSettingsChangingCallback<TTestReverseSearchTraits> foundCallback;
        foundCallback.SetNewSettings(zeroMaxDistanceSettings);
        TTestFastDijkstraEdgeSearcher<TTestReverseSearchTraits, TTestSettingsChangingCallback<TTestReverseSearchTraits>> searcher(graph, defaultSettings, objIndex, foundCallback);
        searcher.Search(startPosition);

        UNIT_ASSERT(foundCallback.IsSettingsChanged() == true);
        UNIT_ASSERT(foundCallback.GetObjectCounter() == 2);

        foundCallback.Reset();
        TFastSearchSettings shortMaxDistanceSettings = TEST_SETTINGS;
        shortMaxDistanceSettings.MaxDistance = TDistance(3000);
        searcher.SetSearchSettings(shortMaxDistanceSettings);
        foundCallback.SetNewSettings(defaultSettings);
        searcher.Search(startPosition);

        UNIT_ASSERT(foundCallback.IsSettingsChanged() == false);
        UNIT_ASSERT(foundCallback.GetObjectCounter() == 2);
    } // Y_UNIT_TEST(TestRealtimeChangingSearchDistanceRestrictions)

    Y_UNIT_TEST(TestRealtimeChangingSearchTimeRestrictions) {
        TGraph graph{CreateGiantRhombusGraph()};
        graph.BuildEdgeStorage(5);

        TPositionOnEdge startPosition{5_eid, 0.5};

        const auto& uuid = 1ull;
        TObjectIndex<ui64> objIndex(graph);

        objIndex.Insert(uuid, TPositionOnEdge{0_eid, 0.5});
        objIndex.Insert(uuid + 1, TPositionOnEdge{2_eid, 0.5});
        objIndex.Insert(uuid + 2, TPositionOnEdge{4_eid, 0.5});

        TFastSearchSettings defaultSettings = TEST_SETTINGS;
        TFastSearchSettings zeroMaxTimeSettings = TEST_SETTINGS;
        zeroMaxTimeSettings.MaxTime = TTime(3000);
        TTestSettingsChangingCallback<TTestReverseSearchTraits> foundCallback;
        foundCallback.SetNewSettings(zeroMaxTimeSettings);
        TTestFastDijkstraEdgeSearcher<TTestReverseSearchTraits, TTestSettingsChangingCallback<TTestReverseSearchTraits>> searcher(graph, defaultSettings, objIndex, foundCallback);
        searcher.Search(startPosition);

        UNIT_ASSERT(foundCallback.IsSettingsChanged() == true);
        UNIT_ASSERT(foundCallback.GetObjectCounter() == 2);

        foundCallback.Reset();
        TFastSearchSettings shortMaxTimeSettings = TEST_SETTINGS;
        shortMaxTimeSettings.MaxTime = TTime(3000);
        searcher.SetSearchSettings(shortMaxTimeSettings);
        foundCallback.SetNewSettings(defaultSettings);
        searcher.Search(startPosition);

        UNIT_ASSERT(foundCallback.IsSettingsChanged() == false);
        UNIT_ASSERT(foundCallback.GetObjectCounter() == 2);
    } // Y_UNIT_TEST(TestRealtimeChangingSearchTimeRestrictions)

    Y_UNIT_TEST(TestChangingSearchSettings) {
        TGraph graph{CreateGiantRhombusGraph()};
        graph.BuildEdgeStorage(5);

        TPositionOnEdge startPosition{5_eid, 0.5};

        const auto& uuid = 1ull;
        TObjectIndex<ui64> objIndex(graph);

        objIndex.Insert(uuid, TPositionOnEdge{0_eid, 0.5});
        objIndex.Insert(uuid + 1, TPositionOnEdge{4_eid, 0.5});

        TFastSearchSettings settings = TEST_SETTINGS;
        settings.MaxTime = TTime(1000);
        TTestCallback<TTestReverseSearchTraits> foundCallback;
        TTestFastDijkstraEdgeSearcher<TTestReverseSearchTraits, TTestCallback<TTestReverseSearchTraits>> searcher(graph, settings, objIndex, foundCallback);
        searcher.Search(startPosition);

        UNIT_ASSERT(foundCallback.GetDistancesToObjects().find(uuid) == foundCallback.GetDistancesToObjects().end());
        UNIT_ASSERT(foundCallback.GetDistancesToObjects().find(uuid + 1) != foundCallback.GetDistancesToObjects().end());

        foundCallback.Reset();
        bool changed = searcher.SetSearchSettings(TEST_SETTINGS);
        UNIT_ASSERT(changed);
        searcher.Search(startPosition);

        UNIT_ASSERT(foundCallback.GetDistancesToObjects().find(uuid) != foundCallback.GetDistancesToObjects().end());
        UNIT_ASSERT(foundCallback.GetDistancesToObjects().find(uuid + 1) != foundCallback.GetDistancesToObjects().end());
    } // Y_UNIT_TEST(TestChangingSearchSettings)

    Y_UNIT_TEST(TestObjectRulesNonPavedDisabled) {
        TGraph graph{CreateGraphWithNonPavedRoads()};

        const auto& uuid = 1ull;
        TObjectIndex<ui64> objIndex(graph);

        objIndex.Insert(uuid, TPositionOnEdge{0_eid, 0.5});

        {
            TTestCallback<TTestReverseSearchTraitsDisableDriveThroughNonPaved> foundCallback;
            TTestFastDijkstraEdgeSearcher<TTestReverseSearchTraitsDisableDriveThroughNonPaved, TTestCallback<TTestReverseSearchTraitsDisableDriveThroughNonPaved>> searcher(graph, TEST_SETTINGS, objIndex, foundCallback);

            searcher.Search({4_eid, 0.5});

            const auto& res = foundCallback.GetEdgeIds();
            UNIT_ASSERT_EQUAL(res.size(), 0);
        }
    } // Y_UNIT_TEST(TestObjectRulesNonPavedDisabled)

    Y_UNIT_TEST(TestObjectRulesNonPavedDisabledInsideYard) {
        TGraph graph{CreateGraphWithNonPavedRoadsInsideYard()};

        const auto& uuid = 1ull;
        TObjectIndex<ui64> objIndex(graph);

        objIndex.Insert(uuid, TPositionOnEdge{0_eid, 0.5});
        objIndex.Insert(uuid + 1, TPositionOnEdge{3_eid, 0.5});

        {
            TTestCallback<TTestReverseSearchTraitsDisableDriveThroughNonPaved> foundCallback;
            TTestFastDijkstraEdgeSearcher<TTestReverseSearchTraitsDisableDriveThroughNonPaved, TTestCallback<TTestReverseSearchTraitsDisableDriveThroughNonPaved>> searcher(graph, TEST_SETTINGS, objIndex, foundCallback);

            searcher.Search({4_eid, 0.5});

            const auto& res = foundCallback.GetEdgeIds();
            UNIT_ASSERT_EQUAL(res.size(), 2);
        }
    } // Y_UNIT_TEST(TestObjectRulesNonPavedDisabledInsideYard)

    Y_UNIT_TEST(TestTollRoadsDisabledStartWithTollRoad) {
        TGraph graph{CreateGraphWithTollRoads()};

        const auto& uuid = 1ull;
        TObjectIndex<ui64> objIndex(graph);

        objIndex.Insert(uuid, TPositionOnEdge{0_eid, 0.5});

        {
            TTestCallback<TTestReverseSearchTraitsDisabledTollRoads> foundCallback;
            TTestFastDijkstraEdgeSearcher<TTestReverseSearchTraitsDisabledTollRoads, TTestCallback<TTestReverseSearchTraitsDisabledTollRoads>> searcher(graph, TEST_SETTINGS, objIndex, foundCallback);

            searcher.Search({3_eid, 0.5});

            const auto& res = foundCallback.GetEdgeIds();
            UNIT_ASSERT_EQUAL(res.size(), 1);
        }
    } // Y_UNIT_TEST(TestTollRoadsDisabledStartWithTollRoad)

    Y_UNIT_TEST(TestTollRoadsDisabledTollRoadInsidePath) {
        TGraph graph{CreateGraphWithTollRoad()};

        const auto& uuid = 1ull;
        TObjectIndex<ui64> objIndex(graph);

        objIndex.Insert(uuid, TPositionOnEdge{0_eid, 0.5});

        {
            TTestCallback<TTestReverseSearchTraitsDisabledTollRoads> foundCallback;
            TTestFastDijkstraEdgeSearcher<TTestReverseSearchTraitsDisabledTollRoads, TTestCallback<TTestReverseSearchTraitsDisabledTollRoads>> searcher(graph, TEST_SETTINGS, objIndex, foundCallback);

            searcher.Search({3_eid, 0.5});

            const auto& res = foundCallback.GetEdgeIds();
            UNIT_ASSERT_EQUAL(res.size(), 0);
        }
    } // Y_UNIT_TEST(TestTollRoadsDisabledTollRoadInsidePath)

    Y_UNIT_TEST(TestTransformatorAndChangeSettingsInSearcher) {
        TGraph graph{CreateGraphWithTollRoad()};

        const auto& uuid = 1ull;
        TTestObjectIndex objIndex(graph);
        objIndex.Insert(uuid, TPositionOnEdge{0_eid, 0.5});
        TestImmediateStopCallback callback;
        TTestObjectIndexSearcherCreator creator(callback, objIndex);
        auto currentSettings = TTestSettings{};

        // Creating searcher
        auto searcher = TTestObjectIndexTransformator::CreateTarget(creator, graph, currentSettings);

        // Check that searcher has appropriate traits
        UNIT_ASSERT_EQUAL(searcher.GetCurrentFlags(), TTestSearchTraitsToFlagsConverter::GetFlags(currentSettings));

        searcher.Search({3_eid, 0.5});

        currentSettings.TrackEdgeLeeway = false;

        // CHange Settings
        searcher.SetSearchSettings(currentSettings);

        // Check that searcher has appropriate traits
        UNIT_ASSERT_EQUAL(searcher.GetCurrentFlags(), TTestSearchTraitsToFlagsConverter::GetFlags(currentSettings));

        searcher.Search({3_eid, 0.5});
    } // Y_UNIT_TEST(TestTransformatorAndChangeSettingsInSearcher)
}
