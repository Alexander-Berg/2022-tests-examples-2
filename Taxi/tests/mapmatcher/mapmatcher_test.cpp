#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <library/cpp/json/json_value.h>
#include <library/cpp/json/json_reader.h>

#include <util/stream/file.h>

#include <yandex/taxi/graph2/graph.h>
#include <yandex/taxi/graph2/container.h>
#include <yandex/taxi/graph2/mapmatcher/matcher.h>
#include <yandex/taxi/graph2/mapmatcher/matcher_config.h>
#include <yandex/taxi/graph2/shortest_path/shortest_path_data.h>
#include <yandex/taxi/graph2/mapmatcher/matched_path_consumer.h>
#include <taxi/graph/external/graph2/lib/gps_signal_impl.h>
#include <taxi/graph/external/graph2/lib/graph_impl.h>
#include <taxi/graph/external/graph2/lib/graph_builder.h>
#include <taxi/graph/external/graph2/lib/container.h>

#include <taxi/graph/libs/graph/graph.h>

#include <util/folder/path.h>

#include <algorithm>
#include <iostream>
#include <fstream>
#include <map>
#include <queue>
#include <set>
#include <filesystem>

using namespace std;
using namespace boost::posix_time;
namespace pt = boost::posix_time;

TString GraphPath(const TString& name) {
    return BinaryPath(JoinFsPaths("taxi/graph/data/graph3", name));
}

TString TestDataPath(const TString& name) {
    return JoinFsPaths(ArcadiaSourceRoot(), "taxi/graph/data/mapmatcher", name);
}

const TString PATH_TO_ROAD_GRAPH = GraphPath("road_graph.fb");
const TString PATH_TO_RTREE = GraphPath("rtree.fb");

const TString CFG_PATH = JoinFsPaths(ArcadiaSourceRoot(), "taxi/graph/external/graph2/tests/mapmatcher/data/offline_best.json");

using SegmentId = maps::jams::static_graph2::SegmentId;
using TMatchedPath = NTaxiExternal::NMapMatcher2::TMatchedPath;
using TPath = NTaxiExternal::NShortestPath2::TPath;
using TPathOnGraph = NTaxiExternal::NShortestPath2::TPathOnGraph;
using TGpsSignal = NTaxiExternal::NGraph2::TGpsSignal;
using TMatchedPaths = std::vector<TMatchedPath>;
using TMatcher = NTaxiExternal::NMapMatcher2::TMatcher;
using IMatchedPathConsumer = NTaxiExternal::NMapMatcher2::IMatchedPathConsumer;
using TMatcherConfig = NTaxiExternal::NMapMatcher2::TMatcherConfig;
using TFilterConfig = NTaxiExternal::NMapMatcher2::TFilterConfig;
using TId = NTaxiExternal::NGraph2::TId;
using TPositionOnEdge = NTaxiExternal::NGraph2::TPositionOnEdge;
using TPositionOnGraph = NTaxiExternal::NGraph2::TPositionOnGraph;
using TTimestamp = NTaxiExternal::NGraph2::TTimestamp;
using TPoint = NTaxiExternal::NGraph2::TPoint;

bool operator==(const TPositionOnEdge& first, const TPositionOnEdge& second) noexcept {
    return first.EdgeId == second.EdgeId && first.Position == second.Position;
}

bool operator==(const TPositionOnGraph& first, const TPositionOnGraph& second) noexcept {
    return second.Position == first.Position && second.EdgeId == first.EdgeId && second.SegmentIndex == first.SegmentIndex;
}

inline TTimestamp ConvertBoostTimeToUnix(const boost::posix_time::ptime& time) noexcept {
    return boost::posix_time::to_time_t(time);
}
inline boost::posix_time::ptime ConvertUnixTimeToBoost(TTimestamp unixTime) noexcept {
    return boost::posix_time::from_time_t(unixTime);
}

