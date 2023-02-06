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
#include <taxi/graph/libs/matcher_framework/adjusted_track_provider.h>
#include <taxi/graph/libs/matcher_framework/vector_reader.h>

#include <taxi/graph/libs/graph-test/graph_test_data.h>
#include <taxi/graph/libs/graph-test/load_signals_from_file.h>

#include <util/folder/path.h>
#include <util/stream/file.h>

#include <iostream>
#include <fstream>
#include <filesystem>

#include "paths.h"

struct TMatcherFrameworkAdjustTrackRoadTestFixture: public ::NUnitTest::TBaseTestCase,
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

    using TAdjustedTrackProvider = NTaxi::NMapMatcher2::TAdjustedTrackProvider;
    using TAdjustedPositionOnGraph = NTaxi::NMapMatcher2::TAdjustedTrackProvider::TAdjustedPositionOnGraph;

    using TGraph = NTaxi::NGraph2::TGraph;
    using TTimestamp = NTaxi::NGraph2::TTimestamp;
    using TGpsSignal = NTaxi::NGraph2::TGpsSignal;
    using TPoint = NTaxi::NGraph2::TPoint;
    using TCandidateGraphDebug = NTaxi::NMapMatcher2::TCandidateGraphDebug;
    using TPositionOnEdge = NTaxi::NGraph2::TPositionOnEdge;
    using TPositionOnGraph = NTaxi::NGraph2::TPositionOnGraph;
    using IAdjustedTrackConsumer = TAdjustedTrackProvider::IAdjustedTrackConsumer;

    class TTestConsumer: public IAdjustedTrackConsumer {
    public:
        TTestConsumer(const TGraph& graph)
            : Graph(graph)
        {
        }

        void OnAdjustedPosition(const std::optional<TAdjustedPositionOnGraph>& point) final {
            Positions.push_back(point);
        }

        const TGraph& Graph;
        std::vector<std::optional<TAdjustedPositionOnGraph>> Positions;
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

    TMatcherFrameworkAdjustTrackRoadTestFixture()
        : graph(GetTestRoadGraph())
        , matcherConfig(CFG_PATH.c_str())
        , matcherSettings{
              TMatcherManagerSettings::TThrowPolicy::ReportAndDiscard,
              TMatcherManagerSettings::TThrowPolicy::ReportAndDiscard} {
    }

    std::shared_ptr<TTestReader> LoadSignalsFromFile(const TString& filename, bool noSpeed = false, bool reverse = false) {
        auto signals = NTaxi::NGraph2::LoadSignalsFromFile(filename, noSpeed);
        if (reverse) {
            std::reverse(signals.begin(), signals.end());
        }

        std::shared_ptr<TTestReader> result = std::make_shared<TTestReader>();

        for (const auto& signal : signals) {
            result->AddSignal(std::move(signal));
        }
        result->MarkFinished();

        return result;
    }

    const TGraph& graph;
    const TMatcherConfig matcherConfig;
    const TMatcherManagerSettings matcherSettings;
    const TFilterConfig filterConfig;
};

