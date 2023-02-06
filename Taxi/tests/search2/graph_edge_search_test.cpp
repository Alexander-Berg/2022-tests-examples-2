#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <taxi/graph/libs/graph/graph_data_builder.h>
#include <taxi/graph/libs/search2/dijkstra_edge_searcher.h>
#include <taxi/graph/libs/search2/object_index_edge_processor.h>

#include <iostream>

#include <taxi/graph/libs/graph-test/graph_test_data.h>

#include "common.h"

#define UNIT_ASSERT_OPTIONAL_DOUBLES_EQUAL(E, A, D)                                        \
    do {                                                                                   \
        if (!(E) && !(A))                                                                  \
            continue;                                                                      \
        if ((!(E) && (A)) || ((E) && (!A))) {                                              \
            if (!E) {                                                                      \
                const auto _as = ToString(ToTestDouble(A));                                \
                auto&& failMsg = Sprintf("left is std::nullopt, right is %s", _as.data()); \
                UNIT_FAIL(failMsg);                                                        \
            }                                                                              \
            const auto _es = ToString(ToTestDouble(E));                                    \
            auto&& failMsg = Sprintf("left is %s, right is std::nullopt", _es.data());     \
            UNIT_FAIL(failMsg);                                                            \
        }                                                                                  \
        UNIT_ASSERT_DOUBLES_EQUAL(ToTestDouble(E), ToTestDouble(A), D);                    \
    } while (false)

using NTaxi::NGraph2::TClosures;
using NTaxi::NGraph2::TEdge;
using NTaxi::NGraph2::TEdgeData;
using NTaxi::NGraph2::TEdgeId;
using NTaxi::NGraph2::TGraph;
using NTaxi::NGraph2::TId;
using NTaxi::NGraph2::TJams;
using NTaxi::NGraph2::TPersistentEdgeId;
using NTaxi::NGraph2::TPersistentIndex;
using NTaxi::NGraph2::TPositionOnEdge;
using NTaxi::NGraph2::TRoadGraphDataBuilder;
using NTaxi::NGraph2::TVertexId;
using NTaxi::NGraphSearch2::EStopReason;
using TWeight = double;
using NTaxi::NGraphSearch2::DirectionizedEdgePastEnd;
using NTaxi::NGraphSearch2::DirectionizedEdgeStart;
using NTaxi::NGraphSearch2::SearchState;
using NTaxi::NGraphSearch2::TDirectionizedPosition;
using NTaxi::NGraphSearch2::TDistance;
using NTaxi::NGraphSearch2::TFastSearchSettings;
using NTaxi::NGraphSearch2::TPathGeolength;
using NTaxi::NGraphSearch2::TTime;

using namespace NTaxi::NGraph2Literals;

namespace {
    struct CollectedTestData {
        std::unordered_map<TVertexId, TWeight> DiscoveredDistances;
        std::unordered_map<TEdgeId, TWeight> DiscoveredEdgeDistances;
        std::unordered_map<TVertexId, TWeight> FinalDistances;
        std::unordered_map<TEdgeId, TWeight> EdgeFinalDistances;
        std::unordered_map<TVertexId, TEdgeId> PrecedingEdges;
        std::vector<TVertexId> VertexVisitOrder;
        std::vector<TEdgeId> EdgeVisitOrder;
    };

    template <typename SearchTraits>
    struct TTestHandlers {
        using TSearchTraits = SearchTraits;
        using TDirectionControl = typename TSearchTraits::TDirectionControl;
        const TGraph& Graph;
        std::shared_ptr<CollectedTestData> TestData;

        double RoundTo3Digits(double value) {
            return static_cast<int>(value * 1000 + 0.5) / 1000.0;
        }

        TTestHandlers(const TGraph& graph)
            : Graph(graph)
            , TestData(std::make_shared<CollectedTestData>())
        {
        }

        void OnClear() {
            *TestData = CollectedTestData{};
            // Don't do like this:
            // TestData = std::make_shared<CollectedTestData>();
            // Somehow, compiler optimized it into non-working code.
        }

        void OnNextEdgeRelaxation([[maybe_unused]] TEdgeId currentEdgeId, [[maybe_unused]] TEdgeId nextEdgeId, [[maybe_unused]] double distanceToStart, TTime timeToStart) {
            TestData->DiscoveredEdgeDistances.insert({nextEdgeId, timeToStart.count()});
        }

        void OnImpassableStartEdge(const TPositionOnEdge& posOnEdge) {
        }

        void OnStartEdgeVisit(const TPositionOnEdge& posOnEdge) {
            ProcessEdgeVisit(posOnEdge.EdgeId, 0, TSearchTraits::TDirectionControl::MapPositionToDirection(posOnEdge.Position), DirectionizedEdgePastEnd);
        }

        template <typename TEdgeInfo>
        void OnEdgeVisit(const TEdgeInfo& edgeInfo) {
            const TEdgeId edgeId = edgeInfo.EdgeId;
            const double timeToStart = edgeInfo.Time.count();

            ProcessEdgeVisit(edgeId, timeToStart, DirectionizedEdgeStart, DirectionizedEdgePastEnd);
        }