struct TMapMatcherTestFixture: public ::NUnitTest::TBaseTestCase {
    /* A mix of taxi/graph wrappers and classes from original
     * maps/analyzer/libs/deprecated/mapmatcher library is used.
     * As such, it is easier to put necessary typedefs
     * directly inside class body
     *
     */

    class DummyMatchedPathConsumer: public IMatchedPathConsumer {
    public:
        void Push(TMatchedPath&&) override {
        }
    };

    class StoringMatchedPathConsumer: public std::vector<TMatchedPath>,
                                       public IMatchedPathConsumer {
    public:
        void Push(TMatchedPath&& path) override {
            emplace_back(std::move(path));
        }
    };

    const size_t TESTS_NUMBER = 5;

    TMapMatcherTestFixture()
        : graph(NTaxiExternal::NGraph2::TRoadGraphFileLoader::Create(
              PATH_TO_ROAD_GRAPH.c_str(), PATH_TO_RTREE.c_str()))
    {
        graphImpl = &(graph.Impl().GetRoadGraph());
    }

    void checkDuplicatedNew();
    void checkMatchStrictPathNew();
    std::vector<NTaxiExternal::NGraph2::TGpsSignal> loadSignalsFromFile(
        const TString& filename);

    /*! This is owning pointer to graph
     */
    NTaxiExternal::NGraph2::TGraph graph;
    /*! And this is non-owning pointer to graph internals
     */
    const NTaxi::NGraph2::TRoadGraphData* graphImpl = nullptr;
};

