#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <library/cpp/json/json_value.h>
#include <library/cpp/json/json_reader.h>

#include <util/stream/file.h>

#include <taxi/graph/libs/shortest_path/path.h>
#include <taxi/graph/libs/graph/gps_signal.h>
#include <taxi/graph/libs/mapmatcher/candidate_graph_debug.h>
#include <taxi/graph/libs/mapmatcher/matcher.h>
#include <taxi/graph/libs/mapmatcher/matcher_config.h>
#include <taxi/graph/libs/mapmatcher/matched_path_consumer.h>
#include <taxi/graph/libs/shortest_path/shortest_path_data.h>
#include <taxi/graph/libs/shortest_path/path_on_graph.h>
#include <taxi/graph/libs/graph-test/load_signals_from_file.h>

#include <maps/analyzer/libs/data/include/gpssignal.h>
#include <maps/analyzer/libs/track_generator/include/gpssignal_creator.h>
#include <maps/analyzer/libs/track_generator/include/generators_factory.h>

#include <maps/libs/geolib/include/test_tools/test_tools.h>
#include <maps/libs/geolib/include/conversion.h>
#include <maps/libs/geolib/include/bounding_box.h>
#include <maps/libs/geolib/include/point.h>
#include <maps/libs/geolib/include/vector.h>
#include <maps/libs/geolib/include/direction.h>
#include <maps/libs/geolib/include/segment.h>
#include <yandex/maps/mms/holder2.h>

#include <boost/random/variate_generator.hpp>
#include <boost/random/uniform_int.hpp>
#include <boost/random.hpp>

#include <util/folder/path.h>

#include <algorithm>
#include <iostream>
#include <fstream>
#include <map>
#include <queue>
#include <set>
#include <filesystem>

using namespace std;
using namespace maps::analyzer::track_generator;
using namespace maps::geolib3;
using maps::road_graph::SegmentId;
using NTaxi::NGraph2::TPositionOnEdge;
using NTaxi::NGraph2::TPositionOnGraph;

bool operator==(const TPositionOnEdge& first, const TPositionOnEdge& second) noexcept {
    return first.GetEdgeId() == second.GetEdgeId() && first.GetPosition() == second.GetPosition();
}

bool operator==(const TPositionOnGraph& first, const TPositionOnGraph& second) noexcept {
    return second.GetSegmentPosition() == first.GetSegmentPosition() && second.GetEdgeId() == first.GetEdgeId() && second.GetSegmentIdx() == first.GetSegmentIdx();
}

TString GraphPath(const TString& name) {
    return BinaryPath(JoinFsPaths("taxi/graph/data/graph3", name));
}

TString TestDataPath(const TString& name) {
    return JoinFsPaths(ArcadiaSourceRoot(), "taxi/graph/data/mapmatcher", name);
}

const TString PATH_TO_ROAD_GRAPH = GraphPath("road_graph.fb");
const TString PATH_TO_RTREE = GraphPath("rtree.fb");
const TString PATH_TO_PERSISTENT_INDEX = GraphPath("edges_persistent_index.fb");

const TString CFG_PATH = JoinFsPaths(ArcadiaSourceRoot(), "taxi/graph/data/conf/mapmatcher/offline.json");

struct TMapMatcherTestFixture: public ::NUnitTest::TBaseTestCase {
    /* A mix of taxi/graph wrappers and classes from original
     * maps/analyzer/libs/mapmatcher library is used.
     * As such, it is easier to put necessary typedefs
     * directly inside class body
     *
     */
    using SegmentId = maps::road_graph::SegmentId;
    using TPath = NTaxi::NShortestPath2::TPath;
    using TPoint = NTaxi::NGraph2::TPoint;
    using TPathOnGraph = NTaxi::NShortestPath2::TPathOnGraph;
    using TGpsSignal = NTaxi::NGraph2::TGpsSignal;
    using SegmentPartIterator = maps::analyzer::shortest_path::SegmentPartIterator;
    using TMatcher = NTaxi::NMapMatcher2::TMatcher;
    using IMatchedPathConsumer = NTaxi::NMapMatcher2::IMatchedPathConsumer;
    using TMatcherConfig = NTaxi::NMapMatcher2::TMatcherConfig;
    using TFilterConfig = NTaxi::NMapMatcher2::TFilterConfig;
    using TCandidateGraphDebug = NTaxi::NMapMatcher2::TCandidateGraphDebug;
    using TId = NTaxi::NGraph2::TId;
    using TPositionOnEdge = NTaxi::NGraph2::TPositionOnEdge;
    using TPositionOnGraph = NTaxi::NGraph2::TPositionOnGraph;
    using TTimestamp = NTaxi::NGraph2::TTimestamp;
    struct TMatchedPath {
        TGpsSignal StartSignal;
        TGpsSignal EndSignal;
        TPath Path;
    };
    using TMatchedPaths = std::vector<TMatchedPath>;
    typedef boost::variate_generator<boost::mt19937,
                                     boost::uniform_int<>>
        UniformInt;

