#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <taxi/graph/libs/graph/graph_data_builder.h>
#include <taxi/graph/libs/search2/dijkstra_edge_searcher.h>
#include <taxi/graph/libs/search2/surge_index_edge_processor.h>
#include <taxi/graph/libs/search2/transformator.h>

#include <iostream>

#include <taxi/graph/libs/graph-test/graph_test_data.h>

#include <util/stream/file.h>

#include "common.h"

using NTaxi::NGraph2::TClosures;
using NTaxi::NGraph2::TJams;
using NTaxi::NGraph2::TEdge;
using NTaxi::NGraph2::TEdgeData;
using NTaxi::NGraph2::TEdgeId;
using NTaxi::NGraph2::TGraph;
using NTaxi::NGraph2::TId;
using NTaxi::NGraph2::TPoint;
using NTaxi::NGraph2::TPositionOnEdge;
using NTaxi::NGraph2::TSurgeZoneIndex;
using NTaxi::NGraph2::TVertexId;
using NTaxi::NGraph2::TZoneId;
using NTaxi::NGraphSearch2::DirectionizedEdgeStart;
using NTaxi::NGraphSearch2::SearchState;
using NTaxi::NGraphSearch2::TFastSearchSettings;
using NTaxi::NGraphSearch2::TSurgeIndexEdgeProcessor;
using NTaxi::NGraphSearch2::TTime;

using namespace NTaxi::NGraph2Literals;

namespace {
    class TTestSurgeSearchCallback {
    public:
        explicit TTestSurgeSearchCallback() = default;

    public:
        SearchState operator()(const TTime timeToZone,
                               const TPositionOnEdge& zoneEntryPoint, const TZoneId zoneId) {
            ZoneEntryPoints[zoneId] = zoneEntryPoint;
            FoundDistances[zoneId] = timeToZone.count();

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
            FoundDistances.clear();
        }

    private:
        std::unordered_map<TZoneId, TPositionOnEdge> ZoneEntryPoints;
        std::unordered_map<TZoneId, double> FoundDistances;
    };

    const TFastSearchSettings TEST_SETTINGS{
        [] {
            TFastSearchSettings result;
            result.MaxVisitedEdgesCount = 10'000u;
            return result;
        }()};

    template <typename TSearchTraits, typename TCallback>
    struct TTestSurgeFastDijkstraEdgeSearcher {
        TTestSurgeFastDijkstraEdgeSearcher(const TGraph& graph,
                                           const TFastSearchSettings& settings,
                                           const TSurgeZoneIndex& surgeZoneIndex,
                                           TCallback& callback,
                                           const TJams* jamsPtr = nullptr,
                                           const TClosures* closuresPtr = nullptr)
            : Graph(graph)
            , EdgeProcessor(surgeZoneIndex, callback)
            , Searcher({graph, graph.GetEdgeStorage()}, settings, EdgeProcessor, jamsPtr, closuresPtr)
        {
        }

        template <typename... Args>
        auto Search(Args&&... args) {
            return Searcher.Search(std::forward<Args>(args)...);
        }

        auto Search(TPositionOnEdge posOnEdge) {
            TVector<TPositionOnEdge> startEdges;
            startEdges.push_back(posOnEdge);
            return Search(startEdges);
        }

        const TGraph& Graph;

        using TTestEdgeProcessor =
            NTaxi::NGraphSearch2::TSurgeIndexEdgeProcessor<TCallback>;

        TTestEdgeProcessor EdgeProcessor;

        using TSearcher =
            NTaxi::NGraphSearch2::TFastDijkstraEdgeSearcher<
                NTaxi::NGraph2::TGraphFacadeCommon,
                TSearchTraits,
                TTestEdgeProcessor>;
        TSearcher Searcher;
    };

    template <typename Traits>
    struct TTestSurgeIndexSearcher {
        using MyTraits = Traits;
        using MyCallback = TTestSurgeSearchCallback;
        using MyEdgeProcessor = NTaxi::NGraphSearch2::TSurgeIndexEdgeProcessor<MyCallback>;
        using MySearcher = NTaxi::NGraphSearch2::TFastDijkstraEdgeSearcher<
            NTaxi::NGraph2::TGraphFacadeCommon,
            MyTraits,
            MyEdgeProcessor,
            NTaxi::NGraphSearch2::DijkstraSearchNoDebugHandlers>;

        static constexpr unsigned char MyFlags = Traits::MyFlags;

        MyEdgeProcessor Processor;
        MySearcher Searcher;

