#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <library/cpp/json/json_value.h>
#include <library/cpp/json/json_reader.h>

#include <util/stream/file.h>

#include <taxi/graph/libs/graph/graph.h>
#include <taxi/graph/libs/mapmatcher/matcher.h>
#include <taxi/graph/libs/mapmatcher/candidate_graph_debug.h>
#include <taxi/graph/libs/mapmatcher/matcher_config.h>
#include <taxi/graph/libs/mapmatcher/timed_position.h>
#include <taxi/graph/libs/graph/gps_signal.h>

#include <taxi/graph/libs/matcher_framework/matcher_framework.h>
#include <taxi/graph/libs/matcher_framework/yson_stream_reader.h>
#include <taxi/graph/libs/matcher_framework/adjusted_point_consumer.h>
#include <taxi/graph/libs/matcher_framework/adjusted_edges_consumer.h>
#include <taxi/graph/libs/matcher_framework/adjusted_point_provider.h>
#include <taxi/graph/libs/matcher_framework/adjusted_edges_provider.h>
#include <taxi/graph/libs/mapmatcher/matcher.h>

#include <iostream>
#include <fstream>
#include <filesystem>

#include "paths.h"

struct TMatcherFrameworkTestFixture: public ::NUnitTest::TBaseTestCase {
    /* A mix of taxi/graph wrappers and classes from original
     * maps/analyzer/libs/deprecated/mapmatcher library is used.
     * As such, it is easier to put necessary typedefs
     * directly inside class body
     *
     */

    using TAdjustedPointProvider = NTaxi::NMapMatcher2::TAdjustedPointProvider;
    using TAdjustedEdgesProvider = NTaxi::NMapMatcher2::TAdjustedEdgesProvider;
    using TYsonStreamReader = NTaxi::NMapMatcher2::TYsonStreamReader;
    using TInputStatus = NTaxi::NMapMatcher2::TInputStatus;

    using TGraph = NTaxi::NGraph2::TGraph;
    using TGpsSignal = NTaxi::NGraph2::TGpsSignal;
    using TMatcher = NTaxi::NMapMatcher2::TMatcher;
    using TMatcherManager = NTaxi::NMapMatcher2::TMatcherManager<TMatcher>;
    using TMatcherConfig = NTaxi::NMapMatcher2::TMatcherConfig;
    using TMatcherManagerSettings = NTaxi::NMapMatcher2::TMatcherManagerSettings;
    using TFilterConfig = NTaxi::NMapMatcher2::TFilterConfig;
    using TCandidateGraphDebug = NTaxi::NMapMatcher2::TCandidateGraphDebug;
    using TPositionOnEdge = NTaxi::NGraph2::TPositionOnEdge;
    using TPositionOnGraph = NTaxi::NGraph2::TPositionOnGraph;
    using TTimestamp = NTaxi::NGraph2::TTimestamp;
    using TAdjustedEdge = NTaxi::NMapMatcher2::TAdjustedEdge;
    using TTimedPositionOnEdge = NTaxi::NMapMatcher2::TTimedPositionOnEdge;
    using IAdjustedPointConsumer = NTaxi::NMapMatcher2::IAdjustedPointConsumer;
    using IAdjustedEdgesConsumer = NTaxi::NMapMatcher2::IAdjustedEdgesConsumer;
    using IMatcherManagerConsumer = NTaxi::NMapMatcher2::IMatcherManagerConsumer<TMatcher>;
    using TMatcherManagerConsumerSplitter = NTaxi::NMapMatcher2::TMatcherManagerConsumerSplitter;

    class TTestConsumer: public IAdjustedPointConsumer, public IMatcherManagerConsumer, public IAdjustedEdgesConsumer {
    public:
        using IMatcherManagerConsumer::TRejectionInfo;

        TTestConsumer(TTimedPositionOnEdge& output, const TGraph& graph)
            : LastSuccessfulPosition(output)
            , Graph(graph)
        {
        }

        void OnAdjustedEdges(std::span<TAdjustedEdge> edges) final {
            AdjustedEdges.insert(AdjustedEdges.end(), edges.begin(), edges.end());
        }

        void OnAdjustedPosition(const TPositionOnGraph& posOnGraph, TTimestamp timestamp) final {
            ++PushCalled;
            Y_ASSERT(!posOnGraph.IsUndefined());
            LastSuccessfulPosition = {Graph.GetPositionOnEdge(posOnGraph), timestamp};
        }

        void OnAppended(const TGpsSignal& signal, const TMatcher& matcher) final {
            ++OnAppendedCalled;
            if (matcher.GetBestPositionAndNPredecessors(5).Speed) {
                SpeedsObserved++;
            }
        }

