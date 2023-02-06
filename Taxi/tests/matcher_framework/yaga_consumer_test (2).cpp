#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <library/cpp/json/json_value.h>

#include <taxi/graph/libs/graph/graph.h>
#include <taxi/graph/libs/graph/gps_signal.h>
#include <taxi/graph/libs/graph/point.h>
#include <taxi/graph/libs/graph/persistent_index.h>
#include <taxi/graph/libs/graph/graph_data_builder.h>

#include <taxi/graph/libs/graph-test/graph_test_data.h>
#include <taxi/graph/libs/graph-test/load_signals_from_file.h>

#include <taxi/graph/libs/matcher_framework/vector_reader.h>
#include <taxi/graph/libs/matcher_framework/yaga_consumer.h>
#include <taxi/graph/libs/matcher_framework/yaga_provider.h>
#include <taxi/graph/libs/matcher_framework/matcher_framework.h>
#include <taxi/graph/libs/mapmatcher/matcher.h>
#include <taxi/graph/libs/mapmatcher/timed_position.h>
#include "paths.h"

using NTaxi::NGraph2::TGpsSignal;
using NTaxi::NGraph2::TGraph;
using NTaxi::NGraph2::TId;
using NTaxi::NGraph2::TPositionOnEdge;
using NTaxi::NGraph2::TPositionOnGraph;
using NTaxi::NGraph2::TPossiblePositionOnEdge;
using NTaxi::NGraph2::TTimestamp;
using NTaxi::NMapMatcher2::TMatcher;
using NTaxi::NMapMatcher2::IMatcherManagerConsumer;
using NTaxi::NMapMatcher2::IYagaConsumer;
using NTaxi::NMapMatcher2::TFilterConfig;
using NTaxi::NMapMatcher2::THeadHypothesesAndBestHeadPredecessors;
using NTaxi::NMapMatcher2::TMatcher;
using NTaxi::NMapMatcher2::TMatcherConfig;
using NTaxi::NMapMatcher2::TMatcherManager;
using NTaxi::NMapMatcher2::TMatcherManagerSettings;
using NTaxi::NMapMatcher2::TTimedPositionOnEdge;
using NTaxi::NMapMatcher2::TVectorReader;
using NTaxi::NMapMatcher2::TYagaPosition;
using NTaxi::NMapMatcher2::TYagaProvider;
using NTaxi::NMapMatcher2::NYagaAux::TYagaMatchedPointsHistory;

namespace {
    // GRAPH
    // V0 ---> V1
    //     |
    //     E0, E1, E2, E3, E4 (five same edges)
    TGraph CreateTestGraph() {
        auto builder = std::make_unique<NTaxi::NGraph2::TRoadGraphDataBuilder>(2, 5, 0);
        for (size_t i = 0; i < 2; ++i) {
            double coord = i;
            builder->SetVertexGeometry(maps::road_graph::VertexId(i), {coord, coord});
        }
        const std::vector<ui32> edge_sources_data = {0, 0, 0, 0, 0};
        const std::vector<ui32> edge_targets_data = {1, 1, 1, 1, 1};
        std::vector<double> edge_lengths;
        for (unsigned int i = 0; i < edge_sources_data.size(); ++i) {
            edge_lengths.push_back(1.);
        }

        const auto& edge_sources = edge_sources_data;
        const auto& edge_targets = edge_targets_data;

        NTaxi::NGraph2::TPolyline fake_polyline;
        fake_polyline.AddPoint({0., 0.});
        fake_polyline.AddPoint({1., 1.});
        for (ui32 i = 0; i < edge_sources.size(); ++i) {
            builder->SetEdge(NTaxi::NGraph2::TEdge(
                                 NTaxi::NGraph2::TEdgeId{i},
                                 NTaxi::NGraph2::TVertexId{edge_sources[i]},
                                 NTaxi::NGraph2::TVertexId{edge_targets[i]}),
                             true);
            builder->SetEdgeData(NTaxi::NGraph2::TEdgeId{i}, NTaxi::NGraph2::TEdgeData{1., edge_lengths[i]}, fake_polyline);
        }

        builder->Build();
        return TGraph(std::move(builder));
    };

    // Used for return values
    struct TMatchedPathForTest {
        NTaxi::NGraph2::TGpsSignal StartSignal;
        NTaxi::NGraph2::TGpsSignal EndSignal;
        NTaxi::NShortestPath2::TPath Path;

        operator IMatcherManagerConsumer<TMatcher>::TMatchedPath() const {
            return IMatcherManagerConsumer<TMatcher>::TMatchedPath{StartSignal, EndSignal, Path};
        }
    };

