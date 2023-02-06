#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <library/cpp/json/json_value.h>
#include <library/cpp/json/json_reader.h>

#include <taxi/graph/libs/graph/graph.h>
#include <taxi/graph/libs/graph/gps_signal.h>
#include <taxi/graph/libs/graph/point.h>

#include <taxi/graph/libs/mapmatcher/matcher.h>
#include <taxi/graph/libs/mapmatcher/candidate_graph_debug.h>
#include <taxi/graph/libs/mapmatcher/matcher_config.h>
#include <taxi/graph/libs/mapmatcher/timed_position.h>

#include <taxi/graph/libs/matcher_framework/matcher_framework.h>
#include <taxi/graph/libs/predict/predictor_provider.h>
#include <taxi/graph/libs/matcher_framework/vector_reader.h>

#include <taxi/graph/libs/graph-test/graph_test_data.h>
#include <taxi/graph/libs/graph-test/load_signals_from_file.h>

#include <util/folder/path.h>
#include <util/stream/file.h>

#include <iostream>
#include <fstream>
#include <filesystem>

#include "paths.h"

struct TMatcherFrameworkPredictTestFixture: public ::NUnitTest::TBaseTestCase,
                                             NTaxi::NGraph2::TGraphTestData {
    /* A mix of taxi/graph wrappers and classes from original
     * maps/analyzer/libs/deprecated/mapmatcher library is used.
     * As such, it is easier to put necessary typedefs
     * directly inside class body
     */
    using TMatcher = NTaxi::NMapMatcher2::TMatcher;
    using TMatcherConfig = NTaxi::NMapMatcher2::TMatcherConfig;
    using TFilterConfig = NTaxi::NMapMatcher2::TFilterConfig;
    using TMatcherManager = NTaxi::NMapMatcher2::TMatcherManager<TMatcher>;
    using TMatcherManagerSettings = NTaxi::NMapMatcher2::TMatcherManagerSettings;
    using TVectorReader = NTaxi::NMapMatcher2::TVectorReader;

    using TGraph = NTaxi::NGraph2::TGraph;
    using TTimestamp = NTaxi::NGraph2::TTimestamp;
    using TGpsSignal = NTaxi::NGraph2::TGpsSignal;
    using TPoint = NTaxi::NGraph2::TPoint;
    using TPositionOnEdge = NTaxi::NGraph2::TPositionOnEdge;
    using TPositionOnGraph = NTaxi::NGraph2::TPositionOnGraph;
    using TPredictorProvider = NTaxi::NPredict::TPredictorProvider<NTaxi::NGraph2::TGraphFacadeCommon>;
    using IPredictorConsumer = NTaxi::NPredict::IPredictorConsumer;

    class TTestConsumer: public IPredictorConsumer {
    public:
        virtual ~TTestConsumer() = default;

        void ProcessCandidate(const NTaxi::NPredict::TCandidateInfo& /*cand*/,
                                      TTimestamp /*candidateTimestamp*/,
                                      const TGpsSignal& /*signal*/) override {
            ++CandidatesCount;
        }

        void Reset() {
            CandidatesCount = 0;
        }

        size_t CandidatesCount = 0;
    };

    TMatcherFrameworkPredictTestFixture()
        : Graph(GetTestRoadGraph(TWithEdgeStorage::Yes))
        , MatcherConfig(CFG_PATH.c_str())
        , MatcherSettings{
              TMatcherManagerSettings::TThrowPolicy::ReportAndDiscard,
              TMatcherManagerSettings::TThrowPolicy::ReportAndDiscard} {
    }

    std::shared_ptr<TVectorReader> LoadSignalsFromFile(const TString& filename) {
        auto signals = NTaxi::NGraph2::LoadSignalsFromFile(filename, false);
        std::shared_ptr<TVectorReader> result = std::make_shared<TVectorReader>();

        for (const auto& signal : signals) {
            result->AddSignal(std::move(signal));
        }
        result->MarkFinished();

        return result;
    }

    const TGraph& Graph;
    const TMatcherConfig MatcherConfig;
    const TMatcherManagerSettings MatcherSettings;
    const TFilterConfig FilterConfig;
};

