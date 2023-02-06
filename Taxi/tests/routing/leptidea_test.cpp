#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <taxi/graph/libs/graph/closures.h>
#include <taxi/graph/libs/graph/graph.h>
#include <taxi/graph/libs/graph/persistent_index.h>
#include <taxi/graph/libs/graph/road_graph_helpers.h>
#include <taxi/graph/libs/graph-test/graph_test_data.h>
#include <taxi/graph/libs/routing/leptidea.h>

using TaxiGraph = NTaxi::NGraph2::TGraph;
using NTaxi::NGraph2::TClosureInfo;
using NTaxi::NGraph2::TClosures;
using NTaxi::NGraph2::TJamInfo;
using NTaxi::NGraph2::TJams;
using NTaxi::NGraph2::TLeptidea;
using NTaxi::NGraph2::TPoint;
using NTaxi::NGraph2::TPersistentIndex;

using namespace NTaxi::NGraph2Literals;

namespace {
    TString GraphPath(const TStringBuf& str) {
        static const TString prefix = "taxi/graph/data/graph3/";
        return BinaryPath(prefix + str);
    }

    std::unique_ptr<TLeptidea> GetTestLeptidea(const TaxiGraph& graph) {
        auto leptidea = std::make_unique<TLeptidea>(graph,
            GraphPath("l6a_topology.fb.7").c_str(),
            GraphPath("l6a_data.fb.7").c_str());
        leptidea->Init(1);
        return leptidea;
    }
}

struct TLeptideaTestFixture: public ::NUnitTest::TBaseTestCase,
                             public NTaxi::NGraph2::TGraphTestData {
};