        /// normalized[To|From]Fraction are to/from position that we fixed
        /// according to directions. That is, 1.0 is always the "end" of an edge
        /// according to selected direction, and 0.0 is alwyas the "beginning"
        /// they denote a half-range(!) - [from, to) - to is NOT included!
        void ProcessEdgeVisit(TEdgeId edgeId, double timeToStart, TDirectionizedPosition normalizedFromFraction,
                              TDirectionizedPosition normalizedToFraction) {
            timeToStart = RoundTo3Digits(timeToStart);
            const auto& edge = Graph.GetEdge(edgeId);
            const auto& edgeData = Graph.GetEdgeData(edgeId);

            const auto& endEdgeVertexId = TDirectionControl::GetEndVertex(edge);
            const auto& startEdgeVertexId = TDirectionControl::GetStartVertex(edge);

            TestData->VertexVisitOrder.push_back(endEdgeVertexId);
            TestData->EdgeVisitOrder.push_back(edgeId);
            if (normalizedFromFraction == DirectionizedEdgeStart) {
                // even if start edge was started with '0.0' position, it still
                // can be visited twice - new dijkstra doesn't track edge
                // fractions. So, use insert/emplace instead of 'operator ='
                TestData->EdgeFinalDistances.emplace(edgeId, timeToStart);
            }

            if (edgeData.Speed == 0.0) {
                return;
            }

            const TWeight edgeTime = std::llround(edgeData.Length / edgeData.Speed) * (normalizedToFraction - normalizedFromFraction).value();
            Y_VERIFY_DEBUG(edgeTime >= 0.0);

            // To check for correctness, we emulate 'seach by vertexes' via edges search:
            // 1. min distance to vertex is min( (min distance to edge) for every outgoing edge)
            // 2. preceding edge is an preceding edge for edge selected above
            if (UpdateWithMin(TestData->FinalDistances, endEdgeVertexId, RoundTo3Digits(timeToStart + edgeTime))) {
                TestData->PrecedingEdges[endEdgeVertexId] = edgeId;
            }
            if (normalizedFromFraction == DirectionizedEdgeStart) {
                UpdateWithMin(TestData->FinalDistances, startEdgeVertexId, timeToStart);
            }
            TestData->DiscoveredDistances.insert({endEdgeVertexId, RoundTo3Digits(timeToStart + edgeTime)});
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

        template <typename Map>
        void PrintIdMapSorted(const Map& map) const {
            TVector<std::pair<typename Map::key_type, typename Map::mapped_type>> data;
            for (const auto& p : map) {
                data.push_back(p);
            }

            std::sort(data.begin(), data.end(), [](const auto& first, const auto& second) { return first.first.value() < second.first.value(); });
            for (auto [k, v] : data) {
                Cout << k.value() << " -> " << v << Endl;
            }
            Cout << "---" << Endl;
        }

        void PrintEdgeFinalDistances() const {
            Cout << "Edge final distance:" << Endl;
            PrintIdMapSorted(TestData->EdgeFinalDistances);
        }
        void PrintVertexFinalDistances() const {
            Cout << "Vertex final distance:" << Endl;
            PrintIdMapSorted(TestData->FinalDistances);
        }
        void PrintDiscoveredEdgeDistances() const {
            Cout << "Discovered edge distance:" << Endl;
            PrintIdMapSorted(TestData->DiscoveredEdgeDistances);
        }
        void PrintDiscoveredVertexDistances() const {
            Cout << "Discovered vertex distance:" << Endl;
            PrintIdMapSorted(TestData->DiscoveredDistances);
        }
        void PrintEdgeVisitOrder() const {
            Cout << "Edge visit order:" << Endl;
            for (auto v : TestData->EdgeVisitOrder)
                Cout << v.value() << Endl;
            Cout << "-" << Endl;
        }

        void EdgeSuccessfullyRelaxed() {
        }
        void EdgeSkippedBecauseBoomBarrierViolated() {
        }
        void EdgeSkippedBecauseClosure() {
        }
        void EdgeSkippedBecauseWorse() {
        }
        void EdgeSkippedBecauseEmptyYard() {
        }
        void EdgeSkippedBecauseResidentialAreaDriveThrough() {
        }
        void EdgeSkippedBecauseTooFar(double distance, TTime time) {
        }
    };

    using TTestForwardSearchHandlers = TTestHandlers<TTestForwardSearchTraits>;
    using TTestForwardSearchEntryProhibitedHandlers = TTestHandlers<TTestForwardEntryProhibitedSearchTraits>;
    using TTestReverseSearchHandlers = TTestHandlers<TTestReverseSearchTraits>;
    using TTestObjectIndex = NTaxi::NGraph2::TObjectIndex<ui64>;

    struct TTestFastFoundObjectsCallback {
        template <typename... Args>
        SearchState operator()(Args&&...) {
            return SearchState::ContinueState;
        }
    };

    template <typename TestHandlersType>
    struct TTestFastDijkstraEdgeSearcher {
        TTestFastDijkstraEdgeSearcher(const TGraph& graph, const TestHandlersType& actions,
                                      TJams* jamsPtr = nullptr, TClosures* closuresPtr = nullptr)
            : Graph(graph)
            , SearchSettings{
                  TTime{1 << 15},      /*MaxTime*/
                  TDistance{100000.0}, /*MaxDistance*/
                  100000,              /*MaxVisitedEdgesCount*/
                  {}}
            , FilledObjectIndex(graph)
            , EdgeProcessor(FilledObjectIndex, EmptyCallback)
            , Searcher({graph, graph.GetEdgeStorage()}, SearchSettings, EdgeProcessor, jamsPtr, closuresPtr, actions)
        {
            InitObjectIndex();
        }

        TTestFastDijkstraEdgeSearcher(const TGraph& graph, const TFastSearchSettings& searchSettings, const TestHandlersType& actions,
                                      TJams* jamsPtr = nullptr, TClosures* closuresPtr = nullptr)
            : Graph(graph)
            , SearchSettings(searchSettings)
            , FilledObjectIndex(graph)
            , EdgeProcessor(FilledObjectIndex, EmptyCallback)
            , Searcher({graph, graph.GetEdgeStorage()}, SearchSettings, EdgeProcessor, jamsPtr, closuresPtr, actions)
        {
            InitObjectIndex();
        }

        void InitObjectIndex() {
            // some dijkstra optimization allow skipping part of graph where
            // there are no drivers.
            // To prevent this, we place one object on every edge

            for (unsigned int i = 0; i < Graph.EdgesCount(); ++i) {
                FilledObjectIndex.Insert(i, TPositionOnEdge{TEdgeId{i}, 0.5});
            }
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

        template <typename... Args>
        auto GetPath(Args&&... args) const {
            return Searcher.GetPath(std::forward<Args>(args)...);
        }

        template <typename... Args>
        auto GetRoute(Args&&... args) const {
            return Searcher.GetRoute(std::forward<Args>(args)...);
        }
        auto GetRoute(const TPositionOnEdge& pos) const {
            return Searcher.GetRoute(pos);
        }

        template <typename... Args>
        auto GetRouteInfo(Args&&... args) const {
            return Searcher.GetRouteInfo(std::forward<Args>(args)...);
        }
        auto GetRouteInfo(const TPositionOnEdge& pos) const {
            return Searcher.GetRouteInfo(pos);
        }

        std::optional<TPathGeolength> GetPathLengthInMeters(const TPositionOnEdge& pos) const {
            const auto& routeInfo = GetRouteInfo(pos);
            if (!routeInfo)
                return std::nullopt;
            return routeInfo->PathLengthInMeters;
        }

        const auto& GetStatistics() const {
            return Searcher.GetStatistics();
        }

        const TGraph& Graph;
        TFastSearchSettings SearchSettings;
        TTestFastFoundObjectsCallback EmptyCallback;
        TTestObjectIndex FilledObjectIndex;
        using TTestEdgeProcessor =
            NTaxi::NGraphSearch2::TObjectIndexEdgeProcessor<
                typename TestHandlersType::TSearchTraits,
                TTestObjectIndex,
                TTestFastFoundObjectsCallback>;

        TTestEdgeProcessor EdgeProcessor;

        using TSearcher =
            NTaxi::NGraphSearch2::TFastDijkstraEdgeSearcher<
                NTaxi::NGraph2::TGraphFacadeCommon,
                typename TestHandlersType::TSearchTraits,
                TTestEdgeProcessor,
                TestHandlersType>;
        TSearcher Searcher;
    };

    using TAnyOrderGroup = std::unordered_set<TEdgeId>;
    using TExpectedVisitOrder = std::deque<std::variant<TEdgeId, TAnyOrderGroup>>;