    class TTestReader: public TVectorReader {
    public:
        using TVectorReader::TVectorReader;

        NTaxi::NMapMatcher2::TInputStatus ReadNextChunk(TVector<TGpsSignal>& signalsOutput) override {
            if (SignalsOriginal.empty()) {
                SignalsOriginal = Signals;
            }
            return TVectorReader::ReadNextChunk(signalsOutput);
        }

        const TVector<TGpsSignal> GetSignals() const {
            return SignalsOriginal;
        }

    private:
        TVector<TGpsSignal> SignalsOriginal;
    };

    class TTestAdditionalHeadHypothesesYagaConsumer: public IYagaConsumer {
    public:
        TTestAdditionalHeadHypothesesYagaConsumer() {
        }
        virtual ~TTestAdditionalHeadHypothesesYagaConsumer() = default;

        void OnAdjustedPosition(const THeadHypothesesAndBestHeadPredecessors& data) override {
            LastHeadsAmount = data.HeadHypotheses.size();
        }

        size_t GetLastHeadsAmount() const {
            return LastHeadsAmount;
        }

    private:
        size_t LastHeadsAmount = 0;
    };

    class TTestYagaStoringConsumer: public IYagaConsumer {
    public:
        std::vector<THeadHypothesesAndBestHeadPredecessors> Results;
        virtual ~TTestYagaStoringConsumer() = default;

        void OnAdjustedPosition(const THeadHypothesesAndBestHeadPredecessors& data) override {
            Results.push_back(data);
        }
    };
}

struct TMatchedFrameworkYagaConsumerTestFixture: public ::NUnitTest::TBaseTestCase {
    TMatchedFrameworkYagaConsumerTestFixture()
        : graph(CreateTestGraph())
        , matcherConfig(CFG_PATH.c_str())
        , matcherSettings{
              TMatcherManagerSettings::TThrowPolicy::ReportAndDiscard,
              TMatcherManagerSettings::TThrowPolicy::ReportAndDiscard} {
    }

    TGraph graph;
    const TMatcherConfig matcherConfig;
    const TMatcherManagerSettings matcherSettings;
    const TFilterConfig filterConfig;
};

static inline TGpsSignal CreateSignal(const NTaxi::NGraph2::TTimestamp timestamp) {
    TGpsSignal signal;
    signal.SetLat(0);
    signal.SetLon(0);
    signal.SetTime(timestamp);
    return signal;
}

static inline TTimedPositionOnEdge CreateTimedPositionOnEdge(const TTimestamp timestamp,
                                                             const NTaxi::NGraph2::TId edgeId, double position) {
    TTimedPositionOnEdge pos;
    pos.Timestamp = timestamp;
    pos.Position = TPositionOnEdge(edgeId, position);
    return pos;
}

static inline TMatchedPathForTest CreatePath(const TTimestamp start, const TTimestamp end,
                                             const TId edgeId, const TGraph& graph) {
    TGpsSignal startSignal = CreateSignal(start);
    TGpsSignal endSignal = CreateSignal(end);
    TPositionOnEdge startPosOnEdge(edgeId, 0.);
    TPositionOnEdge endPosOnEdge(edgeId, 1.);
    TVector<TId> edges = {edgeId};
    NTaxi::NShortestPath2::TPath shortPath(graph.GetPositionOnGraph(startPosOnEdge),
                                           graph.GetPositionOnGraph(endPosOnEdge), edges, graph);
    TMatchedPathForTest path{std::move(startSignal), std::move(endSignal), std::move(shortPath)};
    return path;
}