        TTestSurgeIndexSearcher(const TGraph& graph, const NTaxi::NGraphSearch2::TFastSearchSettings& settings, 
                            const TSurgeZoneIndex& index, MyCallback& callback,
                            const TJams* jamsPtr, const TClosures* closuresPtr)
            : Processor(index, callback)
            , Searcher({graph, graph.GetEdgeStorage()}, settings, Processor, jamsPtr, closuresPtr, {})
        {
        }
    };

    class TTestSurgeIndexSearcherCreator {
    private:
        TTestSurgeSearchCallback& Callback;
        const TSurgeZoneIndex& Index;

    public:
        TTestSurgeIndexSearcherCreator(TTestSurgeSearchCallback& callback, const TSurgeZoneIndex& index)
            : Callback(callback)
            , Index(index)
        {
        }

        template<typename TTarget>
        auto operator()(
                const TGraph& graph,
                const TFastSearchSettings& settings,
                const TJams* jamsPtr,
                const TClosures* closuresPtr) const {
            return std::make_unique<TTarget>(graph, settings, Index, Callback, jamsPtr, closuresPtr);
        };
    };

    template<typename TTraits>
    using TSurgeIndexTarget = TTestSurgeIndexSearcher<TTraits>;

    using TTestSurgeIndexTransformator = NTaxi::NGraphSearch2::TTransformator<
        TTestSearchTraitsFlags,
        TTestSearchTraitsToFlagsConverter,
        TTestSearchTraitsWithFlags,
        TSurgeIndexTarget>;
}

class TGraphSurgeSearchFixture: public ::NUnitTest::TBaseTestCase, public NTaxi::NGraph2::TGraphTestData {
};