Y_UNIT_TEST_SUITE_F(mapmatcher_test, TMapMatcherTestFixture){
    Y_UNIT_TEST(CheckDuplicateSignalsRaiseNew){
        checkMatchStrictPathNew();
}

Y_UNIT_TEST(MatchStrictPath_new) {
    checkDuplicatedNew();
}

Y_UNIT_TEST(CheckSample_1) {
    const TMatcherConfig matcherConfig(
        CFG_PATH.c_str());
    const TFilterConfig filterConfig;

    StoringMatchedPathConsumer matchedPaths;
    TMatcher matcher(graph,
                     nullptr,
                     matcherConfig,
                     filterConfig,
                     &matchedPaths);
    const auto signals = loadSignalsFromFile(TestDataPath("sample1.json"));

    for (const auto& signal : signals) {
        matcher.AppendSignal(signal);
    }

    matcher.Flush();
}

Y_UNIT_TEST(CheckSample_2) {
    const TMatcherConfig matcherConfig(
        CFG_PATH.c_str());
    const TFilterConfig filterConfig;

    StoringMatchedPathConsumer matchedPaths;
    TMatcher matcher(graph,
                     nullptr,
                     matcherConfig,
                     filterConfig,
                     &matchedPaths);
    const auto signals = loadSignalsFromFile(TestDataPath("sample2.json"));

    for (const auto& signal : signals) {
        matcher.AppendSignal(signal);
    }

    matcher.Flush();
}

Y_UNIT_TEST(CheckInterpolation) {
    const TMatcherConfig matcherConfig(
        CFG_PATH.c_str());
    const TFilterConfig filterConfig;

    StoringMatchedPathConsumer matchedPaths;
    TMatcher matcher(graph,
                     nullptr,
                     matcherConfig,
                     filterConfig,
                     &matchedPaths);
    const auto signals = loadSignalsFromFile(TestDataPath("sample2.json"));

    for (const auto& signal : signals) {
        matcher.AppendSignal(signal);
    }

    matcher.Flush();

    bool has_nonbroken_path = false;
    for (const TMatchedPath& matchedPath : matchedPaths) {
        if (matchedPath.Broken()) {
            continue;
        }
        has_nonbroken_path = true;

        const TPath& path = matchedPath.Path;
        TPathOnGraph pathOnGraph{path, graph};

        UNIT_ASSERT(pathOnGraph.GetSourcePoint() == pathOnGraph.GetPointAt(0.0));
        UNIT_ASSERT(pathOnGraph.GetTargetPoint() == pathOnGraph.GetPointAt(1.0));

        TPositionOnEdge lastPos;
        std::unordered_set<TId> usedEdges;
        for (double alpha = 0; alpha <= 1.0; alpha += 0.1) {
            TPositionOnGraph interpolatedPos = pathOnGraph.GetPointAt(alpha);
            TPositionOnEdge currentPos = graph.GetPositionOnEdge(
                interpolatedPos);

            if (currentPos.EdgeId == lastPos.EdgeId) {
                // If edge is the same, then we must be further along it
                UNIT_ASSERT(currentPos.Position >= lastPos.Position);
            } else {
                if (lastPos.EdgeId != NTaxiExternal::NGraph2::UNDEFINED) {
                    usedEdges.insert(lastPos.EdgeId);
                }
                // if edges are different, then check that we, at least, do
                // not go back to already used edges
                UNIT_ASSERT(usedEdges.find(currentPos.EdgeId) == usedEdges.end());
            }

            lastPos = currentPos;
        }
    }

    UNIT_ASSERT(has_nonbroken_path);
}

Y_UNIT_TEST(CheckBestPositionAndNPredecessors) {
    const TMatcherConfig matcherConfig(
        CFG_PATH.c_str());

    StoringMatchedPathConsumer matchedPaths;
    const TFilterConfig signalsConfig;
    TMatcher matcher(graph,
                     nullptr,
                     matcherConfig,
                     signalsConfig,
                     &matchedPaths);
    const auto signals = loadSignalsFromFile(TestDataPath("sample2.json"));

    for (const auto& signal : signals) {
        matcher.AppendSignal(signal);
    }

    auto bestHeadAndPredecessor = matcher.GetBestPositionAndNPredecessors(5);
    Y_ASSERT(bestHeadAndPredecessor.Size() > 1);

    TTimestamp currentTime = bestHeadAndPredecessor[0].Timestamp;
    for (size_t i = 1; i < bestHeadAndPredecessor.Size(); ++i) {
        auto elemTimestamp = bestHeadAndPredecessor[i].Timestamp;
        Y_ASSERT(elemTimestamp < currentTime);
        currentTime = elemTimestamp;
    }
}

Y_UNIT_TEST(CheckInterpolationNew) {
    const TMatcherConfig matcherConfig(
        CFG_PATH.c_str());
    const TFilterConfig signalsConfig;

    StoringMatchedPathConsumer matchedPaths;
    TMatcher matcher(graph,
                     nullptr,
                     matcherConfig,
                     signalsConfig,
                     &matchedPaths);
    const auto signals = loadSignalsFromFile(TestDataPath("sample5.json"));

    for (const auto& signal : signals) {
        matcher.AppendSignal(signal);
    }

    matcher.Flush();

    bool has_nonbroken_path = false;
    for (const TMatchedPath& matchedPath : matchedPaths) {
        if (matchedPath.Broken()) {
            continue;
        }
        has_nonbroken_path = true;

        const TPath& path = matchedPath.Path;
        TPathOnGraph pathOnGraph{path, graph};

        UNIT_ASSERT(pathOnGraph.GetSourcePoint() == pathOnGraph.GetPointAt(0.0));
        UNIT_ASSERT(pathOnGraph.GetTargetPoint() == pathOnGraph.GetPointAt(1.0));

        TPositionOnEdge lastPos;
        std::unordered_set<TId> usedEdges;
        for (double alpha = 0; alpha <= 1.0; alpha += 0.1) {
            TPositionOnGraph interpolatedPos = pathOnGraph.GetPointAt(alpha);
            TPositionOnEdge currentPos = graph.GetPositionOnEdge(
                interpolatedPos);

            if (currentPos.EdgeId == lastPos.EdgeId) {
                // If edge is the same, then we must be further along it
                UNIT_ASSERT(currentPos.Position >= lastPos.Position);
            } else {
                if (lastPos.EdgeId != NTaxiExternal::NGraph2::UNDEFINED) {
                    usedEdges.insert(lastPos.EdgeId);
                }
                // if edges are different, then check that we, at least, do
                // not go back to already used edges
                UNIT_ASSERT(usedEdges.find(currentPos.EdgeId) == usedEdges.end());
            }

            lastPos = currentPos;
        }
    }

    UNIT_ASSERT(has_nonbroken_path);
}
}
;