    class DummyMatchedPathConsumer: public IMatchedPathConsumer {
    public:
        void Push(const TGpsSignal& startSignal, const TGpsSignal& endSignal,
                          const TPath& path) override {
        }

        /// Two matched points that has no path between them (a.k.a. 'path
        /// is broken')
        void Push(const TGpsSignal& startSignal,
                          const TGpsSignal& endSignal) override {
        }
    };

    class StoringMatchedPathConsumer: public std::vector<TMatchedPath>,
                                       public IMatchedPathConsumer {
    public:
        void Push(const TGpsSignal& startSignal, const TGpsSignal& endSignal,
                          const TPath& path) override {
            push_back(TMatchedPath{startSignal, endSignal, path});
        }

        void Push(const TGpsSignal& startSignal,
                          const TGpsSignal& endSignal) override {
            push_back(TMatchedPath{startSignal, endSignal, TPath()});
        }
    };

    const size_t TESTS_NUMBER = 5;

    TMapMatcherTestFixture()
        : graph(std::make_unique<NTaxi::NGraph2::TRoadGraphDataStorage>(
              PATH_TO_ROAD_GRAPH.c_str(), PATH_TO_RTREE.c_str(),
              EMappingMode::Precharged))
        , persistentIndex(PATH_TO_PERSISTENT_INDEX)

    {
        graphImpl = &(graph.GetRoadGraph());
    }

    void checkDuplicated();
    void checkDuplicatedNew();
    void generateTestDataSet(int seed, TestDataSet& testSet);
    void checkMatchStrictPathNew();
    vector<SegmentId> postprocessMatchedPaths(const TMatchedPaths& matchedPaths);
    vector<SegmentId> calculateSegments(const TestData& test, TMatcher& matcher, TMatchedPaths& consumer);
    static inline double calculateQuality(const vector<SegmentId>& first, const vector<SegmentId>& second);
    void sortAndEraseDuplicate(vector<SegmentId>& vec);
    void convertMatchedPathsToSegmentIds(
        const TMatchedPaths& matchedPaths, vector<SegmentId>* ids);
    static size_t difference(const vector<SegmentId>& a, const vector<SegmentId>& b);
    std::vector<NTaxi::NGraph2::TGpsSignal> loadSignalsFromFile(
        const TString& filename);

    /*! This is owning pointer to graph
     */
    NTaxi::NGraph2::TGraph graph;
    /*! And this is non-owning pointer to graph internals
     */
    const NTaxi::NGraph2::TRoadGraphData* graphImpl = nullptr;
    NTaxi::NGraph2::TPersistentIndex persistentIndex;
};