Y_UNIT_TEST_SUITE_F(matcher_framework_yaga_consumer, TMatchedFrameworkYagaConsumerTestFixture) {
    Y_UNIT_TEST(CheckYagaConsumerAdditionalHeadHypothesesMaxCount) {
        constexpr const size_t predecessorsCount = 15;

        for (size_t i = 0; i < 10; ++i) {
            auto matcher = std::make_unique<TMatcher>(graph,
                                                      nullptr,
                                                      matcherConfig,
                                                      filterConfig,
                                                      nullptr);
            std::shared_ptr<TTestAdditionalHeadHypothesesYagaConsumer> consumer = std::make_shared<TTestAdditionalHeadHypothesesYagaConsumer>();
            auto processing = std::make_shared<TYagaProvider>(predecessorsCount, graph, consumer);
            processing->SetAdditionalHeadHypothesesMaxCount(i);
            std::shared_ptr<TVectorReader> reader = std::make_shared<TVectorReader>();
            reader->AddSignal(CreateSignal(0));
            reader->MarkFinished();

            TMatcherManager<TMatcher> matcherManager(std::move(matcher), matcherSettings,
                                           processing, reader);
            matcherManager.MatchAll();

            // if we have 5 edges, than we can have maximum 6 heads (1 best + 5 heads from each edge)
            constexpr size_t maxShouldBe = 1 + 5;
            const size_t shouldBe = std::min(1 + i, maxShouldBe);
            UNIT_ASSERT_EQUAL(consumer->GetLastHeadsAmount(), shouldBe);
        }
    }

    Y_UNIT_TEST(CheckMatcherManagerHistoryCorrectEnriching) {
        const size_t historyMaxSize = 10;
        TYagaMatchedPointsHistory history(historyMaxSize, graph);

        // match 7 paths on same edge but with different timestamps
        // instead of 2 * 7 = 14 points we should have only 8 (for timestamps 1, 2, 3, 4, 5, 6, 7, 8) in our history
        history.MatchPath(CreatePath(1, 2, TId{0}, graph));
        history.MatchPath(CreatePath(2, 3, TId{0}, graph));
        history.MatchPath(CreatePath(3, 4, TId{0}, graph));
        history.MatchPath(CreatePath(4, 5, TId{0}, graph));
        history.MatchPath(CreatePath(5, 6, TId{0}, graph));
        history.MatchPath(CreatePath(6, 7, TId{0}, graph));
        history.MatchPath(CreatePath(7, 8, TId{0}, graph));
        UNIT_ASSERT_EQUAL_C(history.Size(), 8, "History size " << history.Size() << " should equal 8");

        {
            TVector<TTimedPositionOnEdge> lastPoints;
            // we should have timestamps (3, 4, 5, 6, 7, 8) in lastPoints
            history.EnrichByLastKPoints(lastPoints, 6);

            UNIT_ASSERT_EQUAL_C(lastPoints.size(), 6,
                                "lastPoints.size() " << lastPoints.size() << " should be equal to 6");
            TVector<TTimestamp> targetValues = {3, 4, 5, 6, 7, 8};
            for (size_t i = 0; i < lastPoints.size(); ++i) {
                const auto& pt = lastPoints[i];
                const TTimestamp& shouldBeValue = targetValues[i];
                UNIT_ASSERT_EQUAL_C(pt.Timestamp, shouldBeValue,
                                    "Point timestamp " << pt.Timestamp << " differs from required value "
                                                       << shouldBeValue);
            }
        }

        history.MatchPath(CreatePath(10, 11, TId{0}, graph));
        history.MatchPath(CreatePath(11, 12, TId{0}, graph));
        history.MatchPath(CreatePath(12, 13, TId{0}, graph));
        history.MatchPath(CreatePath(13, 14, TId{0}, graph));
        UNIT_ASSERT_EQUAL_C(history.Size(), historyMaxSize, "history.Size() " << history.Size() << " should be equal to history max size " << historyMaxSize);

        {
            TVector<TTimedPositionOnEdge> lastPoints;
            history.EnrichByLastKPoints(lastPoints, 2 * historyMaxSize);
            UNIT_ASSERT_EQUAL_C(lastPoints.size(), historyMaxSize,
                                "lastPoints.size() " << lastPoints.size() << " should be equal to history max size " << historyMaxSize);
            TVector<TTimestamp> targetValues = {4, 5, 6, 7, 8, 10, 11, 12, 13, 14};
            for (size_t i = 0; i < lastPoints.size(); ++i) {
                const auto& pt = lastPoints[i];
                const TTimestamp& shouldBeValue = targetValues[i];
                UNIT_ASSERT_EQUAL_C(pt.Timestamp, shouldBeValue,
                                    "Point timestamp " << pt.Timestamp << " differs from required value "
                                                       << shouldBeValue);
            }
        }
    }

    Y_UNIT_TEST(CheckFunctionLeaveOnlyKNewestIfNeed) {
        {
            TVector<size_t> victim({1, 2, 3, 4, 5, 6, 7, 8, 9, 10});
            NTaxi::NMapMatcher2::NYagaAux::LeaveOnlyKNewestIfNeed(victim, 5);

            UNIT_ASSERT_EQUAL_C(victim.size(), 5, "Victim.size() " << victim.size() << " should be 5");
            TVector<size_t> target({6, 7, 8, 9, 10});
            for (size_t i = 0; i < 5; i++) {
                UNIT_ASSERT_EQUAL_C(victim[i], target[i], "Victim[" << i << "] should be " << target[i]);
            }
        }

        {
            TVector<size_t> victim({1, 2, 3, 4, 5, 6, 7, 8, 9, 10});
            NTaxi::NMapMatcher2::NYagaAux::LeaveOnlyKNewestIfNeed(victim, 0);
            UNIT_ASSERT_C(victim.empty(), "Victim should be empty");
        }
    }

    Y_UNIT_TEST(CheckProcessMatcherResult) {
        const size_t desiredPredecessorsCount = 5;
        // imitate some history
        const size_t historyMaxSize = 10;
        TYagaMatchedPointsHistory history(historyMaxSize, graph);
        // In matched history should be points with timestamps (10, 11, 12, 13, 14)
        history.MatchPath(CreatePath(10, 11, TId{0}, graph));
        history.MatchPath(CreatePath(11, 12, TId{0}, graph));
        history.MatchPath(CreatePath(12, 13, TId{0}, graph));
        history.MatchPath(CreatePath(13, 14, TId{0}, graph));

        {
            // not enough predecessors case
            // Create matcher result
            // [0] - bestHead
            // [1], ..., [2] - predecessors
            TMatcher::TBestPositionAndPredecessors matcherResult;
            matcherResult.BestPositionAndPredecessors.push_back(CreateTimedPositionOnEdge(20, TId{0}, 0));
            matcherResult.BestPositionAndPredecessors.push_back(CreateTimedPositionOnEdge(19, TId{0}, 0.5));
            matcherResult.BestPositionAndPredecessors.push_back(CreateTimedPositionOnEdge(18, TId{0}, 1.));

            THeadHypothesesAndBestHeadPredecessors result = NTaxi::NMapMatcher2::NYagaAux::ProcessMatcherResult(
                std::move(matcherResult), history, desiredPredecessorsCount);

            UNIT_ASSERT_GE_C(result.HeadHypotheses.size(), 1,
                             "headHypotheses.size() " << result.HeadHypotheses.size() << " should be >= 1");
            UNIT_ASSERT_EQUAL_C(result.HeadTimestamp, 20,
                                "bestHead.Timestamp " << result.HeadTimestamp
                                                      << " should be equal 20");

            UNIT_ASSERT_EQUAL_C(result.BestHeadPredecessors.size(), desiredPredecessorsCount,
                                "bestHeadPredecessors.size() " << result.BestHeadPredecessors.size()
                                                               << " should be equal " << desiredPredecessorsCount);

            TVector<TTimestamp> targetValues = {12, 13, 14, 18, 19};
            for (size_t i = 0; i < desiredPredecessorsCount; ++i) {
                UNIT_ASSERT_EQUAL_C(result.BestHeadPredecessors[i].Timestamp, targetValues[i],
                                    "predecessors[" << i << "] " << result.BestHeadPredecessors[i].Timestamp
                                                    << " should be " << targetValues[i]);
            }
        }

        {
            // enough predecessors case
            // Create matcher result
            // [0] - bestHead
            // [1], ..., [5] - predecessors
            TMatcher::TBestPositionAndPredecessors matcherResult;
            matcherResult.BestPositionAndPredecessors.push_back(CreateTimedPositionOnEdge(10, TId{0}, 1));
            matcherResult.BestPositionAndPredecessors.push_back(CreateTimedPositionOnEdge(7, TId{0}, 1));
            matcherResult.BestPositionAndPredecessors.push_back(CreateTimedPositionOnEdge(6, TId{0}, 1));
            matcherResult.BestPositionAndPredecessors.push_back(CreateTimedPositionOnEdge(5, TId{0}, 1));
            matcherResult.BestPositionAndPredecessors.push_back(CreateTimedPositionOnEdge(4, TId{0}, 1));
            matcherResult.BestPositionAndPredecessors.push_back(CreateTimedPositionOnEdge(2, TId{0}, 1));

            THeadHypothesesAndBestHeadPredecessors result = NTaxi::NMapMatcher2::NYagaAux::ProcessMatcherResult(
                std::move(matcherResult), history, desiredPredecessorsCount);

            UNIT_ASSERT_EQUAL_C(result.HeadHypotheses.size(), 1,
                                "headHypotheses.size() " << result.HeadHypotheses.size());
            UNIT_ASSERT_EQUAL_C(result.HeadTimestamp, 10,
                                "bestHead.Timestamp " << result.HeadTimestamp
                                                      << " should be equal 10");

            UNIT_ASSERT_EQUAL_C(result.BestHeadPredecessors.size(), desiredPredecessorsCount,
                                "bestHeadPredecessors.size() " << result.BestHeadPredecessors.size()
                                                               << " should be equal " << desiredPredecessorsCount);

            TVector<TTimestamp> targetValues = {2, 4, 5, 6, 7};
            for (size_t i = 0; i < desiredPredecessorsCount; ++i) {
                UNIT_ASSERT_EQUAL_C(result.BestHeadPredecessors[i].Timestamp, targetValues[i],
                                    "predecessors[" << i << "] " << result.BestHeadPredecessors[i].Timestamp
                                                    << " should be " << targetValues[i]);
            }
        }
    }

    Y_UNIT_TEST(CheckRejectSignal) {
        const size_t predecessorsCount = 5;
        const TTimestamp bestHeadTimestamp = 20;

        THeadHypothesesAndBestHeadPredecessors lastResult;
        TTimedPositionOnEdge headTmp = CreateTimedPositionOnEdge(bestHeadTimestamp, TId{0}, 1);
        TPossiblePositionOnEdge head(headTmp.Position, 1.0);
        lastResult.HeadHypotheses.push_back(TYagaPosition{head, 1007});
        lastResult.HeadTimestamp = bestHeadTimestamp;
        lastResult.BestHeadPredecessors.push_back(CreateTimedPositionOnEdge(5, TId{0}, 1));
        lastResult.BestHeadPredecessors.push_back(CreateTimedPositionOnEdge(6, TId{0}, 1));
        lastResult.BestHeadPredecessors.push_back(CreateTimedPositionOnEdge(7, TId{0}, 1));
        lastResult.BestHeadPredecessors.push_back(CreateTimedPositionOnEdge(8, TId{0}, 1));
        lastResult.BestHeadPredecessors.push_back(CreateTimedPositionOnEdge(9, TId{0}, 1));

        TGpsSignal signal;
        signal.SetTime(100);

        TYagaProvider::TRejectionInfo info{true};

        NTaxi::NMapMatcher2::NYagaAux::RejectSignal(signal, lastResult, predecessorsCount, info);

        UNIT_ASSERT_EQUAL_C(lastResult.HeadHypotheses.size(), 1, "headHypotheses.size() << " << lastResult.HeadHypotheses.size() << " should be equal to 1");
        UNIT_ASSERT_EQUAL_C(lastResult.HeadTimestamp, signal.Time(), "bestHead timestamp " << lastResult.HeadTimestamp << " should be equal to last signal timestamp " << signal.Time());

        // predecessors size <= 2 * predecessorsCount (check RejectSignal impl)
        UNIT_ASSERT_EQUAL_C(lastResult.BestHeadPredecessors.size(), predecessorsCount + 1, "bestHeadPredecessors.size() << " << lastResult.BestHeadPredecessors.size() << " should be equal to " << predecessorsCount);

        UNIT_ASSERT_EQUAL_C(*lastResult.HeadHypotheses.front().Speed, 0., "bestHead speed should equals to zero if driver is not moving");

        TVector<TTimestamp> targetValues = {5, 6, 7, 8, 9, 20};
        for (size_t i = 0; i < predecessorsCount + 1; ++i) {
            UNIT_ASSERT_EQUAL_C(lastResult.BestHeadPredecessors[i].Timestamp, targetValues[i],
                                "predecessors[" << i << "] " << lastResult.BestHeadPredecessors[i].Timestamp
                                                << " should be " << targetValues[i]);
        }
    }

    Y_UNIT_TEST(CheckSample_1) {
        const TMatcherConfig matcherConfig(
            CFG_PATH.c_str());
        const TFilterConfig signalsConfig;
        const auto signals = NTaxi::NGraph2::LoadSignalsFromFile(TestDataPath("sample1.json"));

        std::shared_ptr<TVectorReader> reader = std::make_shared<TVectorReader>();
        for (const auto& signal : signals) {
            reader->AddSignal(signal);
        }
        reader->MarkFinished();

        const auto& graph = NTaxi::NGraph2::TGraphTestData{}.GetTestRoadGraph();

        auto matcher = std::make_unique<TMatcher>(graph,
                                                  nullptr,
                                                  matcherConfig,
                                                  signalsConfig,
                                                  nullptr);

        std::shared_ptr<TTestYagaStoringConsumer> consumer = std::make_shared<TTestYagaStoringConsumer>();
        auto processing = std::make_shared<TYagaProvider>(5, graph, consumer);

        TMatcherManager<TMatcher> matcherManager(std::move(matcher), matcherSettings,
                                       processing, reader);
        matcherManager.MatchAll();

        Y_ASSERT(consumer->Results.size() == signals.size());
    }
}