Y_UNIT_TEST_SUITE_F(graph_surge_search, TGraphSurgeSearchFixture) {
    Y_UNIT_TEST(TestSurgeForwardSearchOnRhombusGraph) {
        TGraph graph{CreateRhombusRoadGraph()};
        graph.BuildEdgeStorage(32);

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
            for (const auto& item : expected) {
                std::cout << item.first << ' ' << item.second.ZoneId << ' ' << item.second.StartPosition << ' ' << item.second.EndPosition << '\n';
            }
            std::cout << "actual:\n";
            for (const auto& item : actual) {
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

        TTestSurgeSearchCallback foundCallback;
        TTestSurgeFastDijkstraEdgeSearcher<TTestForwardSearchTraits, TTestSurgeSearchCallback> searcher(graph, TEST_SETTINGS, index, foundCallback);
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
            auto distance = foundDistances.at(id);
            std::cout << id << ": " << distance << std::endl;
        }

        UNIT_ASSERT(true);
    } // Y_UNIT_TEST(TestSurgeForwardSearchOnRhombusGraph)

    Y_UNIT_TEST(TestSurgeForwardSearchDistancesToZones) {
        TGraph graph{CreateTriangleRoadGraph()};
        graph.BuildEdgeStorage(32);

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

        TTestSurgeSearchCallback foundCallback;
        TTestSurgeFastDijkstraEdgeSearcher<TTestForwardSearchTraits, TTestSurgeSearchCallback> searcher(graph, TEST_SETTINGS, index, foundCallback);

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

        std::unordered_map<TZoneId, double> expectedDistances;
        expectedDistances[TZoneId(0)] = 0;
        expectedDistances[TZoneId(1)] = 3.4;
        expectedDistances[TZoneId(2)] = 0;
        expectedDistances[TZoneId(3)] = 0.4;
        expectedDistances[TZoneId(4)] = 2.8732;
        expectedDistances[TZoneId(5)] = 0;

        const auto& actualDistances = foundCallback.GetFoundDistances();

        for (int i = 0; i < 6; ++i) {
            auto id = TZoneId(i);
            auto expected = expectedDistances.at(id);
            auto actual = actualDistances.at(id);
            UNIT_ASSERT_DOUBLES_EQUAL(expected, actual, 1e-3);
            std::cout << id << ": " << actual << std::endl;
        }

        UNIT_ASSERT(true);
    } // Y_UNIT_TEST(TestSurgeForwardSearchDistancesToZones)

    Y_UNIT_TEST(TestSurgeReverseSearchOnRhombusGraph) {
        TGraph graph{CreateRhombusRoadGraph()};
        graph.BuildEdgeStorage(32);

        // Visualization: https://wiki.yandex-team.ru/users/mesyarik/test-na-poisk-blizhajjshix-shestiugolnikov/ but edges are reversed!
        TSurgeZoneIndex index(graph);

        // red hexagon - zone id 0
        index.AddHexagonalZone({0.0, 1.0}, 0.5);

        // orange hexagon - zone id 1
        index.AddHexagonalZone({0.75, 0.0}, 0.75);

        // green hexagon - zone id 2
        index.AddHexagonalZone({-0.5, -0.5}, 1.0);

        // purple hexagon - zone id 3
        index.AddHexagonalZone({0.0, -1.5}, 0.6);

        TTestSurgeSearchCallback foundCallback;
        TTestSurgeFastDijkstraEdgeSearcher<TTestReverseSearchTraits, TTestSurgeSearchCallback> searcher(graph, TEST_SETTINGS, index, foundCallback);
        searcher.Search(TPositionOnEdge{5_eid, 1});

        std::unordered_map<TZoneId, TPositionOnEdge> expectedEntryPoints;
        expectedEntryPoints[TZoneId(0)] = {2_eid, 0.316976};
        expectedEntryPoints[TZoneId(1)] = {4_eid, 0.633982};
        expectedEntryPoints[TZoneId(2)] = {5_eid, 0.366025};
        expectedEntryPoints[TZoneId(3)] = {5_eid, 1};

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
            auto distance = foundDistances.at(id);
            std::cout << id << ": " << distance << std::endl;
        }

        UNIT_ASSERT(true);
    } // Y_UNIT_TEST(TestSurgeReverseSearchOnRhombusGraph)

    Y_UNIT_TEST(TestSurgeReverseSearchDistancesToZones) {
        TGraph graph{CreateTriangleRoadGraph()};
        graph.BuildEdgeStorage(32);

        TSurgeZoneIndex index(graph);

        // visualization: https://wiki.yandex-team.ru/users/mesyarik/test-na-rasstojanija-pri-poiske-shestiugolnikov/ but edges are reversed!
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

        TTestSurgeSearchCallback foundCallback;
        TTestSurgeFastDijkstraEdgeSearcher<TTestReverseSearchTraits, TTestSurgeSearchCallback> searcher(graph, TEST_SETTINGS, index, foundCallback);

        searcher.Search(TPositionOnEdge{0_eid, 0.5});

        std::unordered_map<TZoneId, TPositionOnEdge> expectedEntryPoints;
        expectedEntryPoints[TZoneId(0)] = {0_eid, 0.5};
        expectedEntryPoints[TZoneId(1)] = {0_eid, 0.4};
        expectedEntryPoints[TZoneId(2)] = {0_eid, 0.5};
        expectedEntryPoints[TZoneId(3)] = {0_eid, 0.9};
        expectedEntryPoints[TZoneId(4)] = {0_eid, 0.1};
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

        std::unordered_map<TZoneId, double> expectedDistances;
        expectedDistances[TZoneId(0)] = 0;
        expectedDistances[TZoneId(1)] = 0.2;
        expectedDistances[TZoneId(2)] = 0;
        expectedDistances[TZoneId(3)] = 3.2;
        expectedDistances[TZoneId(4)] = 0.8;
        expectedDistances[TZoneId(5)] = 0;

        const auto& actualDistances = foundCallback.GetFoundDistances();

        for (int i = 0; i < 6; ++i) {
            auto id = TZoneId(i);
            auto expected = expectedDistances.at(id);
            auto actual = actualDistances.at(id);
            UNIT_ASSERT_DOUBLES_EQUAL(expected, actual, 1e-3);
            std::cout << id << ": " << actual << std::endl;
        }

        UNIT_ASSERT(true);
    } // Y_UNIT_TEST(TestSurgeReverseSearchDistancesToZones)

    Y_UNIT_TEST(TestTransformatorAndChangeSettingsInSearcher) {
        TGraph graph{CreateTriangleRoadGraph()};
        graph.BuildEdgeStorage(32);

        TSurgeZoneIndex index(graph);

        // visualization: https://wiki.yandex-team.ru/users/mesyarik/test-na-rasstojanija-pri-poiske-shestiugolnikov/ but edges are reversed!
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

        TTestSurgeSearchCallback foundCallback;
        TTestSurgeIndexSearcherCreator creator(foundCallback, index);
        auto currentSettings = TTestSettings{};

        // Creating searcher
        auto searcher = TTestSurgeIndexTransformator::CreateTarget(creator, graph, currentSettings);

        // Check that searcher has appropriate traits
        UNIT_ASSERT_EQUAL(searcher.GetCurrentFlags(), TTestSearchTraitsToFlagsConverter::GetFlags(currentSettings));

        searcher.Search({0_eid, 0.5});

        foundCallback.Reset();
        currentSettings.TrackEdgeLeeway = false;

        // CHange Settings
        searcher.SetSearchSettings(currentSettings);

        // Check that searcher has appropriate traits
        UNIT_ASSERT_EQUAL(searcher.GetCurrentFlags(), TTestSearchTraitsToFlagsConverter::GetFlags(currentSettings));

        searcher.Search({0_eid, 0.5});
    } // Y_UNIT_TEST(TestTransformatorAndChangeSettingsInSearcher)
}