    bool operator==(const TExpectedVisitOrder& expected_order_orig, const std::vector<TEdgeId>& actual_order) {
        TExpectedVisitOrder expected_order = expected_order_orig;
        for (TEdgeId edgeId : actual_order) {
            if (expected_order.size() == 0) {
                return false;
            }

            auto& expected_element = expected_order[0];
            // compare with first element. If equal or in set - everything is ok
            // and pull this elemnet out of expected_order.
            if (expected_element.index() == 0) { /*edge id*/
                if (edgeId != std::get<0>(expected_element)) {
                    return false;
                }
                // ok, remove expected_elemnet
                expected_order.pop_front();
                continue;
            } else {
                TAnyOrderGroup& group = std::get<1>(expected_element);
                auto fit = group.find(edgeId);
                if (fit == group.end()) {
                    return false;
                }
                // ok, element is present, remove it
                group.erase(fit);
                // if group now empty, remove whole group
                if (group.empty()) {
                    expected_order.pop_front();
                }
            }
        }
        return true;
    }
    bool operator==(const std::vector<TEdgeId>& actual_order, const TExpectedVisitOrder& expected_order) {
        return expected_order == actual_order;
    }
    [[maybe_unused]] bool operator!=(const std::vector<TEdgeId>& actual_order, const TExpectedVisitOrder& expected_order) {
        return !(expected_order == actual_order);
    }

}

class TGraphFastEdgeDijkstraSearchFixture: public ::NUnitTest::TBaseTestCase, public NTaxi::NGraph2::TGraphTestData {
};

Y_UNIT_TEST_SUITE_F(graph_dijkstra_edge_search, TGraphFastEdgeDijkstraSearchFixture) {
    Y_UNIT_TEST(dijkstra_search_rhombus) {
        TGraph graph{CreateRhombusGraph()};
        graph.BuildEdgeStorage(32);

        TTestForwardSearchHandlers testHandlers(graph);
        TTestFastDijkstraEdgeSearcher searcher(graph, testHandlers);
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

        UNIT_ASSERT_EQUAL(testHandlers.TestData->FinalDistances, expectedFinalDistances);
        UNIT_ASSERT_EQUAL(testHandlers.TestData->EdgeVisitOrder, expectedEdgeVisitOrder);
        UNIT_ASSERT_EQUAL(testHandlers.TestData->VertexVisitOrder, expectedVertexVisitOrder);

        UNIT_ASSERT_EQUAL(testHandlers.TestData->DiscoveredEdgeDistances, expectedDiscoveredDistances);
        UNIT_ASSERT_EQUAL(testHandlers.TestData->PrecedingEdges, expectedPrecedingEdges);

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
        UNIT_ASSERT(searcher.GetStatistics().SkippedEdgesByTimeOrDistance == 0);
    }

    Y_UNIT_TEST(dijkstra_search_rhombus_not_passable_edges) {
        TGraph graph{CreateRhombusGraphNotPassable()};
        graph.BuildEdgeStorage(32);
        TTestForwardSearchHandlers testHandlers(graph);
        TTestFastDijkstraEdgeSearcher searcher(graph, testHandlers);
        const auto searchStopReason = searcher.Search(0_eid);
        UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);

        // clang-format on
        std::vector<TEdgeId> expectedEdgeVisitOrder = {0_eid, 1_eid};

        UNIT_ASSERT_EQUAL(testHandlers.TestData->EdgeVisitOrder, expectedEdgeVisitOrder);
    }
    Y_UNIT_TEST(get_edges_visited) {
        TGraph graph{CreateRhombusGraph()};
        graph.BuildEdgeStorage(32);
        TTestForwardSearchHandlers testHandlers(graph);
        TTestFastDijkstraEdgeSearcher searcher(graph, testHandlers);
        const auto searchStopReason = searcher.Search(0_eid);
        UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);
        UNIT_ASSERT_EQUAL(6, searcher.Searcher.GetVisitedEdgesCount());
    }

    Y_UNIT_TEST(test_recognize_toll_road) {
        TGraph graph{CreateRhombusGraphWithTollRoad()};
        graph.BuildEdgeStorage(32);
        TTestForwardSearchHandlers testHandlers(graph);
        TTestFastDijkstraEdgeSearcher searcher(graph, testHandlers);

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

    Y_UNIT_TEST(dijskstra_search_rhombus_path_lengths) {
        TGraph graph{CreateRhombusGraph()};
        graph.BuildEdgeStorage(32);
        TTestForwardSearchHandlers testHandlers(graph);
        TTestFastDijkstraEdgeSearcher searcher(graph, testHandlers);
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
            // this will test GetRouteInfo as well, because
            // GetPathLengthInMeters is implemented over it
            const auto& actual = searcher.GetPathLengthInMeters(testCase.first);
            const auto& expected = testCase.second;
            UNIT_ASSERT_OPTIONAL_DOUBLES_EQUAL(actual, expected, 0.0001);
        }
    }

    Y_UNIT_TEST(dijskstra_search_rhombus_path_lengths_v2) {
        // A bit different set of cases.
        TGraph graph{CreateRhombusGraph()};
        graph.BuildEdgeStorage(32);
        TTestForwardSearchHandlers testHandlers(graph);
        TTestFastDijkstraEdgeSearcher searcher(graph, testHandlers);
        const auto& searchStopReason = searcher.Search(TPositionOnEdge{1_eid, 0.5});
        UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);

        // first - position on edge, second - length of shortest path to this position
        const std::vector<std::pair<TPositionOnEdge, std::optional<TPathGeolength>>> cases = {
            {TPositionOnEdge{1_eid, 0.}, std::nullopt},
            {TPositionOnEdge{1_eid, 0.5}, TPathGeolength{0.0}},
            {TPositionOnEdge{1_eid, 1.}, TPathGeolength{0.5}},

            {TPositionOnEdge{2_eid, 0.}, std::nullopt},
            {TPositionOnEdge{2_eid, 0.5}, std::nullopt},
            {TPositionOnEdge{2_eid, 1.0}, std::nullopt},

            {TPositionOnEdge{3_eid, 0.}, TPathGeolength{0.5}},
            {TPositionOnEdge{3_eid, 0.5}, TPathGeolength{2.}},
            {TPositionOnEdge{3_eid, 1.}, TPathGeolength{3.5}},
        };

