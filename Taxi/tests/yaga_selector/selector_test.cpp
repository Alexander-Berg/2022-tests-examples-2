#include <library/cpp/iterator/enumerate.h>
#include <library/cpp/testing/gtest/gtest.h>
#include <library/cpp/testing/unittest/env.h>

#include <util/folder/path.h>

#include <taxi/graph/libs/yaga_selector/matcher_managers_selector.h>
#include <taxi/graph/libs/graph-test/graph_test_data.h>
#include <taxi/graph/libs/graph/persistent_index.h>
#include <taxi/graph/libs/graph-test/load_signals_from_file.h>

#include <algorithm>

class TYagaSelectorTestFixture: public NTaxi::NGraph2::TGraphTestData, public testing::Test {
public:
    using TGraph = NTaxi::NGraph2::TGraph;
    using TPersistentIndex = NTaxi::NGraph2::TPersistentIndex;
    using TMatcherConfig = NTaxi::NMapMatcher2::TMatcherConfig;
    using TMatcherManagerSettings = NTaxi::NMapMatcher2::TMatcherManagerSettings;
    using TFilterConfig = NTaxi::NMapMatcher2::TFilterConfig;
    using TMatcherManagersSelector = NTaxi::NYagaSelector::TMatcherManagersSelector;

    class TTestSelectorConsumer: public NTaxi::NYagaSelector::ICommonConsumer {
    public:
        std::vector<NTaxi::NYagaSelector::THypotheses> Results;
        virtual ~TTestSelectorConsumer() = default;

        void OnPositions(const NTaxi::NYagaSelector::THypotheses& data) override {
            Results.push_back(data);
        }
    };

    // static void SetUpTestSuite() { }
    // static void TearDownTestSuite() { }

    const std::string CFG_PATH = JoinFsPaths(ArcadiaSourceRoot(), "taxi/graph/data/conf/mapmatcher/online.json");
    inline std::string TestDataPath(const TString& name) {
        return JoinFsPaths(ArcadiaSourceRoot(), "taxi/graph/data/matcher_framework", name);
    }

    TYagaSelectorTestFixture()
        : Graph(GetTestRoadGraph(TWithEdgeStorage::Yes))
    {
    }

    const TGraph& Graph;
};

