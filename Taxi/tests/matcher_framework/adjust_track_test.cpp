#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <library/cpp/json/json_value.h>
#include <library/cpp/json/json_reader.h>

#include <taxi/graph/external/graph2/lib/conversion.h>
#include <yandex/taxi/graph2/container.h>
#include <yandex/taxi/graph2/graph.h>
#include <yandex/taxi/graph2/api_version.h>

#include <yandex/taxi/graph2/mapmatcher/matcher.h>

#include <yandex/taxi/graph2/matcher_framework/vector_reader.h>
#include <yandex/taxi/graph2/matcher_framework/yaga_consumer.h>
#include <yandex/taxi/graph2/matcher_framework/matcher_manager.h>
#include <yandex/taxi/graph2/mapmatcher/matcher.h>

#include <taxi/graph/libs/graph-test/load_signals_from_file.h>

#include <util/folder/path.h>
#include <util/stream/file.h>

#include <iostream>
#include <fstream>
#include <filesystem>

#include "paths.h"

using namespace std;

using NTaxiExternal::NGraph2::TGpsSignal;
using NTaxiExternal::NGraph2::TGraph;
using NTaxiExternal::NGraph2::TId;
using NTaxiExternal::NGraph2::TOptional;
using NTaxiExternal::NGraph2::TRoadGraphFileLoader;
using NTaxiExternal::NGraph2::TTimestamp;
using NTaxiExternal::NMapMatcher2::TAdjustedTrackConsumer2;
using NTaxiExternal::NMapMatcher2::TFilterConfig;
using NTaxiExternal::NMapMatcher2::TMatcher2;
using NTaxiExternal::NMapMatcher2::TMatcherConfig;
using NTaxiExternal::NMapMatcher2::TMatcherManager;
using NTaxiExternal::NMapMatcher2::TMatcherManagerSettings;
using NTaxiExternal::NMapMatcher2::TVectorReader;

struct TMatcherFrameworkAdjustTrackTestFixture: public ::NUnitTest::TBaseTestCase {
    /* A mix of taxi/graph wrappers and classes from original
     * maps/analyzer/libs/deprecated/mapmatcher library is used.
     * As such, it is easier to put necessary typedefs
     * directly inside class body
     */

    class TTestConsumer: public TAdjustedTrackConsumer2 {
    public:
        TTestConsumer(const TGraph& graph)
            : Graph(graph)
        {
        }

        void OnAdjustedPoint(TOptional<TAdjustedPositionOnGraph>&& point) final {
            Positions.emplace_back(std::move(point));
        }

        const TGraph& Graph;
        std::vector<TOptional<TAdjustedPositionOnGraph>> Positions;
    };

    TMatcherFrameworkAdjustTrackTestFixture()
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

    const TGraph& Graph;
    const TMatcherConfig MatcherConfig;
    const TMatcherManagerSettings MatcherSettings;
    const TFilterConfig FilterConfig;
};

Y_UNIT_TEST_SUITE_F(matcher_framework_adjust_track_test, TMatcherFrameworkAdjustTrackTestFixture) {
    Y_UNIT_TEST(CheckSample_1) {
        const auto signals = NTaxi::NGraph2::LoadSignalsFromFile(TestDataPath("sample1.json"));

        TVectorReader reader;
        ;
        for (const auto& signal : signals) {
            reader.AddSignal(NTaxiExternal::NGraph2::ToExternal(signal));
        }
        reader.MarkFinished();
        TMatcher2 matcher(Graph,
                          (NTaxiExternal::NShortestPath2::TShortestPathData*)nullptr,
                          MatcherConfig,
                          FilterConfig);

        TTestConsumer consumer(Graph);

        TMatcherManager matcherManager(std::move(matcher), MatcherSettings,
                                       consumer, reader, true, true, true);
        while (matcherManager.MatchChunk() != TMatcherManager::TInputStatus::Finished) {
        }

        Cout << "Positions size: " << consumer.Positions.size() << Endl;

        Y_ASSERT(consumer.Positions.size() >= signals.size() / 2);
    };
}