        for (const auto& testCase : cases) {
            const auto& actual = searcher.GetPathLengthInMeters(testCase.first);
            const auto& expected = testCase.second;
            UNIT_ASSERT_OPTIONAL_DOUBLES_EQUAL(actual, expected, 0.0001);
        }
    }

    Y_UNIT_TEST(dijskstra_search_rhombus_path_lengths_cycle) {
        // A bit different set of cases.
        TGraph graph{CreateCycleGraph(10u)};
        graph.BuildEdgeStorage(32);
        TTestForwardSearchHandlers testHandlers(graph);
        TTestFastDijkstraEdgeSearcher searcher(graph, testHandlers);
        const auto& searchStopReason = searcher.Search(TPositionOnEdge{0_eid, 0.5});
        UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);

        // first - position on edge, second - length of shortest path to this position
        const std::vector<std::pair<TPositionOnEdge, std::optional<TPathGeolength>>> cases = {
            {TPositionOnEdge{0_eid, 0.}, TPathGeolength{25.0}},
            {TPositionOnEdge{0_eid, 0.5}, TPathGeolength{0.0}},
            {TPositionOnEdge{0_eid, 1.}, TPathGeolength{5.}},

            {TPositionOnEdge{1_eid, 0.}, TPathGeolength{5.0}},
            {TPositionOnEdge{1_eid, 0.5}, TPathGeolength{10.0}},
            {TPositionOnEdge{1_eid, 1.0}, TPathGeolength{15.0}},

            {TPositionOnEdge{2_eid, 0.}, TPathGeolength{15.0}},
            {TPositionOnEdge{2_eid, 0.5}, TPathGeolength{20.0}},
            {TPositionOnEdge{2_eid, 1.0}, TPathGeolength{25.0}},
        };

        for (const auto& testCase : cases) {
            const auto& actual = searcher.GetPathLengthInMeters(testCase.first);
            const auto& expected = testCase.second;
            UNIT_ASSERT_OPTIONAL_DOUBLES_EQUAL(actual, expected, 0.0001);
        }
    }

    Y_UNIT_TEST(dijkstra_search_reversed_edges) {
        TGraph graph{CreateRhombusGraphReversed()};
        graph.BuildEdgeStorage(32);

        TTestReverseSearchHandlers testHandlers(graph);
        TFastSearchSettings settings;

        TTestFastDijkstraEdgeSearcher searcher(graph, settings, testHandlers);
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

        UNIT_ASSERT_EQUAL(testHandlers.TestData->FinalDistances, expectedFinalDistances);
        UNIT_ASSERT_EQUAL(testHandlers.TestData->EdgeVisitOrder, expectedEdgeVisitOrder);

        UNIT_ASSERT_EQUAL(testHandlers.TestData->DiscoveredEdgeDistances, expectedDiscoveredDistances);
        UNIT_ASSERT_EQUAL(testHandlers.TestData->PrecedingEdges, expectedPrecedingEdges);

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

    Y_UNIT_TEST(dijkstra_search_reversed_rhombus_path_lengths) {
        TGraph graph{CreateRhombusGraphReversed()};
        graph.BuildEdgeStorage(32);

        TTestReverseSearchHandlers testHandlers(graph);
        TFastSearchSettings settings;

        TTestFastDijkstraEdgeSearcher searcher(graph, settings, testHandlers);
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

    // Test with standard stop condition
    Y_UNIT_TEST(dijkstra_search_wikipedia_example) {
        TGraph graph = BuildGraphForDijkstraFromWikipedia();
        graph.BuildEdgeStorage(32);

        TTestForwardSearchHandlers testHandlers(graph);
        TTestFastDijkstraEdgeSearcher searcher(graph, testHandlers);
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
            TExpectedVisitOrder expectedEdgeVisitOrder = {
                0_eid,
                /* those 3 can be in any order actually */
                TAnyOrderGroup{
                  1_eid,
                  2_eid,
                  3_eid,
                },
                /* and those must be in this order*/
                4_eid,
                5_eid,
                6_eid,
                7_eid,
                9_eid,
                8_eid
            };
        // clang-format on

        Cout << "FinalDistances: ";
        for (auto [k, v] : testHandlers.TestData->FinalDistances)
            Cout << k.value() << " " << v << ", " << Endl;
        Cout << "EdgeFinalDistances: ";
        for (auto [k, v] : testHandlers.TestData->EdgeFinalDistances)
            Cout << k.value() << " " << v << ", " << Endl;
        Cout << "PrecedingEdges: ";
        for (auto [k, v] : testHandlers.TestData->PrecedingEdges)
            Cout << k.value() << " " << v.value() << ", " << Endl;
        Cout << "EdgeVisitOrder: ";
        for (auto v : testHandlers.TestData->EdgeVisitOrder)
            Cout << v.value() << ", " << Endl;

        UNIT_ASSERT_EQUAL(testHandlers.TestData->FinalDistances, expectedFinalDistances);
        UNIT_ASSERT_EQUAL(testHandlers.TestData->EdgeFinalDistances, expectedEdgeFinalDistances);
        UNIT_ASSERT_EQUAL(testHandlers.TestData->PrecedingEdges, expectedPrecedingEdges);
        UNIT_ASSERT_EQUAL(testHandlers.TestData->EdgeVisitOrder, expectedEdgeVisitOrder);

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

    Y_UNIT_TEST(dijkstra_search_giant_cycle_graph_path_lengthes) {
        TGraph graph = CreateGiantCycleGraph();
        graph.BuildEdgeStorage(32);

        TTestForwardSearchHandlers testHandlers(graph);
        TTestFastDijkstraEdgeSearcher searcher(graph, testHandlers);
        const auto& searchStopReason = searcher.Search(TPositionOnEdge{0_eid, 0.5});
        UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);

        {
            const auto& actual = searcher.GetPathLengthInMeters(TPositionOnEdge{0_eid, 0.5 - 0.005});
            UNIT_ASSERT(actual);
            UNIT_ASSERT(actual.value().value() >= 0.);
        }
    }

    Y_UNIT_TEST(dijkstra_search_wikipedia_example_path_lengthes) {
        TGraph graph = BuildGraphForDijkstraFromWikipedia();
        graph.BuildEdgeStorage(32);

        TTestForwardSearchHandlers testHandlers(graph);
        TTestFastDijkstraEdgeSearcher searcher(graph, testHandlers);
        const auto& searchStopReason = searcher.Search(TPositionOnEdge{0_eid, 0.5});
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

    Y_UNIT_TEST(dijkstra_search_stop_by_distance) {
        TGraph graph = BuildGraphForDijkstraFromWikipedia();
        graph.BuildEdgeStorage(32);

        TTestForwardSearchHandlers testHandlers(graph);
        TFastSearchSettings settings;
        settings.StopCondition = [](const TGraph&, TEdgeId, TWeight currentDistance) {
            return currentDistance >= 8;
        };
        settings.IterationsCountPerStopCheck = 1;

        TTestFastDijkstraEdgeSearcher searcher(graph, settings, testHandlers);
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
            // {6_eid, 9}, // this edge would have caused a halt
        };
        TExpectedVisitOrder expectedEdgeVisitOrder = {
          0_eid,
          /* those 3 can be in any order */
          TAnyOrderGroup{
          1_eid,
          2_eid,
          3_eid,
          },
          // the rest cant
          4_eid,
          5_eid,
          // 6_eid, this edge is not visited due to stop condition
        };
        // clang-format on

        Cout << "FinalDistances: ";
        for (auto [k, v] : testHandlers.TestData->FinalDistances)
            Cout << k.value() << " " << v << ", " << Endl;
        Cout << "EdgeFinalDistances: ";
        for (auto [k, v] : testHandlers.TestData->EdgeFinalDistances)
            Cout << k.value() << " " << v << ", " << Endl;
        Cout << "PrecedingEdges: ";
        for (auto [k, v] : testHandlers.TestData->PrecedingEdges)
            Cout << k.value() << " " << v.value() << ", " << Endl;
        Cout << "EdgeVisitOrder: ";
        for (auto v : testHandlers.TestData->EdgeVisitOrder)
            Cout << v.value() << ", " << Endl;
        UNIT_ASSERT_EQUAL(testHandlers.TestData->EdgeFinalDistances, expectedEdgeFinalDistances);
        UNIT_ASSERT_EQUAL(testHandlers.TestData->EdgeVisitOrder, expectedEdgeVisitOrder);
    }

    Y_UNIT_TEST(dijkstra_search_stop_by_path_length_in_meters) {
        TGraph graph = BuildGraphForDijkstraFromWikipedia();
        graph.BuildEdgeStorage(32);

        TTestForwardSearchHandlers testHandlers(graph);
        TFastSearchSettings settings;
        settings.MaxDistance = TDistance{10.0};

        TTestFastDijkstraEdgeSearcher searcher(graph, settings, testHandlers);
        const auto& searchStopReason = searcher.Search(0_eid);
        UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);

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
            TExpectedVisitOrder expectedEdgeVisitOrder = {
              0_eid,
              TAnyOrderGroup{
              1_eid,
              2_eid,
              3_eid,
              },
              4_eid,
              5_eid,
              6_eid,
              7_eid,
            };
        // clang-format on

        UNIT_ASSERT_EQUAL(testHandlers.TestData->EdgeFinalDistances, expectedEdgeFinalDistances);
        UNIT_ASSERT_EQUAL(testHandlers.TestData->EdgeVisitOrder, expectedEdgeVisitOrder);
        UNIT_ASSERT(searcher.GetStatistics().SkippedEdgesByTimeOrDistance > 0);
    }

    Y_UNIT_TEST(dijkstra_search_stop_by_path_time) {
        TGraph graph = BuildGraphForDijkstraFromWikipedia();
        graph.BuildEdgeStorage(32);

        TTestForwardSearchHandlers testHandlers(graph);
        TFastSearchSettings settings;
        settings.MaxTime = TTime{7.1};

        TTestFastDijkstraEdgeSearcher searcher(graph, settings, testHandlers);
        const auto& searchStopReason = searcher.Search(0_eid);
        UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);

        // clang-format off
            std::unordered_map<TEdgeId, TWeight> expectedEdgeFinalDistances = {
                {0_eid, 0},
                {1_eid, 0},
                {2_eid, 0},
                {3_eid, 0},
                {4_eid, 7},
                {5_eid, 7},
            };
            TExpectedVisitOrder expectedEdgeVisitOrder = {
              0_eid,
              TAnyOrderGroup{
              1_eid,
              2_eid,
              3_eid,
              },
              4_eid,
              5_eid,
            };
        // clang-format on

        UNIT_ASSERT_EQUAL(testHandlers.TestData->EdgeFinalDistances, expectedEdgeFinalDistances);
        UNIT_ASSERT_EQUAL(testHandlers.TestData->EdgeVisitOrder, expectedEdgeVisitOrder);
        UNIT_ASSERT(searcher.GetStatistics().SkippedEdgesByTimeOrDistance > 0);
    }

    Y_UNIT_TEST(dijkstra_search_stop_by_max_discovered_edges) {
        TGraph graph = BuildGraphForDijkstraFromWikipedia();
        graph.BuildEdgeStorage(32);

        TTestForwardSearchHandlers testHandlers(graph);
        TFastSearchSettings settings;
        settings.MaxVisitedEdgesCount = 5;
        settings.IterationsCountPerStopCheck = 1;

        TTestFastDijkstraEdgeSearcher searcher(graph, settings, testHandlers);
        const auto& searchStopReason = searcher.Search(0_eid);
        UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);

        // clang-format off
            std::unordered_map<TEdgeId, TWeight> expectedEdgeFinalDistances = {
                {0_eid, 0},
                {1_eid, 0},
                {2_eid, 0},
                {3_eid, 0},
                {4_eid, 7},
            };
            TExpectedVisitOrder expectedEdgeVisitOrder = {
              0_eid,
              TAnyOrderGroup{
                1_eid,
                2_eid,
                3_eid,
              },
              4_eid,
            };
        // clang-format on

        UNIT_ASSERT_EQUAL(testHandlers.TestData->EdgeFinalDistances, expectedEdgeFinalDistances);
        UNIT_ASSERT_EQUAL(testHandlers.TestData->EdgeVisitOrder, expectedEdgeVisitOrder);
    }

    Y_UNIT_TEST(dijkstra_search_zero_visited_edges) {
        TGraph graph = BuildGraphForDijkstraFromWikipedia();
        graph.BuildEdgeStorage(32);

        TTestForwardSearchHandlers testHandlers(graph);
        TFastSearchSettings settings;
        settings.MaxVisitedEdgesCount = 0;

        TTestFastDijkstraEdgeSearcher searcher(graph, settings, testHandlers);
        const auto& searchStopReason = searcher.Search(0_eid);
        UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);
        // just wanted to check that there would be no segfault
    }

    Y_UNIT_TEST(dijkstra_bidirectional_search) {
        // Visualization: https://wiki.yandex-team.ru/taxi/backend/graph/libraries/libtaxigraph/docs/images/Test-na-start-s-neskolkix-reber/
        TGraph graph = BuildGraphForMultipleStartEdges();
        graph.BuildEdgeStorage(32);

        {
            TTestForwardSearchHandlers testHandlers(graph);
            TFastSearchSettings settings;

            TTestFastDijkstraEdgeSearcher searcher(graph, settings, testHandlers);
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
                /* TODO: order can vary greatly. Probably best to remove this
                 * check
                std::vector<TEdgeId> expectedEdgeVisitOrder = {
                14_eid, 15_eid, 12_eid, 13_eid, 10_eid, 11_eid, 8_eid, 9_eid, 2_eid, 3_eid, 4_eid, 5_eid, 6_eid, 7_eid, 0_eid, 1_eid,
                };
                */

            // clang-format on

            testHandlers.PrintEdgeFinalDistances();
            testHandlers.PrintEdgeVisitOrder();

            UNIT_ASSERT_EQUAL(testHandlers.TestData->EdgeFinalDistances, expectedEdgeFinalDistances);
            UNIT_ASSERT_EQUAL(testHandlers.TestData->DiscoveredEdgeDistances, expectedDiscoveredEdgeDistances);
            // TODO: RM, se above
            //UNIT_ASSERT_EQUAL(testHandlers.TestData->EdgeVisitOrder, expectedEdgeVisitOrder);
        }
        {
            TTestReverseSearchHandlers testHandlers(graph);
            TFastSearchSettings settings;

            TTestFastDijkstraEdgeSearcher searcher(graph, settings, testHandlers);
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
                /* TODO: RM
                std::vector<TEdgeId> expectedEdgeVisitOrder = {
                    5_eid, 8_eid, 1_eid, 3_eid, 10_eid, 4_eid, 12_eid, 2_eid, 0_eid, 6_eid, 9_eid, 15_eid, 7_eid, 14_eid, 11_eid, 13_eid,
                };
                */

            // clang-format on

            /* for possible debug needs in future */
            /*std::cout << "Edge visit order:";
                for (auto item: testHandlers.TestData->EdgeVisitOrder) {
                    std::cout << item << ' ';
                }
                std::cout << std::endl << "DiscoveredEdgeDistances:";
                for (auto item: testHandlers.TestData->DiscoveredEdgeDistances) {
                    std::cout << item.first << ' ' << item.second << ", ";
                }
                std::cout << std::endl << "EdgeFinalDistances";
                for (auto item: testHandlers.TestData->EdgeFinalDistances) {
                    std::cout << item.first << ' ' << item.second << ", ";
                }
                std::cout << std::endl << "DiscoveredDistances";
                for (auto item: testHandlers.TestData->DiscoveredDistances) {
                    std::cout << item.first << ' ' << item.second << ", ";
                }
                std::cout << std::endl << "FinalDistances";
                for (auto item: testHandlers.TestData->FinalDistances) {
                    std::cout << item.first << ' ' << item.second << ", ";
                }*/

            UNIT_ASSERT_EQUAL(testHandlers.TestData->EdgeFinalDistances, expectedEdgeFinalDistances);
            UNIT_ASSERT_EQUAL(testHandlers.TestData->DiscoveredEdgeDistances, expectedDiscoveredEdgeDistances);
            // TODO:RM
            //UNIT_ASSERT_EQUAL(testHandlers.TestData->EdgeVisitOrder, expectedEdgeVisitOrder);
        }
    }

    Y_UNIT_TEST(dijkstra_straight_search_with_boom_barriersi_entry_disabled) {
        /*
         *  v0            v1              v2             v3                v4                v5
         *  | >e0 <e3 (1) |  >e2 <e6 (1)  |  >e4 <e9 (2) |  >e7 <e11 (1)   |  >e10 <e12 (1)  |
         *  |<----------->|<-]----------->|<-[--------]->|<--------------->|<--[------------>|
         *  |             |               |              |                 |                 |
         *  |                             |              |                                   |
         *  |        >e1 (5)              |  >e5 (4)     |         >e8 (5)                   |
         *  |---------------------------->|------------->|---------------------------------->|
         *
         *  >eN means edge number N directed from left to right, <eM - edge number M from right to left.
         *  Each bidirectional edge are actually two unidirectional edges.
         *  Lengths of edges are given in brackets.
         *  Square brackets are boom barriers.
         *  Correct optimal route from v0 to v5 is: e0->e2->e5->e8, length is 11.
        */
        auto graph = BuildGraphForBoomBarriers(TReverse::No, TBoomBarriersTestCase::BlockTheWay);
        graph.BuildEdgeStorage(32);

        {
            TTestForwardSearchEntryProhibitedHandlers testHandlers(graph);
            TFastSearchSettings settings;

            TTestFastDijkstraEdgeSearcher searcher(graph, settings, testHandlers);
            const auto& searchStopReason = searcher.Search(0_eid);
            UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);

            std::unordered_map<TVertexId, TWeight> expectedFinalDistances = {
                {0_vid, 0},
                {1_vid, 1},
                {2_vid, 2},
                {3_vid, 6},
                {4_vid, 7},
                {5_vid, 11},
            };

            UNIT_ASSERT_EQUAL(testHandlers.TestData->FinalDistances, expectedFinalDistances);
        }

        // Disable only passing through area surrounded by boom barriers
        // In this case we can use e4 to reach v3
        {
            TTestForwardSearchHandlers testHandlers(graph);
            TFastSearchSettings settings;

            TTestFastDijkstraEdgeSearcher searcher(graph, settings, testHandlers);
            const auto& searchStopReason = searcher.Search(0_eid);
            UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);

            std::unordered_map<TVertexId, TWeight> expectedFinalDistances = {
                {0_vid, 0},
                {1_vid, 1},
                {2_vid, 2},
                {3_vid, 4},
                {4_vid, 7},
                {5_vid, 8},
            };

            UNIT_ASSERT_EQUAL(testHandlers.TestData->FinalDistances, expectedFinalDistances);
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
        auto graph = BuildGraphForBoomBarriers(TReverse::Yes, TBoomBarriersTestCase::BlockTheWay);
        graph.BuildEdgeStorage(32);

        TTestReverseSearchHandlers testHandlers(graph);
        TFastSearchSettings settings;

        TTestFastDijkstraEdgeSearcher searcher(graph, settings, testHandlers);
        const auto& searchStopReason = searcher.Search(1_eid);
        UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);

        std::unordered_map<TVertexId, TWeight> expectedFinalDistances = {
            {0_vid, 0},
            {1_vid, 1},
            {2_vid, 2},
            {3_vid, 4},
            {4_vid, 7},
            {5_vid, 8},
        };

        UNIT_ASSERT_EQUAL(testHandlers.TestData->FinalDistances, expectedFinalDistances);
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
        auto graph = BuildGraphForBoomBarriers(TReverse::Yes, TBoomBarriersTestCase::WayThrough);
        graph.BuildEdgeStorage(32);

        TTestReverseSearchHandlers testHandlers(graph);
        TFastSearchSettings settings;

        TTestFastDijkstraEdgeSearcher searcher(graph, settings, testHandlers);
        const auto& searchStopReason = searcher.Search(1_eid);
        UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);

        std::unordered_map<TVertexId, TWeight> expectedFinalDistances = {
            {0_vid, 0},
            {1_vid, 1},
            {2_vid, 2},
            {3_vid, 4},
            {4_vid, 5},
            {5_vid, 6},
        };

        UNIT_ASSERT_EQUAL(testHandlers.TestData->FinalDistances, expectedFinalDistances);
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
        auto graph = BuildGraphForBoomBarriers(TReverse::Yes, TBoomBarriersTestCase::WayAround);
        graph.BuildEdgeStorage(32);

        TTestReverseSearchHandlers testHandlers(graph);
        TFastSearchSettings settings;

        TTestFastDijkstraEdgeSearcher searcher(graph, settings, testHandlers);
        const auto& searchStopReason = searcher.Search(0_eid);
        UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);

        std::unordered_map<TVertexId, TWeight> expectedDiscoveredDistances = {
            {0_vid, 1},
            {1_vid, 2},
            {2_vid, 6},
            {3_vid, 7},
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

        testHandlers.PrintDiscoveredVertexDistances();
        UNIT_ASSERT_EQUAL(testHandlers.TestData->DiscoveredDistances, expectedDiscoveredDistances);
        UNIT_ASSERT_EQUAL(testHandlers.TestData->FinalDistances, expectedFinalDistances);
        UNIT_ASSERT_EQUAL(testHandlers.TestData->PrecedingEdges[5_vid], 11_eid);
    }

    // Test with standard stop condition
    Y_UNIT_TEST(dijkstra_search_wikipedia_example_reuse_searcher) {
        TGraph graph = BuildGraphForDijkstraFromWikipedia();
        graph.BuildEdgeStorage(32);

        TTestForwardSearchHandlers testHandlers(graph);
        TTestFastDijkstraEdgeSearcher searcher(graph, testHandlers);
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
            TExpectedVisitOrder expectedEdgeVisitOrder = {
                0_eid,
                TAnyOrderGroup{
                  1_eid,
                  2_eid,
                  3_eid,
                },
                4_eid,
                5_eid,
                6_eid,
                7_eid,
                9_eid,
                8_eid
            };
        // clang-format on

        Cout << "FinalDistances: ";
        for (auto [k, v] : testHandlers.TestData->FinalDistances)
            Cout << k.value() << " " << v << ", " << Endl;
        Cout << "EdgeFinalDistances: ";
        for (auto [k, v] : testHandlers.TestData->EdgeFinalDistances)
            Cout << k.value() << " " << v << ", " << Endl;
        Cout << "PrecedingEdges: ";
        for (auto [k, v] : testHandlers.TestData->PrecedingEdges)
            Cout << k.value() << " " << v.value() << ", " << Endl;
        Cout << "EdgeVisitOrder: ";
        for (auto v : testHandlers.TestData->EdgeVisitOrder)
            Cout << v.value() << ", " << Endl;

        UNIT_ASSERT_EQUAL(testHandlers.TestData->FinalDistances, expectedFinalDistances);
        UNIT_ASSERT_EQUAL(testHandlers.TestData->EdgeFinalDistances, expectedEdgeFinalDistances);
        UNIT_ASSERT_EQUAL(testHandlers.TestData->PrecedingEdges, expectedPrecedingEdges);
        UNIT_ASSERT_EQUAL(testHandlers.TestData->EdgeVisitOrder, expectedEdgeVisitOrder);

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

            Cout << "FinalDistances: ";
            for (auto [k, v] : testHandlers.TestData->FinalDistances)
                Cout << k.value() << " " << v << ", " << Endl;
            Cout << "EdgeFinalDistances: ";
            for (auto [k, v] : testHandlers.TestData->EdgeFinalDistances)
                Cout << k.value() << " " << v << ", " << Endl;
            Cout << "PrecedingEdges: ";
            for (auto [k, v] : testHandlers.TestData->PrecedingEdges)
                Cout << k.value() << " " << v.value() << ", " << Endl;
            Cout << "EdgeVisitOrder: ";
            for (auto v : testHandlers.TestData->EdgeVisitOrder)
                Cout << v.value() << ", " << Endl;

            UNIT_ASSERT_EQUAL(testHandlers.TestData->FinalDistances, expectedFinalDistances);
            UNIT_ASSERT_EQUAL(testHandlers.TestData->EdgeFinalDistances, expectedEdgeFinalDistances);
            UNIT_ASSERT_EQUAL(testHandlers.TestData->PrecedingEdges, expectedPrecedingEdges);
            UNIT_ASSERT_EQUAL(testHandlers.TestData->EdgeVisitOrder, expectedEdgeVisitOrder);
        }
    }

    Y_UNIT_TEST(dijkstra_search_change_search_settings) {
        TGraph graph = CreateRhombusGraph();
        graph.BuildEdgeStorage(32);
        TTestForwardSearchHandlers testHandlers(graph);
        TTestFastDijkstraEdgeSearcher searcher(graph, testHandlers);

        {
            const auto& searchStopReason = searcher.Search(0_eid);
            UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::Done);
            const auto& length_for_5_edge = searcher.GetPathLengthInMeters({5_eid, 0.});
            UNIT_ASSERT_OPTIONAL_DOUBLES_EQUAL(length_for_5_edge, std::optional<double>{3.}, 0.0001);
        }

        {
            TFastSearchSettings settings;
            settings.StopCondition = [](const TGraph&, TEdgeId, TWeight) {
                return true;
            };
            settings.IterationsCountPerStopCheck = 1;
            searcher.Searcher.SetSearchSettings(std::move(settings));

            const auto& searchStopReason = searcher.Search(0_eid);
            UNIT_ASSERT_EQUAL(searchStopReason, EStopReason::ByStopCondition);
            const auto& length_for_5_edge = searcher.GetPathLengthInMeters({5_eid, 0.});
            UNIT_ASSERT_OPTIONAL_DOUBLES_EQUAL(length_for_5_edge, std::optional<double>{}, 0.0001);
        }
    }

    Y_UNIT_TEST(dijkstra_search_rhombus_with_passes) {
        TGraph graph{CreateRhombusGraphWithComplexPasses()};
        graph.BuildEdgeStorage(32);
        TTestForwardSearchHandlers testHandlers(graph);
        TTestFastDijkstraEdgeSearcher searcher(graph, testHandlers);
        // Start not from pass.
        // We could get to edge 4, because we could't drive through passes.
        // Also that why we couldn't get to edge 6, but we could get into passes,
        // that's why edges 2 and 5 are visited.
        searcher.Search(0_eid);

        TExpectedVisitOrder expectedEdgeVisitOrder = {
            0_eid,
            TAnyOrderGroup{
                1_eid,
                2_eid,
            },
            3_eid,
            5_eid};

        testHandlers.PrintEdgeVisitOrder();
        UNIT_ASSERT_EQUAL(testHandlers.TestData->EdgeVisitOrder, expectedEdgeVisitOrder);
    }

    Y_UNIT_TEST(dijkstra_search_rhombus_with_passes_entry_disabled) {
        TGraph graph{CreateRhombusGraphWithComplexPasses()};
        graph.BuildEdgeStorage(32);
        TTestForwardSearchEntryProhibitedHandlers testHandlers(graph);
        TTestFastDijkstraEdgeSearcher searcher(graph, testHandlers);
        searcher.Search(0_eid);

        TExpectedVisitOrder expectedEdgeVisitOrder = {
            0_eid,
            1_eid,
            3_eid};

        testHandlers.PrintEdgeVisitOrder();
        UNIT_ASSERT_EQUAL(testHandlers.TestData->EdgeVisitOrder, expectedEdgeVisitOrder);
    }

    Y_UNIT_TEST(dijkstra_search_rhombus_with_passes_start_from_pass) {
        TGraph graph{CreateRhombusGraphWithComplexPasses()};
        graph.BuildEdgeStorage(32);
        TTestForwardSearchHandlers testHandlers(graph);
        TTestFastDijkstraEdgeSearcher searcher(graph, testHandlers);
        // Start from edge in passes.
        // We go out from pass (edge 4) and could enter the pass (edge 5).
        // But we couldn't go through the pass (go to edge 6 after 5).
        searcher.Search(2_eid);

        std::vector<TEdgeId> expectedEdgeVisitOrder = {
            2_eid,
            4_eid,
            5_eid};

        testHandlers.PrintEdgeVisitOrder();

        UNIT_ASSERT_EQUAL(testHandlers.TestData->EdgeVisitOrder, expectedEdgeVisitOrder);
    }