TEST_F(TYagaSelectorTestFixture, CheckSample_1_WithSelectorSwitch) {
    const TMatcherConfig matcherConfig(CFG_PATH.c_str());
    const TFilterConfig filterConfig;
    const auto signals1 = NTaxi::NGraph2::LoadSignalsFromFile(TestDataPath("sample1.json"));
    auto signals2 = signals1;

    // increase time
    for (auto& signal : signals2) {
        signal.SetTime(signal.Time() + 1'000);
    }

    auto mainConsumer = std::make_shared<TTestSelectorConsumer>();
    auto experimentalConsumer = std::make_shared<TTestSelectorConsumer>();

    TPersistentIndex index(
            GraphPath("edges_persistent_index.fb").data());

    TMatcherManagersSelector selector{Graph,
                                      TMatcherManagerSettings{TMatcherManagerSettings::TThrowPolicy::ReportAndDiscard, TMatcherManagerSettings::TThrowPolicy::ReportAndDiscard},
                                      nullptr, matcherConfig, filterConfig, index, nullptr};
    // Order does matter, don't change
    selector.AddConsumer(mainConsumer);
    selector.AddConsumer(experimentalConsumer);

    selector.SetMainSettings(NTaxi::NYagaSelector::TYagaAdjustSettings{});
    selector.SetExperimentalSettings(NTaxi::NYagaSelector::TYagaPredictSettings{10, 10});

    for (const auto& signal : signals1) {
        selector.AddSignal(signal);
    }

    selector.ForceFlushOnYield();

    EXPECT_GE(mainConsumer->Results.size(), signals1.size() / 2);
    EXPECT_GE(experimentalConsumer->Results.size(), signals1.size() / 2);
    EXPECT_GT(experimentalConsumer->Results[0].Hypotheses.size(), 0ul);

    auto beforeSwitchAdjusted = mainConsumer->Results.size();
    auto beforeSwitchPredicted = experimentalConsumer->Results.size();

    selector.SetExperimentalSettings(NTaxi::NYagaSelector::TNearestEdgesSettings{20, 5});

    for (const auto& signal : signals2) {
        selector.AddSignal(signal);
    }

    selector.ForceFlushOnYield();

    EXPECT_EQ(mainConsumer->Results.size(), beforeSwitchAdjusted * 2);
    EXPECT_EQ(experimentalConsumer->Results.size(), beforeSwitchPredicted * 2);

    selector.SetExperimentalSettings(NTaxi::NYagaSelector::TMapPredictSettings{10'000, NTaxi::NPredict::EPredictStrategy::kTime, {std::chrono::milliseconds{10'000}}});

    selector.SetMainSettings(NTaxi::NYagaSelector::TMapPredictSettings{10'000, NTaxi::NPredict::EPredictStrategy::kDistance, {std::chrono::milliseconds{3'000}, std::chrono::milliseconds{10'000}}});

    // increase time again
    for (auto& signal : signals2) {
        signal.SetTime(signal.Time() + 1'000);
    }

    for (const auto& signal : signals2) {
        selector.AddSignal(signal);
    }

    selector.ForceFlushOnYield();

    EXPECT_EQ(mainConsumer->Results.size(), beforeSwitchAdjusted * 3);
    EXPECT_EQ(experimentalConsumer->Results.size(), beforeSwitchPredicted * 3);

    selector.SetExperimentalSettings(NTaxi::NYagaSelector::TYagaPredictSettings{.K = 10, .PredictionTargetMilliSeconds = 20'000});

    selector.SetMainSettings(NTaxi::NYagaSelector::TGuidanceSettings{});

    // increase time again
    for (auto& signal : signals2) {
        signal.SetTime(signal.Time() + 1'000);
    }

    for (const auto& signal : signals2) {
        selector.AddSignal(signal);
    }

    selector.ForceFlushOnYield();

    EXPECT_EQ(mainConsumer->Results.size(), beforeSwitchAdjusted * 4);
    EXPECT_EQ(experimentalConsumer->Results.size(), beforeSwitchPredicted * 4);
}

TEST_F(TYagaSelectorTestFixture, MapPredictCheckDifferentTimes) {
    const TMatcherConfig matcherConfig(CFG_PATH.c_str());
    const TFilterConfig filterConfig;
    const auto signals = NTaxi::NGraph2::LoadSignalsFromFile(TestDataPath("sample1.json"));

    auto consumer = std::make_shared<TTestSelectorConsumer>();

    TPersistentIndex index(
        GraphPath("edges_persistent_index.fb").data());

    TMatcherManagersSelector selector{Graph,
                                      TMatcherManagerSettings{
                                          TMatcherManagerSettings::TThrowPolicy::ReportAndDiscard,
                                          TMatcherManagerSettings::TThrowPolicy::ReportAndDiscard},
                                      nullptr, matcherConfig, filterConfig, index, nullptr};

    auto token = selector.AddConsumer(consumer);

    const std::vector PrefferedTimes{{std::chrono::milliseconds{3'000},
                                      std::chrono::milliseconds{10'000},
                                      std::chrono::milliseconds{13'000},
                                      std::chrono::milliseconds{23'000}}};

    selector.SetSettings(
        NTaxi::NYagaSelector::TMapPredictSettings{
            .PredictionTargetMilliSeconds = 20'000,
            .PrefferedTimes = PrefferedTimes},
        token);

    for (const auto& signal : signals) {
        selector.AddSignal(signal);
    }

    selector.ForceFlushOnYield();

    EXPECT_EQ(consumer->Results.size(), signals.size());

    for (const auto& hypo : consumer->Results) {
        EXPECT_TRUE(std::is_sorted(hypo.Hypotheses.cbegin(), hypo.Hypotheses.cend(), [](const auto& first, const auto& second) {
            return first.PredictionShift <= second.PredictionShift;
        }));
        EXPECT_EQ(hypo.Hypotheses.size(), PrefferedTimes.size() - 1);
        for (const auto& [id, val] : Enumerate(hypo.Hypotheses)) {
            EXPECT_EQ(val.PredictionShift, PrefferedTimes[id]);
        }
    }
}