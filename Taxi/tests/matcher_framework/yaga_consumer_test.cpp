#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <taxi/graph/libs/graph-test/load_signals_from_file.h>

#include <taxi/graph/external/graph2/lib/conversion.h>
#include <yandex/taxi/graph2/container.h>
#include <yandex/taxi/graph2/graph.h>
#include <yandex/taxi/graph2/api_version.h>

#include <yandex/taxi/graph2/mapmatcher/matcher.h>

#include <yandex/taxi/graph2/matcher_framework/vector_reader.h>
#include <yandex/taxi/graph2/matcher_framework/yaga_consumer.h>
#include <yandex/taxi/graph2/matcher_framework/matcher_manager.h>
#include <yandex/taxi/graph2/matcher_framework/matcher_managers_selector.h>
#include <yandex/taxi/graph2/mapmatcher/matcher.h>
#include <yandex/taxi/graph2/nearest_edges2/nearest_edges_matcher.h>

#include "paths.h"

using NTaxiExternal::NGraph2::TGpsSignal;
using NTaxiExternal::NGraph2::TGraph;
using NTaxiExternal::NGraph2::TId;
using NTaxiExternal::NGraph2::TRoadGraphFileLoader;
using NTaxiExternal::NGraph2::TTimestamp;
using NTaxiExternal::NGraph2::TNearestEdgesMatcher;
using NTaxiExternal::NGraph2::TNearestEdgesMatcherSettings;
using NTaxiExternal::NMapMatcher2::TFilterConfig;
using NTaxiExternal::NMapMatcher2::THeadHypothesesAndBestHeadPredecessors;
using NTaxiExternal::NMapMatcher2::TMatcher2;
using NTaxiExternal::NMapMatcher2::TMatcherConfig;
using NTaxiExternal::NMapMatcher2::TMatcherManager;
using NTaxiExternal::NMapMatcher2::TMatcherManagerSettings;
using NTaxiExternal::NMapMatcher2::TVectorReader;
using NTaxiExternal::NMapMatcher2::TYagaConsumer;
using NTaxiExternal::NMapMatcher2::TYagaConsumerSettings;
using NTaxiExternal::NMapMatcher2::TYagaPosition;
using NTaxiExternal::NPredict::TFuturePositionOnEdge;
using NTaxiExternal::NMapMatcher2::IConsumerBase;
using NTaxiExternal::NMapMatcher2::TMatcherManagersSelector;

struct TMatchedFrameworkYagaConsumerTestFixture: public ::NUnitTest::TBaseTestCase {
    TMatchedFrameworkYagaConsumerTestFixture()
        : Graph(TestRoadGraph())
        , MatcherConfig(CFG_PATH.c_str())
    {
    }

    TString GraphPath(const TStringBuf& str) {
        static const TString prefix = "taxi/graph/data/graph3/";
        return BinaryPath(prefix + str);
    }

    const TGraph& TestRoadGraph() {
        static const TGraph graph(TRoadGraphFileLoader::Create(
            GraphPath("road_graph.fb").c_str(),
            GraphPath("rtree.fb").c_str()));
        return graph;
    }