Y_UNIT_TEST_SUITE_F(leptidea_interface, TLeptideaTestFixture) {
    Y_UNIT_TEST(fb_leptidea_line_path) {
        const auto& leptidea = GetTestLeptidea(GetTestRoadGraph());

        const TPoint from{37.529272, 55.697285};
        const TPoint to{37.526510, 55.698854};

        const auto& routes = leptidea->CalcRoute(0, from, to);

        UNIT_ASSERT_EQUAL(routes.size(), 1);
        UNIT_ASSERT_DOUBLES_EQUAL(routes[0].GetDuration(), 18.94757271, 1e-2);
        UNIT_ASSERT_DOUBLES_EQUAL(routes[0].GetLength(), 246.3184357, 1e-2);

        const auto& path = routes[0].Path;
        double length = 0;
        double duration = 0;
        for (size_t i = 0; i < path.size(); i++) {
            if (path[i].Duration) {
                UNIT_ASSERT(duration <= *path[i].Duration);
                duration = *path[i].Duration;
            }

            if (path[i].Length) {
                UNIT_ASSERT(length <= *path[i].Length);
                length = *path[i].Length;
            }
        }
    }

    Y_UNIT_TEST(fb_leptidea_big_path) {
        const auto& leptidea = GetTestLeptidea(GetTestRoadGraph());

        const TPoint from{37.492241, 55.653965};
        const TPoint to{37.543391, 55.892239};

        const auto& routes = leptidea->CalcRoute(0, from, to);

        UNIT_ASSERT_EQUAL(routes.size(), 21);
        UNIT_ASSERT_DOUBLES_EQUAL(routes[0].GetDuration(), 2195.250732, 1e-2);
        UNIT_ASSERT_DOUBLES_EQUAL(routes[0].GetLength(), 33126.46484, 1e-2);

        const auto& path = routes[0].Path;
        double length = 0;
        double duration = 0;
        for (size_t i = 0; i < path.size(); i++) {
            if (path[i].Duration) {
                UNIT_ASSERT(duration <= *path[i].Duration);
                duration = *path[i].Duration;
            }

            if (path[i].Length) {
                UNIT_ASSERT(length <= *path[i].Length);
                length = *path[i].Length;
            }
        }
    }

    Y_UNIT_TEST(fb_leptidea_same_edge_path) {
        const auto& leptidea = GetTestLeptidea(GetTestRoadGraph());

        const TPoint from{37.527497, 55.698309};
        const TPoint to{37.522926, 55.700941};

        const auto& routes = leptidea->CalcRoute(0, from, to);

        UNIT_ASSERT_EQUAL(routes.size(), 1);
        UNIT_ASSERT_DOUBLES_EQUAL(routes[0].GetDuration(), 31.56914139, 1e-2);
        UNIT_ASSERT_DOUBLES_EQUAL(routes[0].GetLength(), 410.3988342, 1e-2);
    }

    Y_UNIT_TEST(fb_leptidea_many_paths) {
        const auto& leptidea = GetTestLeptidea(GetTestRoadGraph());

        const TPoint from{37.541258, 55.703967};
        const TPoint to{37.521246, 55.702218};

        const auto& routes = leptidea->CalcRoute(0, from, to);

        UNIT_ASSERT_EQUAL(routes.size(), 2);
        UNIT_ASSERT_EQUAL(routes[0].Path.size(), 34);
        UNIT_ASSERT_DOUBLES_EQUAL(routes[0].GetDuration(), 197.2241058, 1e-2);
        UNIT_ASSERT_DOUBLES_EQUAL(routes[0].GetLength(), 1775.300049, 1e-2);
    }

    Y_UNIT_TEST(fb_leptidea_closures) {
        // https://yandex.ru/maps/-/CKubvBLv

        using namespace NTaxi::NGraph2Literals;
        using namespace std::chrono_literals;

        const auto& leptidea = GetTestLeptidea(GetTestRoadGraph());
        TPersistentIndex index(GraphPath("edges_persistent_index.fb").data());

        const TPoint from{37.533478, 55.694876};
        const TPoint to{37.518142, 55.703703};

        auto routes = leptidea->CalcRoute(0, from, to);
        UNIT_ASSERT_EQUAL(routes.size(), 1);

        // fix one route
        auto& route = routes[0];

        // check without closures
        UNIT_ASSERT_EQUAL(route.Blocked, std::nullopt);

        const auto& now = std::chrono::system_clock::now();
        auto closures = TClosures(index, now);

        // check with empty closures
        leptidea->ApplyClosures(closures, route);
        UNIT_ASSERT_EQUAL(route.Blocked, false);

        // check with closure
        closures.AddClosure(6302_eid, /* region */ 0, now - 10'000s, now + 10'000s);
        leptidea->ApplyClosures(closures, route);
        UNIT_ASSERT_EQUAL(route.Blocked, true);
    }

    Y_UNIT_TEST(fb_leptidea_dead_jam) {
        // https://yandex.ru/maps/-/CKubvBLv

        using namespace NTaxi::NGraph2Literals;
        using namespace std::chrono_literals;

        const auto& leptidea = GetTestLeptidea(GetTestRoadGraph());
        TPersistentIndex index(GraphPath("edges_persistent_index.fb").data());

        const TPoint from{37.533478, 55.694876};
        const TPoint to{37.518142, 55.703703};

        auto routes = leptidea->CalcRoute(0, from, to);
        UNIT_ASSERT_EQUAL(routes.size(), 1);

        // fix one route
        auto& route = routes[0];

        // check without jams
        UNIT_ASSERT_EQUAL(route.HasDeadJam, std::nullopt);

        auto jams = TJams(index);

        // check with empty jams
        leptidea->ApplyJams(jams, route);
        UNIT_ASSERT_EQUAL(route.HasDeadJam, false);

        // check with jams
        jams.AddJam(6302_eid, /* speed */ 0.0, /* region */ 0, /* deadJam */ true);
        leptidea->ApplyJams(jams, route);
        UNIT_ASSERT_EQUAL(route.HasDeadJam, true);
    }

    Y_UNIT_TEST(fb_leptidea_jam) {
        // https://yandex.ru/maps/-/CKubvBLv

        using namespace NTaxi::NGraph2Literals;
        using namespace std::chrono_literals;

        const auto& leptidea = GetTestLeptidea(GetTestRoadGraph());
        TPersistentIndex index(GraphPath("edges_persistent_index.fb").data());

        const TPoint from{37.533478, 55.694876};
        const TPoint to{37.518142, 55.703703};

        auto routes = leptidea->CalcRoute(0, from, to);
        UNIT_ASSERT_EQUAL(routes.size(), 1);

        // fix one route
        auto& route = routes[0];

        // check without jams
        UNIT_ASSERT_DOUBLES_EQUAL(route.GetDuration(), 105.9110107, 1e-2);
        UNIT_ASSERT_DOUBLES_EQUAL(route.GetLength(), 1376.843262, 1e-2);

        auto jams = TJams(index);

        // check with empty jams
        leptidea->ApplyJams(jams, route);
        UNIT_ASSERT_DOUBLES_EQUAL(route.GetDuration(), 105.9110107, 1e-2);
        UNIT_ASSERT_DOUBLES_EQUAL(route.GetLength(), 1376.843262, 1e-2);

        // check with jams
        jams.AddJam(6302_eid, /* speed */ 1);
        leptidea->ApplyJams(jams, route);
        UNIT_ASSERT_DOUBLES_EQUAL(route.GetDuration(), 485.2852168, 1e-2);
        UNIT_ASSERT_DOUBLES_EQUAL(route.GetLength(), 1376.843262, 1e-2);
    }
}