        void OnRejected(const TGpsSignal& signal, const TMatcher& matcher, const TRejectionInfo&) final {
            ++OnRejectedCalled;
        }

        void OnInvalid(const TGpsSignal& signal, const TMatcher& matcher) final {
            ++OnInvalidCalled;
        }

        void OnFinished() final {
            ++OnFinishedCalled;
        }
        //private:
        size_t PushCalled = 0;
        size_t OnAppendedCalled = 0;
        size_t OnRejectedCalled = 0;
        size_t OnInvalidCalled = 0;
        size_t OnFinishedCalled = 0;
        size_t SpeedsObserved = 0;
        TVector<TAdjustedEdge> AdjustedEdges;
        TTimedPositionOnEdge& LastSuccessfulPosition;
        const TGraph& Graph;
    };

    const size_t TESTS_NUMBER = 5;

    TMatcherFrameworkTestFixture()
        : graph(std::make_unique<NTaxi::NGraph2::TRoadGraphDataStorage>(
              PATH_TO_ROAD_GRAPH.c_str(), PATH_TO_RTREE.c_str(), EMappingMode::Precharged)) {
    }

    NTaxi::NGraph2::TGraph graph;
};

Y_UNIT_TEST_SUITE_F(matcher_framework_test, TMatcherFrameworkTestFixture) {
    Y_UNIT_TEST(StreamReaderCheck_1) {
        TFileInput file(TestDataPath("sample1.yson"));
        TYsonStreamReader reader(file);
        TVector<TGpsSignal> signals;
        TInputStatus inputStatus = reader.ReadNextChunk(signals);
        Y_ASSERT(inputStatus == TInputStatus::Finished);
        for (size_t i = 0; i < signals.size(); ++i) {
            double ref = static_cast<double>(i);
            UNIT_ASSERT_EQUAL(signals[i].Lat(), ref);
            UNIT_ASSERT_EQUAL(signals[i].Lon(), ref);
            UNIT_ASSERT_EQUAL(signals[i].AverageSpeed(), ref);
            UNIT_ASSERT_EQUAL(signals[i].Direction(), ref);
            UNIT_ASSERT_EQUAL(signals[i].Accuracy(), ref);
            UNIT_ASSERT_EQUAL(signals[i].Time(), static_cast<TTimestamp>(i));
        }
    }

    Y_UNIT_TEST(StreamReaderCheck_2) {
        TFileInput file(TestDataPath("sample2.yson"));
        TYsonStreamReader reader(file);
        reader.SetField(TYsonStreamReader::TGpsColumn::Lat, "custom_latitude");
        reader.SetField(TYsonStreamReader::TGpsColumn::Lon, "custom_longitude");
        TVector<TGpsSignal> signals;
        TInputStatus inputStatus = reader.ReadNextChunk(signals);
        Y_ASSERT(inputStatus == TInputStatus::Finished);
        for (size_t i = 0; i < signals.size(); ++i) {
            UNIT_ASSERT_EQUAL(signals[i].Lat(), static_cast<double>(i));
            UNIT_ASSERT_EQUAL(signals[i].Lon(), static_cast<double>(i));
            UNIT_ASSERT(!signals[i].HasDirection());
            UNIT_ASSERT(!signals[i].HasAccuracy());
        }
    }

    Y_UNIT_TEST(CheckSample) {
        const TMatcherConfig matcherConfig(
            CFG_PATH.c_str());
        TFilterConfig filterConfig;

        auto matcher = std::make_unique<TMatcher>(graph,
                                                  nullptr,
                                                  matcherConfig,
                                                  filterConfig,
                                                  nullptr);

        TTimedPositionOnEdge outputData;
        TFileInput file(TestDataPath("sample3.yson"));
        TMatcherManagerSettings settings = {TMatcherManagerSettings::TThrowPolicy::ReportAndDiscard, TMatcherManagerSettings::TThrowPolicy::ReportAndDiscard};
        std::shared_ptr<TYsonStreamReader> reader = std::make_shared<TYsonStreamReader>(file);
        reader->SetField(TYsonStreamReader::TGpsColumn::Time, "timestamp");

        std::shared_ptr<TTestConsumer> consumer = std::make_shared<TTestConsumer>(outputData, graph);
        std::shared_ptr<TAdjustedPointProvider> provider = std::make_shared<TAdjustedPointProvider>(graph, consumer, TAdjustedPointProvider::TConsumeMode::BeginEnd);
        /// Attach both consumers to splitter
        std::shared_ptr<TMatcherManagerConsumerSplitter> splitter = std::make_shared<TMatcherManagerConsumerSplitter>(provider, consumer);

        TMatcherManager matcherManager(std::move(matcher), settings);
        matcherManager.SetConsumer(splitter);
        matcherManager.SetInputReader(reader);

        matcherManager.MatchAll();

        double refLat = 55.6231965;
        double refLon = 37.61548399;

        Y_ASSERT(!outputData.Position.IsUndefined());

        const auto adjustedPoint = graph.GetCoords(outputData.Position);
        double adjLat = adjustedPoint.Lat;
        double adjLon = adjustedPoint.Lon;

        TMatcherManager::TStatistics matcherStats = matcherManager.GetStatistics();

        UNIT_ASSERT_EQUAL(consumer->OnInvalidCalled, 3);
        UNIT_ASSERT_EQUAL(matcherStats.OutOfOrderCount, 1);
        UNIT_ASSERT_EQUAL(matcherStats.FrozenInTimeCount, 2);
        UNIT_ASSERT_EQUAL(consumer->PushCalled, 40);
        UNIT_ASSERT_EQUAL(consumer->OnAppendedCalled, 50);
        UNIT_ASSERT_EQUAL(consumer->OnRejectedCalled, 3);
        UNIT_ASSERT_EQUAL(consumer->OnFinishedCalled, 1);
        UNIT_ASSERT(consumer->SpeedsObserved > 0);
        UNIT_ASSERT_DOUBLES_EQUAL(adjLat, refLat, 1e-3);
        UNIT_ASSERT_DOUBLES_EQUAL(adjLon, refLon, 1e-3);
    }

    Y_UNIT_TEST(CheckAdjustedEdges) {
        const TMatcherConfig matcherConfig(
            CFG_PATH.c_str());
        TFilterConfig filterConfig;

        auto matcher = std::make_unique<TMatcher>(graph,
                                                  nullptr,
                                                  matcherConfig,
                                                  filterConfig,
                                                  nullptr);

        TTimedPositionOnEdge outputData;
        TFileInput file(TestDataPath("sample3.yson"));
        TMatcherManagerSettings settings = {TMatcherManagerSettings::TThrowPolicy::ReportAndDiscard, TMatcherManagerSettings::TThrowPolicy::ReportAndDiscard};
        std::shared_ptr<TYsonStreamReader> reader = std::make_shared<TYsonStreamReader>(file);
        reader->SetField(TYsonStreamReader::TGpsColumn::Time, "timestamp");

        std::shared_ptr<TTestConsumer> consumer = std::make_shared<TTestConsumer>(outputData, graph);
        std::shared_ptr<TAdjustedEdgesProvider> provider = std::make_shared<TAdjustedEdgesProvider>(graph, consumer);
        std::shared_ptr<TMatcherManagerConsumerSplitter> splitter = std::make_shared<TMatcherManagerConsumerSplitter>(provider, consumer);

        TMatcherManager matcherManager(std::move(matcher), settings);
        matcherManager.SetConsumer(splitter);
        matcherManager.SetInputReader(reader);

        matcherManager.MatchAll();

        for (const auto& edge : consumer->AdjustedEdges) {
            UNIT_ASSERT(edge.StartTimestamp < edge.EndTimestamp);
        }

        UNIT_ASSERT(consumer->AdjustedEdges.size() >= 5);
    }

    Y_UNIT_TEST(CheckStats) {
        const TMatcherConfig matcherConfig(
            CFG_PATH.c_str());
        TFilterConfig filterConfig;

        auto matcher = std::make_unique<TMatcher>(graph,
                                                  nullptr,
                                                  matcherConfig,
                                                  filterConfig,
                                                  nullptr);

        TTimedPositionOnEdge outputData;
        TFileInput file(TestDataPath("sample3.yson"));
        TMatcherManagerSettings settings = {TMatcherManagerSettings::TThrowPolicy::ReportAndDiscard, TMatcherManagerSettings::TThrowPolicy::ReportAndDiscard};
        std::shared_ptr<TYsonStreamReader> reader = std::make_shared<TYsonStreamReader>(file);
        reader->SetField(TYsonStreamReader::TGpsColumn::Time, "timestamp");

        std::shared_ptr<TTestConsumer> consumer = std::make_shared<TTestConsumer>(outputData, graph);
        std::shared_ptr<TAdjustedPointProvider> provider = std::make_shared<TAdjustedPointProvider>(graph, consumer, TAdjustedPointProvider::TConsumeMode::BeginEnd);
        std::shared_ptr<TMatcherManagerConsumerSplitter> splitter = std::make_shared<TMatcherManagerConsumerSplitter>(provider, consumer);

        TMatcherManager matcherManager(std::move(matcher), settings);
        matcherManager.SetConsumer(splitter);
        matcherManager.SetInputReader(reader);

        TMatcherManager::TStatistics accumulatedStatistics;
        TMatcherManager::TStatistics chunkStatistics;
        while (matcherManager.MatchChunk(chunkStatistics) != TInputStatus::Finished) {
            accumulatedStatistics += chunkStatistics;
        }
        accumulatedStatistics += chunkStatistics;

        UNIT_ASSERT_EQUAL(accumulatedStatistics.OutOfOrderCount, 1);
        UNIT_ASSERT_EQUAL(accumulatedStatistics.FrozenInTimeCount, 2);
        UNIT_ASSERT_EQUAL(accumulatedStatistics.AcceptedCount, 50);
        UNIT_ASSERT_EQUAL(accumulatedStatistics.RejectedCount, 3);

        UNIT_ASSERT_EQUAL(consumer->OnInvalidCalled, 3);
        UNIT_ASSERT_EQUAL(consumer->PushCalled, 40);
        UNIT_ASSERT_EQUAL(consumer->OnAppendedCalled, 50);
        UNIT_ASSERT_EQUAL(consumer->OnRejectedCalled, 3);
        UNIT_ASSERT_EQUAL(consumer->OnFinishedCalled, 1);
    }

    Y_UNIT_TEST(CheckThrowIfLess) {
        const TMatcherConfig matcherConfig(
            CFG_PATH.c_str());
        const TFilterConfig filterConfig;

        auto matcher = std::make_unique<TMatcher>(graph,
                                                  nullptr,
                                                  matcherConfig,
                                                  filterConfig,
                                                  nullptr);

        TTimedPositionOnEdge outputData;
        TFileInput file(TestDataPath("sample3.yson"));
        TMatcherManagerSettings settings = {TMatcherManagerSettings::TThrowPolicy::ReportAndDiscard, TMatcherManagerSettings::TThrowPolicy::Throw};
        std::shared_ptr<TYsonStreamReader> reader = std::make_shared<TYsonStreamReader>(file);
        reader->SetField(TYsonStreamReader::TGpsColumn::Time, "timestamp");

        std::shared_ptr<TTestConsumer> consumer = std::make_shared<TTestConsumer>(outputData, graph);
        std::shared_ptr<TAdjustedPointProvider> provider = std::make_shared<TAdjustedPointProvider>(graph, consumer, TAdjustedPointProvider::TConsumeMode::BeginEnd);
        std::shared_ptr<TMatcherManagerConsumerSplitter> splitter = std::make_shared<TMatcherManagerConsumerSplitter>(provider, consumer);

        TMatcherManager matcherManager(std::move(matcher), settings);
        matcherManager.SetConsumer(splitter);
        matcherManager.SetInputReader(reader);

        UNIT_CHECK_GENERATED_EXCEPTION(matcherManager.MatchAll(), std::runtime_error);
    }

    Y_UNIT_TEST(CheckThrowIfEquals) {
        const TMatcherConfig matcherConfig(
            CFG_PATH.c_str());

        const TFilterConfig filterConfig;

        auto matcher = std::make_unique<TMatcher>(graph,
                                                  nullptr,
                                                  matcherConfig,
                                                  filterConfig,
                                                  nullptr);

        TTimedPositionOnEdge outputData;
        TFileInput file(TestDataPath("sample3.yson"));
        TMatcherManagerSettings settings = {TMatcherManagerSettings::TThrowPolicy::Throw, TMatcherManagerSettings::TThrowPolicy::ReportAndDiscard};
        std::shared_ptr<TYsonStreamReader> reader = std::make_shared<TYsonStreamReader>(file);
        reader->SetField(TYsonStreamReader::TGpsColumn::Time, "timestamp");

        std::shared_ptr<TTestConsumer> consumer = std::make_shared<TTestConsumer>(outputData, graph);
        std::shared_ptr<TAdjustedPointProvider> provider = std::make_shared<TAdjustedPointProvider>(graph, consumer, TAdjustedPointProvider::TConsumeMode::BeginEnd);
        std::shared_ptr<TMatcherManagerConsumerSplitter> splitter = std::make_shared<TMatcherManagerConsumerSplitter>(provider, consumer);
        TMatcherManager matcherManager(std::move(matcher), settings);
        matcherManager.SetConsumer(splitter);
        matcherManager.SetInputReader(reader);

        UNIT_CHECK_GENERATED_EXCEPTION(matcherManager.MatchAll(), std::runtime_error);
    }
}
