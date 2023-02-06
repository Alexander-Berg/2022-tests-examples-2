#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <taxi/graph/libs/graph-test/load_signals_from_file.h>

#include <taxi/graph/external/graph2/lib/conversion.h>
#include <yandex/taxi/graph2/container.h>
#include <yandex/taxi/graph2/graph.h>
#include <yandex/taxi/graph2/api_version.h>


#include <yandex/taxi/graph2/matcher_framework/vector_reader.h>
#include <yandex/taxi/graph2/matcher_framework/matcher_manager.h>
#include <yandex/taxi/graph2/mapmatcher/matcher.h>
#include <yandex/taxi/graph2/predict/predictions_consumer.h>

#include "paths.h"

using NTaxiExternal::NGraph2::TGpsSignal;
using NTaxiExternal::NGraph2::TGraph;
using NTaxiExternal::NGraph2::TId;
using NTaxiExternal::NGraph2::TRoadGraphFileLoader;
using NTaxiExternal::NGraph2::TTimestamp;
using NTaxiExternal::NMapMatcher2::TFilterConfig;
using NTaxiExternal::NMapMatcher2::THeadHypothesesAndBestHeadPredecessors;
using NTaxiExternal::NMapMatcher2::TMatcher2;
using NTaxiExternal::NMapMatcher2::TMatcherConfig;
using NTaxiExternal::NMapMatcher2::TMatcherManager;
using NTaxiExternal::NMapMatcher2::TMatcherManagerSettings;
using NTaxiExternal::NMapMatcher2::TVectorReader;
using NTaxiExternal::NMapMatcher2::TKBestPredictionsConsumerSettings;
using NTaxiExternal::NMapMatcher2::TYagaConsumer;
using NTaxiExternal::NMapMatcher2::TYagaConsumerSettings;
using NTaxiExternal::NPredict::TKBestPredictionsConsumer;
using NTaxiExternal::NPredict::TFuturePositionOnEdge;

struct TKBestPredictionsConsumerTestFixture: public ::NUnitTest::TBaseTestCase {
    TKBestPredictionsConsumerTestFixture()
        : Graph(TestRoadGraph())
        , MatcherConfig(CFG_PATH.c_str())
    {
    }

    TString GraphPath(const TStringBuf& str) {
        static const TString prefix = "taxi/graph/data/graph3/";
        return BinaryPath(prefix + str);
    }

    const TGraph& TestRoadGraph() {
        static TGraph graph(TRoadGraphFileLoader::Create(
            GraphPath("road_graph.fb").c_str(),
            GraphPath("rtree.fb").c_str()));
        graph.BuildEdgeStorage(4);
        return graph;
    }

    TString TestDataPath(const TString& name) {
        return JoinFsPaths(ArcadiaSourceRoot(), "taxi/graph/data/matcher_framework", name);
    }

    const TGraph& Graph;
    const TMatcherConfig MatcherConfig;
    const TMatcherManagerSettings MatcherSettings;
    const TFilterConfig FilterConfig;
};

class TTestKBestPredictionsStoringConsumer: public TKBestPredictionsConsumer {
public:
    std::vector<std::vector<TFuturePositionOnEdge>> Results;
    virtual ~TTestKBestPredictionsStoringConsumer() = default;

    void OnPredictions(const TGpsSignal& signal,
      NTaxiExternal::NGraph2::TContainer<TFuturePositionOnEdge> predictions) override {
        Results.push_back({predictions.begin(), predictions.end()});
    }
};

class TTestYagaStoringConsumer: public TYagaConsumer {
public:
    std::vector<THeadHypothesesAndBestHeadPredecessors> Results;
    virtual ~TTestYagaStoringConsumer() = default;

    void OnAdjustedPosition(const THeadHypothesesAndBestHeadPredecessors& data) override {
        Results.push_back(data);
    }
};