Y_UNIT_TEST_SUITE_F(mapmatcher_test, TMapMatcherTestFixture) {
    Y_UNIT_TEST(CheckDuplicateSignalsRaiseNew) {
        checkMatchStrictPathNew();
    }

    Y_UNIT_TEST(MatchStrictPath_new) {
        checkDuplicatedNew();
    }

    Y_UNIT_TEST(CheckCandidateGraphDebugInfo) {
        const TMatcherConfig matcherConfig(
            CFG_PATH.c_str());

        TFilterConfig filterConfig;

        const auto signals = loadSignalsFromFile(TestDataPath("sample3.json"));

        TString outputCdgString;
        auto matchingDebug(
            TCandidateGraphDebug::CreateInMemoryYsonDebug(
                graph,
                persistentIndex,
                true,
                outputCdgString));

        StoringMatchedPathConsumer matchedPaths;
        TMatcher matcher(graph,
                         matcherConfig,
                         filterConfig,
                         &matchedPaths,
                         nullptr,
                         std::move(matchingDebug));

        UNIT_ASSERT(signals.size() > 0);

        for (const auto& signal : signals) {
            matcher.AppendSignal(signal);
        }

        matcher.Flush();

        UNIT_ASSERT(outputCdgString.Size() > 0);
    };

    Y_UNIT_TEST(CheckSample_1_new) {
        const TMatcherConfig matcherConfig(
            CFG_PATH.c_str());
        const TFilterConfig signalsConfig;

        StoringMatchedPathConsumer matchedPaths;
        TMatcher matcher(graph,
                         nullptr,
                         matcherConfig,
                         signalsConfig,
                         &matchedPaths);
        const auto signals = loadSignalsFromFile(TestDataPath("sample1.json"));

        for (const auto& signal : signals) {
            matcher.AppendSignal(signal);
        }

        matcher.Flush();
    }

    Y_UNIT_TEST(CheckSample_2_new) {
        const TMatcherConfig matcherConfig(
            CFG_PATH.c_str());
        const TFilterConfig signalsConfig;

        StoringMatchedPathConsumer matchedPaths;
        TMatcher matcher(graph,
                         nullptr,
                         matcherConfig,
                         signalsConfig,
                         &matchedPaths);
        const auto signals = loadSignalsFromFile(TestDataPath("sample2.json"));

        for (const auto& signal : signals) {
            matcher.AppendSignal(signal);
        }

        matcher.Flush();
    }

    Y_UNIT_TEST(CheckBestHeads) {
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

        auto bestPositions = matcher.GetBestPossiblePositions(5, 5);

        Y_ASSERT(bestPositions.size() > 0);
        for (const auto& pos : bestPositions) {
            Y_ASSERT(pos.GetProbability() > 0.0);
            Y_ASSERT(pos.GetProbability() <= 1.0);
        }

        auto noPositions = matcher.GetBestPossiblePositions(0, 5);
        Y_ASSERT(noPositions.size() == 0);

        auto noLayers = matcher.GetBestPossiblePositions(5, 0);
        Y_ASSERT(noLayers.size() == 0);

        auto noNothing = matcher.GetBestPossiblePositions(0, 0);
        Y_ASSERT(noNothing.size() == 0);
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

        auto bestHeadAndPredecessor = matcher.GetBestPositionAndNPredecessors(5).BestPositionAndPredecessors;
        Y_ASSERT(bestHeadAndPredecessor.size() > 1);

        TTimestamp currentTime = bestHeadAndPredecessor[0].Timestamp;
        for (size_t i = 1; i < bestHeadAndPredecessor.size(); ++i) {
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
            if (!matchedPath.Path.Exists()) {
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

                if (currentPos.GetEdgeId() == lastPos.GetEdgeId()) {
                    // If edge is the same, then we must be further along it
                    UNIT_ASSERT(currentPos.GetPosition() >= lastPos.GetPosition());
                } else {
                    if (lastPos.GetEdgeId() != NTaxi::NGraph2::UNDEFINED) {
                        usedEdges.insert(lastPos.GetEdgeId());
                    }
                    // if edges are different, then check that we, at least, do
                    // not go back to already used edges
                    UNIT_ASSERT(usedEdges.find(currentPos.GetEdgeId()) == usedEdges.end());
                }

                lastPos = currentPos;
            }
        }

        UNIT_ASSERT(has_nonbroken_path);
    }
};

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
    time_t now = time(nullptr);
    signal1.SetTime(now);
    signal2.SetTime(now - 2);
    signal2.SetLon(37.551257);
    signal2.SetLat(55.666974);
    UNIT_ASSERT(matcher.AppendSignal(signal1).IsAdded);
    // UNIT_ASSERT_EXCEPTION(matcher.AppendSignal(signal1), maps::Exception);
    // UNIT_ASSERT_EXCEPTION(matcher.AppendSignal(signal2), maps::Exception);
}