Y_UNIT_TEST_SUITE_F(matcher_framework_predict_test, TMatcherFrameworkPredictTestFixture) {
    Y_UNIT_TEST(CheckHasPrediction) {
        auto matcher = std::make_unique<TMatcher>(Graph,
                                                  MatcherConfig,
                                                  FilterConfig,
                                                  nullptr);

        std::shared_ptr<TTestConsumer> consumer = std::make_shared<TTestConsumer>();
        std::shared_ptr<TPredictorProvider> provider = std::make_shared<TPredictorProvider>(NTaxi::NGraph2::TGraphFacadeCommon{Graph, Graph.GetEdgeStorage()}, consumer);
        const auto& reader = LoadSignalsFromFile(TestDataPath("sample1.json"));

        TMatcherManager matcherManager(std::move(matcher), MatcherSettings, provider, reader);
        matcherManager.MatchAll();

        UNIT_ASSERT_GT(consumer->CandidatesCount, 0);
    }
    Y_UNIT_TEST(DisablePrediction) {
        auto matcher = std::make_unique<TMatcher>(Graph,
                                                  MatcherConfig,
                                                  FilterConfig,
                                                  nullptr);

        std::shared_ptr<TTestConsumer> consumer = std::make_shared<TTestConsumer>();
        std::shared_ptr<TPredictorProvider> provider = std::make_shared<TPredictorProvider>(NTaxi::NGraph2::TGraphFacadeCommon{Graph, Graph.GetEdgeStorage()}, consumer);
        // Disabling prediction
        provider->SetPredictionTargetTime(std::chrono::seconds{0});
        const auto& reader = LoadSignalsFromFile(TestDataPath("sample1.json"));

        TMatcherManager matcherManager(std::move(matcher), MatcherSettings, provider, reader);
        matcherManager.MatchAll();

        UNIT_ASSERT(consumer->CandidatesCount == 0);
    }
    Y_UNIT_TEST(PredictionForRejectedSignal) {
        auto matcher = std::make_unique<TMatcher>(Graph,
                                                  MatcherConfig,
                                                  FilterConfig,
                                                  nullptr);

        std::shared_ptr<TTestConsumer> consumer = std::make_shared<TTestConsumer>();
        std::shared_ptr<TPredictorProvider> provider = std::make_shared<TPredictorProvider>(NTaxi::NGraph2::TGraphFacadeCommon{Graph, Graph.GetEdgeStorage()}, consumer);
        std::shared_ptr<TVectorReader> reader = std::make_shared<TVectorReader>();
        TMatcherManager matcherManager(std::move(matcher), MatcherSettings, provider, reader);
        const auto& signals = NTaxi::NGraph2::LoadSignalsFromFile(TestDataPath("sample1.json"), false);

        NTaxi::NGraph2::TGpsSignal duplicatedSignal = signals[0];
        reader->AddSignal(signals[0]);
        matcherManager.MatchChunk();
        UNIT_ASSERT_GT(consumer->CandidatesCount, 0);

        reader->AddSignal(duplicatedSignal);
        matcherManager.MatchChunk();
        UNIT_ASSERT_GT(consumer->CandidatesCount, 0);
    }
    Y_UNIT_TEST(PredictionForRejectedSignalAfterALongTime) {
        auto matcher = std::make_unique<TMatcher>(Graph,
                                                  MatcherConfig,
                                                  FilterConfig,
                                                  nullptr);

        std::shared_ptr<TTestConsumer> consumer = std::make_shared<TTestConsumer>();
        std::shared_ptr<TPredictorProvider> provider = std::make_shared<TPredictorProvider>(NTaxi::NGraph2::TGraphFacadeCommon{Graph, Graph.GetEdgeStorage()}, consumer);
        std::shared_ptr<TVectorReader> reader = std::make_shared<TVectorReader>();
        TMatcherManager matcherManager(std::move(matcher), MatcherSettings, provider, reader);
        const auto& signals = NTaxi::NGraph2::LoadSignalsFromFile(TestDataPath("sample4.json"), false);

        for (const auto& signal: signals) {
            reader->AddSignal(signal);
            matcherManager.MatchChunk();
            Cout << "consumer->CandidatesCount is " << consumer->CandidatesCount << Endl;
            UNIT_ASSERT_GT(consumer->CandidatesCount, 0);
            consumer->Reset();
        }
    }
}