#if 0
    // TODO: Enable back after fixing resedintial drive-through settings
    Y_UNIT_TEST(dijkstra_search_rhombus_with_passes_disabled_checking) {
            TGraph graph{CreateRhombusGraphWithComplexPasses()};
            graph.BuildEdgeStorage(32);
            TTestForwardSearchHandlers testHandlers(graph);

            // Disable checking crossing the passes.
            NTaxi::NGraphSearch2::TFastSearchSettings settings;
            settings.DisableResidentialDriveThrough = false;

            TTestFastDijkstraEdgeSearcher searcher(graph, settings,  testHandlers);

            // From first edge gonna be all edges except 0, 2, 4.
            searcher.Search(1_eid);
            std::vector<TEdgeId> expectedEdgeVisitOrder = {
                1_eid,
                3_eid,
                5_eid,
                6_eid};
            UNIT_ASSERT_EQUAL(testHandlers.TestData->EdgeVisitOrder, expectedEdgeVisitOrder);

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
            UNIT_ASSERT_EQUAL(testHandlers.TestData->EdgeVisitOrder, expectedEdgeVisitOrder);
    }
#endif

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
        auto graph = BuildGraphForStartFromPositionOnEdge();
        graph.BuildEdgeStorage(32);

        TTestReverseSearchHandlers testHandlers(graph);
        TFastSearchSettings settings;

        TTestFastDijkstraEdgeSearcher searcher(graph, settings, testHandlers);
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
        const TExpectedVisitOrder expectedEdgeVisitOrder = {
            0_eid,
            3_eid,
            5_eid,
            1_eid,
            0_eid,
            TAnyOrderGroup{
                2_eid,
                4_eid,
            },
            7_eid,
            6_eid,
        };

        Cout << "FinalDistances: ";
        for (auto [k, v] : testHandlers.TestData->FinalDistances)
            Cout << k.value() << " " << v << ", " << Endl;
        Cout << "EdgeFinalDistances: ";
        for (auto [k, v] : testHandlers.TestData->EdgeFinalDistances)
            Cout << k.value() << " " << v << ", " << Endl;
        Cout << "PrecedingEdges: ";
        for (auto [k, v] : testHandlers.TestData->PrecedingEdges)
            Cout << k.value() << " " << v.value() << ", " << Endl;
        Cout << "EdgeVisitOrder: ";
        for (auto v : testHandlers.TestData->EdgeVisitOrder)
            Cout << v.value() << ", " << Endl;

        UNIT_ASSERT_EQUAL(testHandlers.TestData->FinalDistances, expectedFinalDistances);
        UNIT_ASSERT_EQUAL(testHandlers.TestData->EdgeFinalDistances, expectedEdgeFinalDistances);
        UNIT_ASSERT_EQUAL(testHandlers.TestData->PrecedingEdges, expectedPrecedingEdges);
        UNIT_ASSERT_EQUAL(testHandlers.TestData->EdgeVisitOrder, expectedEdgeVisitOrder);
    }

    Y_UNIT_TEST(dijkstra_search_from_multiple_positions_on_edges) {
        /*
         *
         *         e0 (5)                   e2 (5)
         *  v0 -----------------> v1 <------------------- v2
         *  ^                    ^  |                     ^
         *  | 40%                |  |                     |
         *  |e3 (5)       e4 (2) |  | e1 (2)              |
         *  X 60%        50/50%  X  |                     |e7 (5)
         *  |                    |  |                     |
         *  |                    |  |                     |
         *  | 40%  e5 (5)  60%   |  v       e6 (5)        |
         *  v3 <-----X----------- v4 -------------------> v5
         *
         *
         *  This time we start searching from the 0.5 of the 4th edge and from
         *  the 0.6 of the 3d and 5th edges simultaneously. Reverse edges option is false.
        */
        auto graph = BuildGraphForStartFromPositionOnEdge();
        graph.BuildEdgeStorage(32);

        TTestForwardSearchHandlers testHandlers(graph);
        TFastSearchSettings settings;

        TTestFastDijkstraEdgeSearcher searcher(graph, settings, testHandlers);
        searcher.Search(TArrayRef<const TPositionOnEdge>{{3_eid, 0.6}, {4_eid, 0.5}, {5_eid, 0.6}});

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
            double expectedLength = 4;
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
            {0_vid, 2},
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
        const TExpectedVisitOrder expectedEdgeVisitOrder = {
            3_eid,
            4_eid,
            5_eid,
            1_eid,
            3_eid,
            0_eid,
            TAnyOrderGroup{
                4_eid,
                5_eid,
            },
            6_eid,
            7_eid,
            2_eid,
        };

        testHandlers.PrintEdgeVisitOrder();
        UNIT_ASSERT_EQUAL(testHandlers.TestData->PrecedingEdges, expectedPrecedingEdges);
        UNIT_ASSERT_EQUAL(testHandlers.TestData->EdgeVisitOrder, expectedEdgeVisitOrder);
        testHandlers.PrintVertexFinalDistances();
        UNIT_ASSERT_EQUAL(testHandlers.TestData->FinalDistances, expectedFinalDistances);
    }

    Y_UNIT_TEST(search_with_jams) {
        TGraph graph{CreateRhombusGraph()};
        graph.BuildEdgeStorage(5);
        TPersistentIndex index{CreateRhombusPersistentIndex()};
        TJams jams(index);

        // add jams to first edge
        jams.AddJam(1_eid, 0.02);

        TTestForwardSearchHandlers testHandlers(graph);

        TTestFastDijkstraEdgeSearcher searcher(graph, testHandlers, &jams);
        searcher.Search(0_eid);

        TExpectedVisitOrder expectedEdgeVisitOrder = {
            0_eid,
            TAnyOrderGroup{
                1_eid,
                2_eid,
            },
            // because of the jam on edge 1, it should be 4_eid, 5_eid and only then 3_eid
            4_eid,
            5_eid,
            3_eid};

        testHandlers.PrintEdgeVisitOrder();
        UNIT_ASSERT_EQUAL(testHandlers.TestData->EdgeVisitOrder, expectedEdgeVisitOrder);
        UNIT_ASSERT_EQUAL(testHandlers.TestData->EdgeFinalDistances[3_eid], 50 /* (1 / 0.02) */);
    }

    Y_UNIT_TEST(search_with_closures) {
        TGraph graph{CreateRhombusGraph()};
        graph.BuildEdgeStorage(5);
        TPersistentIndex index{CreateRhombusPersistentIndex()};
        const auto& now = std::chrono::system_clock::now();
        const auto& some_future_moment = now + std::chrono::hours(10);
        const auto& some_past_moment = now - std::chrono::hours(10);
        TClosures closures(index, now);

        // add closure to 2 edge
        const int kRegion = 0;
        closures.AddClosure(2_eid, kRegion, some_past_moment, some_future_moment);

        UNIT_ASSERT(closures.IsClosedAtMoment(2_eid, now));

        TTestForwardSearchHandlers testHandlers(graph);

        TTestFastDijkstraEdgeSearcher searcher(graph, testHandlers, nullptr, &closures);

        searcher.Search(0_eid);
        searcher.Searcher.PrintPerformanceStats();

        TExpectedVisitOrder expectedEdgeVisitOrder = {
            0_eid,
            1_eid,
            3_eid,
            5_eid};
        // 2_eid and 4_eid are missing because of the closure

        testHandlers.PrintEdgeVisitOrder();
        UNIT_ASSERT_EQUAL(testHandlers.TestData->EdgeVisitOrder, expectedEdgeVisitOrder);
        UNIT_ASSERT(!testHandlers.TestData->EdgeFinalDistances.contains(4_eid));
    }

    Y_UNIT_TEST(search_start_from_edge_with_closure) {
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

        TTestForwardSearchHandlers testHandlers(graph);

        TTestFastDijkstraEdgeSearcher searcher(graph, testHandlers, nullptr, &closures);
        searcher.Search(0_eid);

        // because closures on start edges 0 and 1 not considered,
        // visit order should be as usual
        TExpectedVisitOrder expectedEdgeVisitOrder = {
            0_eid,
            TAnyOrderGroup{
                1_eid,
                2_eid,
            },
            3_eid,
            4_eid,
            5_eid};

        UNIT_ASSERT_EQUAL(testHandlers.TestData->EdgeVisitOrder, expectedEdgeVisitOrder);
    }
}