void TMapMatcherTestFixture::generateTestDataSet(int seed, TestDataSet& testSet) {
    const double LL_X = 33.5, LL_Y = 53.8;
    const double RU_X = 39.5, RU_Y = 59.8;
    const double MIN_PATH_LENGTH = 200;
    const double MAX_PATH_LENGTH = 500;

    Point2 leftLower(LL_X, LL_Y), rightUpper(RU_X, RU_Y);
    BoundingBox boundingBox(leftLower, rightUpper);
    PathGeneratorConfig pathConfig;
    pathConfig.boundingBox = boundingBox;
    pathConfig.minPathLength = MIN_PATH_LENGTH;
    pathConfig.maxPathLength = MAX_PATH_LENGTH;

    maps::xml3::Doc doc(TestDataPath("driving_config.xml"), maps::xml3::Doc::File);
    DrivingConfig drivingConfig = DrivingConfig::fromXml(doc.root());

    TestConfig config;
    config.drivingConfig = drivingConfig;
    config.pathGeneratorConfig = pathConfig;
    config.testsNumber = TESTS_NUMBER;
    config.trackType = "edge_speed_limit";

    boost::mt19937 randEngine(static_cast<ui32>(seed));
    GeneratorsFactory factory(*graph.GetRoadGraph().RoadGraph, *graph.GetRoadGraph().SuccinctRtree);
    unique_ptr<TestGenerator> tgen = factory.generator(config, randEngine);

    tgen->gen(&testSet);
    UNIT_ASSERT_EQUAL(testSet.tests.size(), TESTS_NUMBER);
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
    UNIT_ASSERT(matchedPath.Path.Exists());

    const TPath& path = matchedPath.Path;
    TPathOnGraph pathOnGraph{path, graph};
    const auto& targetPoint = pathOnGraph.GetTargetPoint();
    const auto coords = graph.GetCoords(targetPoint);

    Cerr << coords.Lon << "," << coords.Lat << Endl;
    UNIT_ASSERT(abs(coords.Lon - refPoint.Lon) < 0.0003);
    UNIT_ASSERT(abs(coords.Lat - refPoint.Lat) < 0.0003);
}

vector<SegmentId> TMapMatcherTestFixture::postprocessMatchedPaths(const TMatchedPaths& matchedPaths) {
    vector<SegmentId> result;

    convertMatchedPathsToSegmentIds(matchedPaths, &result);
    sortAndEraseDuplicate(result);

    for (size_t i = 0; i < result.size(); i++) {
        result[i] = SegmentId{
            graphImpl->RoadGraph->base(result[i].edgeId),
            result[i].segmentIndex};
    }

    return result;
}

vector<SegmentId> TMapMatcherTestFixture::calculateSegments(const TestData& test, TMatcher& matcher, TMatchedPaths& consumer) {
    const auto& signals = test.gpsSignals();

    size_t prevIndex = 0;
    matcher.AppendSignal(NTaxi::NGraph2::ConvertToTaxiGps(signals[0]));
    for (size_t i = 1; i < signals.size(); i++) {
        prevIndex = i;
        matcher.AppendSignal(NTaxi::NGraph2::ConvertToTaxiGps(signals[i]));
    }
    matcher.Flush();

    return postprocessMatchedPaths(consumer);
}

inline double TMapMatcherTestFixture::calculateQuality(const vector<SegmentId>& first, const vector<SegmentId>& second) {
    return 1.0 - static_cast<double>(difference(first, second)) / (first.size() + second.size());
}

void TMapMatcherTestFixture::sortAndEraseDuplicate(vector<SegmentId>& vec) {
    sort(vec.begin(), vec.end());
    vec.erase(unique(vec.begin(), vec.end()), vec.end());
}

void TMapMatcherTestFixture::convertMatchedPathsToSegmentIds(
    const TMatchedPaths& matchedPaths, vector<SegmentId>* ids) {
    for (const TMatchedPath& matchedPath : matchedPaths) {
        for (const auto& segmentPart : matchedPath.Path.GetSegmentParts()) {
            ids->push_back(segmentPart.segmentId);
        }
    }
}

size_t TMapMatcherTestFixture::difference(const vector<SegmentId>& a, const vector<SegmentId>& b) {
    assert(is_sorted(a.begin(), a.end()) && is_sorted(b.begin(), b.end()));
    size_t matchesCount = 0;
    size_t i = 0;
    size_t j = 0;
    while (i < a.size() && j < b.size()) {
        if (a[i] == b[j]) {
            matchesCount++;
            i++;
            j++;
        } else if (a[i] < b[j]) {
            i++;
        } else {
            j++;
        }
    }
    return a.size() + b.size() - 2 * matchesCount;
}

std::vector<NTaxi::NGraph2::TGpsSignal> TMapMatcherTestFixture::loadSignalsFromFile(
    const TString& filename) {
    return NTaxi::NGraph2::LoadSignalsFromFile(filename);
}