Y_UNIT_TEST_SUITE_F(matcher_framework_adjust_track_road_test, TMatcherFrameworkAdjustTrackRoadTestFixture) {
    Y_UNIT_TEST(CheckUnadjustableTrackRoad) {
        auto testFunc = [this](bool snap) {
            auto matcher = std::make_unique<TMatcher>(graph,
                                                      matcherConfig,
                                                      filterConfig,
                                                      nullptr);

            std::shared_ptr<TTestConsumer> consumer = std::make_shared<TTestConsumer>(graph);
            std::shared_ptr<TAdjustedTrackProvider> adjustedTrackConsumer = std::make_shared<TAdjustedTrackProvider>(graph, consumer, false, false, snap);
            const auto& reader = LoadSignalsFromFile(TestDataPath("adjust_track_test/unadjustable_track1.json"));

            TMatcherManager matcherManager(std::move(matcher), matcherSettings, adjustedTrackConsumer, reader);
            matcherManager.MatchAll();

            for (const auto& pos : consumer->Positions) {
                UNIT_ASSERT_EQUAL(pos, std::nullopt);
            }
        };

        for (const auto& snap : {true, false}) {
            testFunc(snap);
        }
    }

    Y_UNIT_TEST(CheckAdjustEmptyTrackRoad) {
        auto testFunc = [this](bool extrapolation, bool snap) {
            auto matcher = std::make_unique<TMatcher>(graph,
                                                      matcherConfig,
                                                      filterConfig,
                                                      nullptr);

            std::shared_ptr<TTestConsumer> consumer = std::make_shared<TTestConsumer>(graph);
            std::shared_ptr<TAdjustedTrackProvider> adjustedTrackConsumer = std::make_shared<TAdjustedTrackProvider>(graph, consumer, false, extrapolation, snap);
            const auto& reader = std::make_shared<TVectorReader>();
            reader->MarkFinished();

            TMatcherManager matcherManager(std::move(matcher), matcherSettings, adjustedTrackConsumer, reader);
            matcherManager.MatchAll();

            UNIT_ASSERT_EQUAL(consumer->Positions.size(), 0);
        };

        for (const auto& extrapolation : {true, false}) {
            for (const auto& snap : {true, false}) {
                testFunc(extrapolation, snap);
            }
        }
    }

    Y_UNIT_TEST(CheckTimeFrozenRoad) {
        auto testFunc = [this](bool noSpeed, bool extrapolation) {
            auto matcher = std::make_unique<TMatcher>(graph,
                                                      matcherConfig,
                                                      filterConfig,
                                                      nullptr);

            std::shared_ptr<TTestConsumer> consumer = std::make_shared<TTestConsumer>(graph);
            std::shared_ptr<TAdjustedTrackProvider> adjustedTrackConsumer = std::make_shared<TAdjustedTrackProvider>(graph, consumer, false, extrapolation, false);
            const auto& reader = LoadSignalsFromFile(TestDataPath("adjust_track_test/time_frozen_track.json"), noSpeed);

            TMatcherManager matcherManager(std::move(matcher), matcherSettings, adjustedTrackConsumer, reader);
            matcherManager.MatchAll();

            UNIT_ASSERT_EQUAL(consumer->Positions.size(), 3);
        };

        for (const auto& noSpeed : {true, false}) {
            for (const auto& extrapolation : {true, false}) {
                testFunc(noSpeed, extrapolation);
            }
        }
    }

    Y_UNIT_TEST(CheckSpaceFrozenRoad) {
        auto testFunc = [this](bool noSpeed, bool extrapolation) {
            auto matcher = std::make_unique<TMatcher>(graph,
                                                      matcherConfig,
                                                      filterConfig,
                                                      nullptr);

            std::shared_ptr<TTestConsumer> consumer = std::make_shared<TTestConsumer>(graph);
            std::shared_ptr<TAdjustedTrackProvider> adjustedTrackConsumer = std::make_shared<TAdjustedTrackProvider>(graph, consumer, false, extrapolation, false);
            const auto& reader = LoadSignalsFromFile(TestDataPath("adjust_track_test/space_frozen_track.json"), noSpeed);

            TMatcherManager matcherManager(std::move(matcher), matcherSettings, adjustedTrackConsumer, reader);
            matcherManager.MatchAll();

            UNIT_ASSERT_EQUAL(consumer->Positions.size(), 3);
        };

        for (const auto& noSpeed : {true, false}) {
            for (const auto& extrapolation : {true, false}) {
                testFunc(noSpeed, extrapolation);
            }
        }
    }

    Y_UNIT_TEST(CheckExtrapolationRoad) {
        auto testFunc = [this](bool noSpeed, bool extrapolation) {
            auto matcher = std::make_unique<TMatcher>(graph,
                                                      matcherConfig,
                                                      filterConfig,
                                                      nullptr);

            std::shared_ptr<TTestConsumer> consumer = std::make_shared<TTestConsumer>(graph);
            std::shared_ptr<TAdjustedTrackProvider> adjustedTrackConsumer = std::make_shared<TAdjustedTrackProvider>(graph, consumer, false, extrapolation, false);
            const auto& reader = LoadSignalsFromFile(TestDataPath("adjust_track_test/track_extrapolation_test.json"), noSpeed);

            TMatcherManager matcherManager(std::move(matcher), matcherSettings, adjustedTrackConsumer, reader);
            matcherManager.MatchAll();

            return consumer->Positions;
        };

        for (const auto& noSpeed : {true, false}) {
            auto nonExtrapolated = testFunc(noSpeed, false);
            UNIT_ASSERT_EQUAL(nonExtrapolated.size(), 12);

            const auto& lastNonExtrapolated = nonExtrapolated.back();
            UNIT_ASSERT_EQUAL(lastNonExtrapolated, std::nullopt);

            auto adjustedElem = [](const auto& elem) -> bool {
                return static_cast<bool>(elem);
            };
            const auto refElem =
                std::find_if(nonExtrapolated.crbegin(), nonExtrapolated.crend(), adjustedElem);
            UNIT_ASSERT_UNEQUAL(refElem, nonExtrapolated.crend());

            auto extrapolated = testFunc(noSpeed, true);
            const auto& lastExtrapolated = extrapolated.back();
            UNIT_ASSERT_UNEQUAL(lastExtrapolated, std::nullopt);
            UNIT_ASSERT(lastExtrapolated->IsExtrapolated);

            UNIT_ASSERT(TPoint::IsSamePoint((*refElem)->Position.Point(), lastExtrapolated->Position.Point()));
        }
    }

    Y_UNIT_TEST(CheckAdjustPathRoad) {
        auto testFunc = [this](bool noSpeed, bool extrapolation, bool snap) {
            auto matcher = std::make_unique<TMatcher>(graph,
                                                      matcherConfig,
                                                      filterConfig,
                                                      nullptr);

            std::shared_ptr<TTestConsumer> consumer = std::make_shared<TTestConsumer>(graph);
            std::shared_ptr<TAdjustedTrackProvider> adjustedTrackConsumer = std::make_shared<TAdjustedTrackProvider>(graph, consumer, false, extrapolation, snap);
            const auto& reader = LoadSignalsFromFile(TestDataPath("adjust_track_test/adjustable_track1.json"), noSpeed);

            TMatcherManager matcherManager(std::move(matcher), matcherSettings, adjustedTrackConsumer, reader);
            matcherManager.MatchAll();

            return std::make_pair(reader->GetSignals(), consumer->Positions);
        };

        for (const auto& noSpeed : {true, false}) {
            for (const auto& extrapolation : {true, false}) {
                for (const auto& snap : {true, false}) {
                    const auto result = testFunc(noSpeed, extrapolation, snap);
                    const auto& track = result.first;
                    const auto& adjusted = result.second;
                    UNIT_ASSERT_EQUAL(adjusted.size(), 10);

                    int adjustedCount = 0;
                    bool current_position = false;
                    for (auto it = std::make_pair(track.begin(), adjusted.begin());
                         it.first != track.end() && it.second != adjusted.end();
                         ++it.first, ++it.second) {
                        const auto& srcPos = *it.first;
                        const auto& adjPos = *it.second;

                        if (!adjPos) {
                            continue;
                        }

                        const auto& adjPoint = adjPos->Position.Point();
                        UNIT_ASSERT(-90 <= adjPoint.Lat);
                        UNIT_ASSERT(adjPoint.Lat <= 90);
                        UNIT_ASSERT(-180 <= adjPoint.Lon);
                        UNIT_ASSERT(adjPoint.Lon <= 180);
                        UNIT_ASSERT_GE(adjPos->Position.Time(), 0);

                        adjustedCount++;
                        UNIT_ASSERT_EQUAL(srcPos.Time(), adjPos->Position.Time());

                        if (!current_position) {
                            current_position = (adjPos->Edge != NTaxi::NGraph2::UNDEFINED);
                        }

                        UNIT_ASSERT(!adjPos->IsToll);
                    }

                    UNIT_ASSERT_GE(adjustedCount, 3);
                    UNIT_ASSERT(current_position);

                    const auto& lastScrPoint = track.back().Point();
                    const auto& lastAdjPoint = adjusted.back()->Position.Point();
                    UNIT_ASSERT_LT(lastAdjPoint.Lat - lastScrPoint.Lat, 0.001);
                    UNIT_ASSERT_LT(lastAdjPoint.Lon - lastScrPoint.Lon, 0.001);
                }
            }
        }
    }

    Y_UNIT_TEST(CheckInterpolatedRoad) {
        auto testFunc = [this](bool interpolation) {
            auto matcher = std::make_unique<TMatcher>(graph,
                                                      matcherConfig,
                                                      filterConfig,
                                                      nullptr);

            std::shared_ptr<TTestConsumer> consumer = std::make_shared<TTestConsumer>(graph);
            std::shared_ptr<TAdjustedTrackProvider> adjustedTrackConsumer = std::make_shared<TAdjustedTrackProvider>(graph, consumer, interpolation, false, false);
            const auto& reader = LoadSignalsFromFile(TestDataPath("adjust_track_test/track_interpolation_test.json"));

            TMatcherManager matcherManager(std::move(matcher), matcherSettings, adjustedTrackConsumer, reader);
            matcherManager.MatchAll();

            return consumer->Positions;
        };

        auto nonInterpolated = testFunc(false);
        UNIT_ASSERT_EQUAL(nonInterpolated.size(), 7);

        auto interpolated = testFunc(true);
        UNIT_ASSERT_EQUAL(interpolated.size(), 7);

        auto adjustedElem = [](const auto& elem) -> bool {
            return static_cast<bool>(elem);
        };

        const auto nullElemNonInterpolated =
            std::find_if_not(nonInterpolated.cbegin(), nonInterpolated.cend(), adjustedElem);
        UNIT_ASSERT_UNEQUAL(nullElemNonInterpolated, nonInterpolated.cend());

        const auto nullElemInterpolated =
            std::find_if_not(interpolated.cbegin(), interpolated.cend(), adjustedElem);
        UNIT_ASSERT_EQUAL(nullElemInterpolated, interpolated.cend());

        for (auto it = std::make_pair(nonInterpolated.begin(), interpolated.begin());
             it.first != nonInterpolated.end() && it.second != interpolated.end();
             ++it.first, ++it.second) {
            const auto& nonItem = *it.first;
            const auto& item = *it.second;

            if (nonItem) {
                UNIT_ASSERT(!item->IsInterpolated);
                UNIT_ASSERT_EQUAL(nonItem->Position.Time(), item->Position.Time());
            } else {
                UNIT_ASSERT(item->IsInterpolated);
            }
        }

        auto timestamp = interpolated.front()->Position.Time();
        for (const auto& item : interpolated) {
            UNIT_ASSERT_LE(timestamp, item->Position.Time());
            timestamp = item->Position.Time();
        }
    }
}