Y_UNIT_TEST_SUITE_F(matcher_framework_kbest_predictions_consumer, TKBestPredictionsConsumerTestFixture) {
    Y_UNIT_TEST(CheckSample_1) {
        const TMatcherConfig matcherConfig(
            CFG_PATH.c_str());
        const TFilterConfig signalsConfig;
        const auto signals = NTaxi::NGraph2::LoadSignalsFromFile(TestDataPath("sample1.json"));

        TVectorReader reader;
        ;
        for (const auto& signal : signals) {
            reader.AddSignal(NTaxiExternal::NGraph2::ToExternal(signal));
        }
        reader.MarkFinished();

        const auto& graph = TestRoadGraph();

        TMatcher2 matcher(graph,
                          (NTaxiExternal::NShortestPath2::TShortestPathData*)nullptr,
                          matcherConfig,
                          signalsConfig);

        TTestKBestPredictionsStoringConsumer consumer;

        TMatcherManager matcherManager(std::move(matcher), MatcherSettings,
                                       consumer, reader,  Graph, 10);
        matcherManager.SetPredictionTargetTime(12'000);
        matcherManager.SetPredictionVariantsCount(5);

        Y_ASSERT(matcherManager.GetPredictionTargetTime() == 12'000);
        Y_ASSERT(matcherManager.GetPredictionVariantsCount() == 5);
        while (matcherManager.MatchChunk() != TMatcherManager::TInputStatus::Finished) {
        }

        Y_ASSERT(consumer.Results.size() >= signals.size() / 2);
        Y_ASSERT(consumer.Results[0].size() > 0);
    }

    Y_UNIT_TEST(CheckSample_1_Constructor_2) {
        const TMatcherConfig matcherConfig(
            CFG_PATH.c_str());
        const TFilterConfig signalsConfig;
        const auto signals = NTaxi::NGraph2::LoadSignalsFromFile(TestDataPath("sample1.json"));

        TVectorReader reader;
        ;
        for (const auto& signal : signals) {
            reader.AddSignal(NTaxiExternal::NGraph2::ToExternal(signal));
        }
        reader.MarkFinished();

        const auto& graph = TestRoadGraph();

        TMatcher2 matcher(graph,
                          (NTaxiExternal::NShortestPath2::TShortestPathData*)nullptr,
                          matcherConfig,
                          signalsConfig);

        TTestKBestPredictionsStoringConsumer consumer;

        TKBestPredictionsConsumerSettings consumerAndSettings{graph, consumer, 10};

        TMatcherManager matcherManager(std::move(matcher), MatcherSettings,
                                       consumerAndSettings, reader);

        matcherManager.SetPredictionTargetTime(12'000);
        matcherManager.SetPredictionVariantsCount(5);

        Y_ASSERT(matcherManager.GetPredictionTargetTime() == 12'000);
        Y_ASSERT(matcherManager.GetPredictionVariantsCount() == 5);
        while (matcherManager.MatchChunk() != TMatcherManager::TInputStatus::Finished) {
        }

        Y_ASSERT(consumer.Results.size() >= signals.size() / 2);
        Y_ASSERT(consumer.Results[0].size() > 0);
    }

    Y_UNIT_TEST(CheckSample_1_WithYaga) {
        const TMatcherConfig matcherConfig(
            CFG_PATH.c_str());
        const TFilterConfig signalsConfig;
        const auto signals = NTaxi::NGraph2::LoadSignalsFromFile(TestDataPath("sample1.json"));

        TVectorReader reader;
        ;
        for (const auto& signal : signals) {
            reader.AddSignal(NTaxiExternal::NGraph2::ToExternal(signal));
        }
        reader.MarkFinished();

        const auto& graph = TestRoadGraph();

        TMatcher2 matcher(graph,
                          (NTaxiExternal::NShortestPath2::TShortestPathData*)nullptr,
                          matcherConfig,
                          signalsConfig);

        TTestKBestPredictionsStoringConsumer consumer;
        TTestYagaStoringConsumer yagaConsumer;

        TKBestPredictionsConsumerSettings consumerAndSettings{graph, consumer, 10};
        TYagaConsumerSettings yagaConsumerAndSettings{graph, yagaConsumer, 10};

        TMatcherManager matcherManager(std::move(matcher), MatcherSettings,
                                       yagaConsumerAndSettings, consumerAndSettings, reader);

        matcherManager.SetPredictionTargetTime(12'000);
        matcherManager.SetPredictionVariantsCount(5);

        Y_ASSERT(matcherManager.GetPredictionTargetTime() == 12'000);
        Y_ASSERT(matcherManager.GetPredictionVariantsCount() == 5);
        while (matcherManager.MatchChunk() != TMatcherManager::TInputStatus::Finished) {
        }

        Y_ASSERT(consumer.Results.size() >= signals.size() / 2);
        Y_ASSERT(yagaConsumer.Results.size() >= signals.size() / 2);
        Y_ASSERT(consumer.Results[0].size() > 0);
    }
}