void TMapMatcherTestFixture::checkDuplicatedNew() {
    const TMatcherConfig matcherConfig(
        CFG_PATH.c_str());
    const TFilterConfig signalsConfig;
    DummyMatchedPathConsumer dummy;
    TMatcher matcher(graph,
                     nullptr,
                     matcherConfig,
                     signalsConfig,
                     &dummy);
    TGpsSignal signal1, signal2;
    signal1.SetLon(37.551257);
    signal1.SetLat(55.666974);
    ptime now = maps::nowUtc();
    signal1.SetTime(ConvertBoostTimeToUnix(now));
    signal2.SetTime(ConvertBoostTimeToUnix(now - pt::seconds(2)));
    signal2.SetLon(37.551257);
    signal2.SetLat(55.666974);
    UNIT_ASSERT(matcher.AppendSignal(signal1));
    // UNIT_ASSERT_EXCEPTION(matcher.AppendSignal(signal1), maps::Exception);
    // UNIT_ASSERT_EXCEPTION(matcher.AppendSignal(signal2), maps::Exception);
}

void TMapMatcherTestFixture::checkMatchStrictPathNew() {
    const TMatcherConfig matcherConfig(
        CFG_PATH.c_str());
    const TFilterConfig signalsConfig;
    const auto signals = loadSignalsFromFile(TestDataPath("sample4.json"));

    const TPoint refPoint{37.61548399, 55.6231965};

    StoringMatchedPathConsumer matchedPaths;
    TMatcher matcher(graph,
                     nullptr,
                     matcherConfig,
                     signalsConfig,
                     &matchedPaths);

    UNIT_ASSERT(signals.size() > 0);

    for (const auto& signal : signals) {
        matcher.AppendSignal(signal);
    }
    matcher.Flush();

    const TMatchedPath& matchedPath = matchedPaths.back();
    UNIT_ASSERT(!matchedPath.Broken());

    const TPath& path = matchedPath.Path;
    TPathOnGraph pathOnGraph{path, graph};
    const auto& targetPoint = pathOnGraph.GetTargetPoint();
    const auto coords = graph.GetCoords(targetPoint);

    UNIT_ASSERT(abs(coords.Lon - refPoint.Lon) < 0.0003);
    UNIT_ASSERT(abs(coords.Lat - refPoint.Lat) < 0.0003);
}

std::vector<NTaxiExternal::NGraph2::TGpsSignal> TMapMatcherTestFixture::loadSignalsFromFile(
    const TString& filename) {
    TFileInput file(filename);
    NJson::TJsonValue root;
    NJson::ReadJsonTree(&file, true, &root);

    std::vector<NTaxiExternal::NGraph2::TGpsSignal> result;

    TString uid = "test-uid";
    TString clid = "test-clid";

    NJson::TJsonValue track = root["track"];
    for (const NJson::TJsonValue& signalJson : track.GetArraySafe()) {
        NTaxiExternal::NGraph2::TGpsSignal gpsSignal;
        gpsSignal.SetLon(signalJson["lon"].GetDoubleSafe());
        gpsSignal.SetLat(signalJson["lat"].GetDoubleSafe());
        gpsSignal.SetTime(signalJson["timestamp"].GetUIntegerSafe());
        gpsSignal.SetAverageSpeed(signalJson["speed"].GetDoubleSafe());

        result.emplace_back(std::move(gpsSignal));
    }

    return result;
}

//__________________________________________________________________________//