    const TGraph& TestRoadGraphWithInitializedEdgeStorage() {
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

class TTestYagaStoringConsumer: public TYagaConsumer {
public:
    std::vector<THeadHypothesesAndBestHeadPredecessors> Results;
    virtual ~TTestYagaStoringConsumer() = default;

    void OnAdjustedPosition(const THeadHypothesesAndBestHeadPredecessors& data) override {
        Results.push_back(data);
    }
};

class TTestSelectorConsumer: public IConsumerBase {
public:
    std::vector<THeadHypothesesAndBestHeadPredecessors> ResultsAdjusted;
    std::vector<std::vector<TFuturePositionOnEdge>> ResultsPredicted;
    virtual ~TTestSelectorConsumer() = default;

    void OnAdjustedPosition(const THeadHypothesesAndBestHeadPredecessors& data) override {
        ResultsAdjusted.push_back(data);
    }

    void OnPredictions(const TGpsSignal& signal,
      NTaxiExternal::NGraph2::TContainer<TFuturePositionOnEdge> predictions) override {
        ResultsPredicted.push_back({predictions.begin(), predictions.end()});
    }
};

Y_UNIT_TEST_SUITE_F(matcher_framework_yaga_consumer, TMatchedFrameworkYagaConsumerTestFixture) {
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

        TTestYagaStoringConsumer consumer;

        TMatcherManager matcherManager(std::move(matcher), MatcherSettings,
                                       consumer, reader, 2, Graph);
        while (matcherManager.MatchChunk() != TMatcherManager::TInputStatus::Finished) {
        }

        Y_ASSERT(consumer.Results.size() == signals.size());
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

        TTestYagaStoringConsumer consumer;

        TYagaConsumerSettings consumerAndSettings{graph, consumer, 2};

        TMatcherManager matcherManager(std::move(matcher), MatcherSettings,
                                       consumerAndSettings, reader);
        while (matcherManager.MatchChunk() != TMatcherManager::TInputStatus::Finished) {
        }

        Y_ASSERT(consumer.Results.size() == signals.size());
    }

    Y_UNIT_TEST(CheckSampleNearestEdgeMatcher_1) {
        const TMatcherConfig matcherConfig(
            CFG_PATH.c_str());
        const auto signals = NTaxi::NGraph2::LoadSignalsFromFile(TestDataPath("sample1.json"));

        TVectorReader reader;

        for (const auto& signal : signals) {
            reader.AddSignal(NTaxiExternal::NGraph2::ToExternal(signal));
        }
        reader.MarkFinished();

        const auto& graph = TestRoadGraph();

        TNearestEdgesMatcher matcher(graph,
                          TNearestEdgesMatcherSettings(20, 5));

        Y_VERIFY_DEBUG(matcher.GetPimpl() != nullptr);

        TTestYagaStoringConsumer consumer;

        TMatcherManager matcherManager(std::move(matcher), MatcherSettings,
                                       consumer, reader);
        while (matcherManager.MatchChunk() != TMatcherManager::TInputStatus::Finished) {
        }

        Y_ASSERT(consumer.Results.size() == signals.size());
    }

    Y_UNIT_TEST(CheckSample_1_WithSelector) {
        const TMatcherConfig matcherConfig(
            CFG_PATH.c_str());
        const TFilterConfig signalsConfig;
        const auto signals = NTaxi::NGraph2::LoadSignalsFromFile(TestDataPath("sample1.json"));

        const auto& graph = TestRoadGraphWithInitializedEdgeStorage();

        TTestSelectorConsumer firstMainConsumer;

        TMatcherManagersSelector selector{graph, MatcherSettings, firstMainConsumer, 10, nullptr, matcherConfig, signalsConfig};

        selector.AddCommonMatcherManagerWithPredictions(graph, MatcherSettings, 10, 10'000, nullptr, matcherConfig, signalsConfig);

        for (const auto& signal : signals) {
            selector.AddSignal(NTaxiExternal::NGraph2::ToExternal(signal));
        }

        selector.SetPredictionTargetTime(12'000);
        selector.SetPredictionVariantsCount(5);

        Y_ASSERT(selector.GetPredictionTargetTime() == 12'000);
        Y_ASSERT(selector.GetPredictionVariantsCount() == 5);

        selector.ForceFlushOnYield();

        TTestSelectorConsumer secondMainConsumer;
        TTestSelectorConsumer experimentalConsumer;

        selector.SetMainMatcherManagerType(TMatcherManagersSelector::MatcherManagerType::CommonMapMatcherWithPredictions);
        selector.SetExperimentalMatcherManagerType(TMatcherManagersSelector::MatcherManagerType::CommonMapMatcherWithPredictions);

        selector.SetMainConsumer(secondMainConsumer);
        selector.SetExperimentalConsumer(experimentalConsumer);

        for (const auto& signal : signals) {
            selector.AddSignal(NTaxiExternal::NGraph2::ToExternal(signal));
        }

        selector.ForceFlushOnYield();

        Y_ASSERT(firstMainConsumer.ResultsAdjusted.size() >= signals.size() / 2);
        Y_ASSERT(firstMainConsumer.ResultsAdjusted.size() == secondMainConsumer.ResultsAdjusted.size());
        Y_ASSERT(experimentalConsumer.ResultsPredicted.size() >= signals.size() / 2);
        Y_ASSERT(experimentalConsumer.ResultsPredicted[0].size() > 0);
    }

    Y_UNIT_TEST(CheckSampleNearestEdgeMatcher_1_WithSelector) {
        const TMatcherConfig matcherConfig(
            CFG_PATH.c_str());
        const TFilterConfig signalsConfig;
        const auto signals = NTaxi::NGraph2::LoadSignalsFromFile(TestDataPath("sample1.json"));

        const auto& graph = TestRoadGraphWithInitializedEdgeStorage();

        TTestSelectorConsumer firstMainConsumer;

        TMatcherManagersSelector selector{graph, MatcherSettings, firstMainConsumer, 10, nullptr, matcherConfig, signalsConfig};

        selector.AddNearestEdgesManager(graph, MatcherSettings, 20, 5);

        for (const auto& signal : signals) {
            selector.AddSignal(NTaxiExternal::NGraph2::ToExternal(signal));
        }

        selector.ForceFlushOnYield();

        TTestSelectorConsumer mainConsumer;
        TTestSelectorConsumer experimentalConsumer;

        selector.SetMainMatcherManagerType(TMatcherManagersSelector::MatcherManagerType::NearestEdgesMatcher);
        selector.SetExperimentalMatcherManagerType(TMatcherManagersSelector::MatcherManagerType::NearestEdgesMatcher);

        selector.SetMainConsumer(mainConsumer);
        selector.SetExperimentalConsumer(experimentalConsumer);

        for (const auto& signal : signals) {
            selector.AddSignal(NTaxiExternal::NGraph2::ToExternal(signal));
        }

        selector.ForceFlushOnYield();

        Y_ASSERT(firstMainConsumer.ResultsAdjusted.size() >= signals.size() / 2);
        Y_ASSERT(mainConsumer.ResultsAdjusted.size() == firstMainConsumer.ResultsAdjusted.size());
        Y_ASSERT(mainConsumer.ResultsAdjusted.size() == experimentalConsumer.ResultsAdjusted.size());
    }

    Y_UNIT_TEST(CheckSample_1_WithSelectorAndConstructorWithTwoConsumers) {
        const TMatcherConfig matcherConfig(
            CFG_PATH.c_str());
        const TFilterConfig signalsConfig;
        const auto signals = NTaxi::NGraph2::LoadSignalsFromFile(TestDataPath("sample1.json"));

        const auto& graph = TestRoadGraphWithInitializedEdgeStorage();

        TTestSelectorConsumer mainConsumer;
        TTestSelectorConsumer experimentalConsumer;

        TMatcherManagersSelector selector{graph, MatcherSettings, mainConsumer, experimentalConsumer, 10, nullptr, matcherConfig, signalsConfig};

        selector.AddCommonMatcherManagerWithPredictions(graph, MatcherSettings, 10, 10'000, nullptr, matcherConfig, signalsConfig);
        selector.SetMainMatcherManagerType(TMatcherManagersSelector::MatcherManagerType::CommonMapMatcherWithPredictions);
        selector.SetExperimentalMatcherManagerType(TMatcherManagersSelector::MatcherManagerType::CommonMapMatcherWithPredictions);

        for (const auto& signal : signals) {
            selector.AddSignal(NTaxiExternal::NGraph2::ToExternal(signal));
        }

        selector.ForceFlushOnYield();

        Y_ASSERT(mainConsumer.ResultsAdjusted.size() >= signals.size() / 2);
        Y_ASSERT(experimentalConsumer.ResultsPredicted.size() >= signals.size() / 2);
        Y_ASSERT(experimentalConsumer.ResultsPredicted[0].size() > 0);
    }

    Y_UNIT_TEST(CheckSample_1_WithSelectorSwitchFromSplitter) {
        const TMatcherConfig matcherConfig(
            CFG_PATH.c_str());
        const TFilterConfig signalsConfig;
        const auto signals1 = NTaxi::NGraph2::LoadSignalsFromFile(TestDataPath("sample1.json"));
        auto signals2 = signals1;

        // increase time
        for (auto& signal: signals2) {
            signal.SetTime(signal.Time() + 1'000);
        }

        const auto& graph = TestRoadGraphWithInitializedEdgeStorage();

        TTestSelectorConsumer mainConsumer;
        TTestSelectorConsumer experimentalConsumer;

        TMatcherManagersSelector selector{graph, MatcherSettings, mainConsumer, experimentalConsumer, 10, nullptr, matcherConfig, signalsConfig};

        selector.AddCommonMatcherManagerWithPredictions(graph, MatcherSettings, 10, 10'000, nullptr, matcherConfig, signalsConfig);
        selector.AddNearestEdgesManager(graph, MatcherSettings, 20, 5);
        selector.SetMainMatcherManagerType(TMatcherManagersSelector::MatcherManagerType::CommonMapMatcherWithPredictions);
        selector.SetExperimentalMatcherManagerType(TMatcherManagersSelector::MatcherManagerType::CommonMapMatcherWithPredictions);

        for (const auto& signal : signals1) {
            selector.AddSignal(NTaxiExternal::NGraph2::ToExternal(signal));
        }

        selector.ForceFlushOnYield();

        Y_ASSERT(mainConsumer.ResultsAdjusted.size() >= signals1.size() / 2);
        Y_ASSERT(experimentalConsumer.ResultsPredicted.size() >= signals1.size() / 2);
        Y_ASSERT(experimentalConsumer.ResultsPredicted[0].size() > 0);

        auto beforeSwitchMainAdjusted = mainConsumer.ResultsAdjusted.size();
        auto beforeSwitchMainPredicted = mainConsumer.ResultsPredicted.size();
        auto beforeSwitchExperimentalAdjusted = experimentalConsumer.ResultsAdjusted.size();
        auto beforeSwitchExperimentalPredicted = experimentalConsumer.ResultsPredicted.size();

        selector.SetExperimentalMatcherManagerType(TMatcherManagersSelector::MatcherManagerType::NearestEdgesMatcher);

        for (const auto& signal : signals2) {
            selector.AddSignal(NTaxiExternal::NGraph2::ToExternal(signal));
        }

        selector.ForceFlushOnYield();

        Y_ASSERT(mainConsumer.ResultsAdjusted.size() == beforeSwitchMainAdjusted * 2);
        Y_ASSERT(mainConsumer.ResultsPredicted.size() == beforeSwitchMainPredicted * 2);
        Y_ASSERT(experimentalConsumer.ResultsAdjusted.size() == beforeSwitchExperimentalAdjusted * 2);
        Y_ASSERT(experimentalConsumer.ResultsPredicted.size() == beforeSwitchExperimentalPredicted);

        // Set Splitter again
        selector.SetExperimentalMatcherManagerType(TMatcherManagersSelector::MatcherManagerType::CommonMapMatcherWithPredictions);

        // Switch from splitter on main channel
        selector.SetMainMatcherManagerType(TMatcherManagersSelector::MatcherManagerType::CommonMapMatcher);

        // increase time again
        for (auto& signal: signals2) {
            signal.SetTime(signal.Time() + 1'000);
        }

        for (const auto& signal : signals2) {
            selector.AddSignal(NTaxiExternal::NGraph2::ToExternal(signal));
        }

        selector.ForceFlushOnYield();

        Y_ASSERT(mainConsumer.ResultsAdjusted.size() == beforeSwitchMainAdjusted * 3);
        Y_ASSERT(mainConsumer.ResultsPredicted.size() == beforeSwitchMainPredicted * 2);
        Y_ASSERT(experimentalConsumer.ResultsAdjusted.size() == beforeSwitchExperimentalAdjusted * 3);
        Y_ASSERT(experimentalConsumer.ResultsPredicted.size() == beforeSwitchExperimentalPredicted * 2);
    }
}
