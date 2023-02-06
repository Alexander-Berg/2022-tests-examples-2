#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <taxi/graph/libs/graph-test/graph_test_data.h>
#include <taxi/graph/libs/graph/graph.h>
#include <taxi/graph/libs/route_matcher/route_matcher.hpp>

using NTaxi::NGraph2::TEdgeData;
using NTaxi::NGraph2::TGraph;
using NTaxi::NGraph2::TId;
using NTaxi::NGraph2::TPoint;
using NTaxi::NGraph2::TPolyline;
using NTaxi::NGraph2::TPositionOnEdge;

using namespace NTaxi::NGraph2Literals;

namespace {
#define TEST_DEBUG(x) \
    { Cerr << #x << ": " << x << "\n"; }

    TPolyline MakePoly(std::vector<maps::geolib3::Point2> poly) {
        TPolyline ret;
        ret.AsGeolibPolyline() = maps::geolib3::Polyline2(std::move(poly));
        return ret;
    }

    TPolyline MakeLoopPoly() {
        std::vector<maps::geolib3::Point2> poly =
            {
                {37.49451537142868, 55.73235636698644},
                {37.49288458834762, 55.73205367181036},
                {37.491253805266574, 55.73173886632682},
                {37.4894942761528, 55.73142405829385},
                {37.48745579730149, 55.73106081508778},
                {37.48556752215501, 55.730721785033055},
                {37.48374362002486, 55.7303585352647},
                {37.482713651763156, 55.73043118548992},
                {37.482520532714084, 55.73103659875335},
                {37.483293008910366, 55.731460382427755},
                {37.484580469237514, 55.7316662185455},
                {37.48633999835129, 55.731981024617355},
                {37.48807806979294, 55.73225950478654},
                {37.48930115710372, 55.732441121213334},
                {37.48992342959519, 55.73216264234529},
                {37.490266752349086, 55.73173886632682},
                {37.490824651824184, 55.73112135585783},
                {37.49131817828292, 55.73054016057317},
                {37.49191899310225, 55.72989841401874},
                {37.492519807921596, 55.72928087431342},
                {37.493077707396694, 55.7287238693022}};
        return MakePoly(std::move(poly));
    }

    TPolyline MakePolyForCaseWithKeyPointsNearBegin() {
        std::vector<maps::geolib3::Point2> poly = {
            {37.582857, 55.806307},
            {37.582764, 55.806451},
            {37.582764, 55.806492},
            {37.582793, 55.806532},
            {37.582849, 55.80656},
            {37.583017, 55.806595},
            {37.583216, 55.806187},
            {37.583226, 55.806154},
            {37.583216, 55.806125},
            {37.583177, 55.806106},
            {37.583011, 55.806067},
            {37.582857, 55.806307},
            {37.582764, 55.806451},
            {37.582764, 55.806492},
            {37.582793, 55.806532},
            {37.582849, 55.80656},
            {37.583017, 55.806595},
            {37.583216, 55.806187},
            {37.583226, 55.806154},
            {37.583216, 55.806125},
            {37.583177, 55.806106},
            {37.583011, 55.806067},
            {37.583074, 55.805943},
            {37.583102, 55.805894},
            {37.583169, 55.805761},
            {37.582886, 55.805727},
            {37.582802, 55.805715},
            {37.582377, 55.805651},
            {37.582164, 55.805618},
            {37.581858, 55.805567},
            {37.581743, 55.805549},
            {37.581398, 55.805492},
            {37.581364, 55.80556},
            {37.581352, 55.805584},
            {37.581203, 55.805811},
            {37.581076, 55.806007},
        };
        return MakePoly(std::move(poly));
    }

    TPolyline MakeTestPolyline(size_t maxPoints = 100, double step = 0.001) {
        TPolyline ret;
        ret.ReservePoints(maxPoints);

        NTaxi::NGraph2::TPoint point(37, 55);
        for (size_t i = 0; i < maxPoints; ++i) {
            auto p = point;
            //p.Lat += i * step;
            p.Lon += i * step;
            ret.AddPoint(p);
        }

        return ret;
    }

    TPolyline MakeTestPolylineWithRepeatedLastPoint(size_t maxPoints = 100, double step = 0.001) {
        TPolyline ret;
        ret.ReservePoints(maxPoints);

        NTaxi::NGraph2::TPoint point(37, 55);
        for (size_t i = 0; i < maxPoints; ++i) {
            auto p = point;
            p.Lon += i * step;
            ret.AddPoint(p);
        }
        ret.AddPoint(ret.PointAt(maxPoints-1));

        return ret;
    }

    TVector<TPoint> MakeKeyPoints(TPolyline poly) {
        TVector<TPoint> ret;
        ret.reserve(poly.PointsSize());
        for (const auto& point : poly.AsGeolibPolyline().points()) {
            ret.push_back(point);
        }
        return ret;
    }
}

Y_UNIT_TEST_SUITE(route_matcher_test) {
    NTaxi::NRouteMatcher::TTimeDistanceIndex MakeTimeDistanceIndex(const TPolyline& poly) {
        NTaxi::NRouteMatcher::TTimeDistanceIndex ret;
        const size_t pointsCount = poly.PointsSize();
        const size_t distanceUnit = 1000;
        const size_t timeUnit = 10;
        ret.reserve(pointsCount);

        for (size_t i = 0; i < pointsCount; ++i) {
            NTaxi::NRouteMatcher::TTimeDistance timeDistance;
            timeDistance.Meters = i * distanceUnit;
            timeDistance.Seconds = i * timeUnit;
            ret.push_back(timeDistance);
        }

        return ret;
    }

    Y_UNIT_TEST(TestMatcherWithTimeDistances) {
        using ::NTaxi::NRouteMatcher::DistancesByRoute;
        const auto poly = MakeTestPolyline(11);
        UNIT_ASSERT_EQUAL(poly.PointsSize(), 11);
        UNIT_ASSERT_EQUAL(poly.SegmentsSize(), 10);
        const auto timeDistanceIndex = MakeTimeDistanceIndex(poly);

        const double routeTimeDuration = timeDistanceIndex.back().Seconds;
        const double routeLength = timeDistanceIndex.back().Meters;
        const double maxDistance = 1000;

        UNIT_ASSERT_DOUBLES_EQUAL(routeTimeDuration, 100.0, 1.0);
        UNIT_ASSERT_DOUBLES_EQUAL(routeLength, 10000.0, 1.0);

        NTaxi::NRouteMatcher::TRouteMatcher routeMatcher;
        UNIT_ASSERT(!routeMatcher.HasRoute());
        routeMatcher.SetRoute(poly, timeDistanceIndex, routeTimeDuration);
        UNIT_ASSERT(routeMatcher.HasRoute());

        {
            // Test first point at start of polyline
            const auto& point = poly.PointAt(0);
            routeMatcher.SetRoute(poly, timeDistanceIndex, routeTimeDuration);
            routeMatcher.Adjust(point, maxDistance);
            auto timeleftfull = routeMatcher.GetTimeDistanceLeft();
            UNIT_ASSERT(timeleftfull.has_value());
            const auto& timeleft = timeleftfull->TimeDistance;
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.Meters, routeLength, 1.0);
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.Seconds, routeTimeDuration, 1.0);
        }
        {
            // Test last point at end of polyline
            const auto& point = poly.PointAt(poly.PointsSize() - 1);
            routeMatcher.SetRoute(poly, timeDistanceIndex, routeTimeDuration);
            routeMatcher.Adjust(point, maxDistance);
            auto timeleftfull = routeMatcher.GetTimeDistanceLeft();
            UNIT_ASSERT(timeleftfull.has_value());
            const auto& timeleft = timeleftfull->TimeDistance;
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.Meters, 0, 1.0);
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.Seconds, 0.0, 1.0);
        }
        {
            // Test point at midle of polyline
            const auto& point = poly.PointAt(poly.PointsSize() / 2);
            routeMatcher.SetRoute(poly, timeDistanceIndex, routeTimeDuration);
            routeMatcher.Adjust(point, maxDistance);
            auto timeleftfull = routeMatcher.GetTimeDistanceLeft();
            UNIT_ASSERT(timeleftfull.has_value());
            const auto& timeleft = timeleftfull->TimeDistance;
            const auto expectedLength = 5000.0;
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.Meters, expectedLength, 5.0);
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.Seconds, routeTimeDuration / 2, 1.0);
        }
        {
            // Test point to far from route
            const auto& point = NTaxi::NGraph2::TPoint(50, 50);
            routeMatcher.SetRoute(poly, timeDistanceIndex, routeTimeDuration);
            routeMatcher.Adjust(point, maxDistance);
            auto timeleft = routeMatcher.GetTimeDistanceLeft();
            UNIT_ASSERT(timeleft.has_value() == false);
        }

        {
            // Test point to far from route after success
            {
                // Successfull (middle point)
                const auto& point = poly.PointAt(poly.PointsSize() / 2);
                routeMatcher.SetRoute(poly, timeDistanceIndex, routeTimeDuration);
                routeMatcher.Adjust(point, maxDistance);
                auto timeleftfull = routeMatcher.GetTimeDistanceLeft();
                UNIT_ASSERT(timeleftfull.has_value());
            }

            const auto& point = NTaxi::NGraph2::TPoint(50, 50);
            routeMatcher.Adjust(point, maxDistance);
            auto timeleft = routeMatcher.GetTimeDistanceLeft();
            UNIT_ASSERT(timeleft.has_value() == false);
        }

        routeMatcher.ResetRoute();
        UNIT_ASSERT(!routeMatcher.HasRoute());
    }

    Y_UNIT_TEST(TestMatcherResultLessThanPrevious) {
        using ::NTaxi::NRouteMatcher::DistancesByRoute;
        const auto poly = MakeTestPolyline(10);
        const auto timeDistanceIndex = MakeTimeDistanceIndex(poly);

        const double routeTimeDuration = timeDistanceIndex.back().Seconds;
        const double routeLength = timeDistanceIndex.back().Meters;
        const double maxDistance = 1000;

        UNIT_ASSERT_DOUBLES_EQUAL(routeTimeDuration, 90.0, 1.0);
        UNIT_ASSERT_DOUBLES_EQUAL(routeLength, 9000.0, 1.0);

        NTaxi::NRouteMatcher::TRouteMatcher routeMatcher;
        routeMatcher.SetRoute(poly, timeDistanceIndex, routeTimeDuration);

        const auto& point1 = poly.PointAt(1);
        routeMatcher.Adjust(point1, maxDistance);
        auto timeleftfull1 = routeMatcher.GetTimeDistanceLeft();
        UNIT_ASSERT(timeleftfull1.has_value());
        const auto& timeleft1 = timeleftfull1->TimeDistance;

        // Should not change result
        const auto& point0 = poly.PointAt(0);
        routeMatcher.Adjust(point0, maxDistance);
        auto timeleftfull0 = routeMatcher.GetTimeDistanceLeft();
        UNIT_ASSERT(timeleftfull0.has_value());
        const auto& timeleft0 = timeleftfull0->TimeDistance;
        UNIT_ASSERT_DOUBLES_EQUAL(timeleft0.Meters, timeleft1.Meters, 1.0);
        UNIT_ASSERT_DOUBLES_EQUAL(timeleft0.Seconds, timeleft1.Seconds, 1.0);

        // Next point has better result
        const auto& point2 = poly.PointAt(2);
        routeMatcher.Adjust(point2, maxDistance);
        auto timeleftfull2 = routeMatcher.GetTimeDistanceLeft();
        UNIT_ASSERT(timeleftfull2.has_value());
        const auto& timeleft2 = timeleftfull2->TimeDistance;
        UNIT_ASSERT_LT(timeleft2.Meters, timeleft1.Meters);
        UNIT_ASSERT_LT(timeleft2.Seconds, timeleft1.Seconds);

        // Reset stored last position by setting new route
        routeMatcher.SetRoute(poly, timeDistanceIndex, routeTimeDuration);
        routeMatcher.Adjust(point0, maxDistance);
        auto timeleftfull0_after_reset = routeMatcher.GetTimeDistanceLeft();
        UNIT_ASSERT(timeleftfull0_after_reset.has_value());
        const auto& timeleft = timeleftfull0_after_reset->TimeDistance;
        // New time/distance can be worse than previous after new route set
        UNIT_ASSERT_GT(timeleft.Meters, timeleft2.Meters);
        UNIT_ASSERT_GT(timeleft.Seconds, timeleft2.Seconds);
    }

    Y_UNIT_TEST(TestIntermediatePoints) {
        using ::NTaxi::NRouteMatcher::DistancesByRoute;
        auto poly = MakeTestPolyline(101);
        const auto key_points_count = 11;
        auto key_points = MakeKeyPoints(MakeTestPolyline(key_points_count, 0.01));
        UNIT_ASSERT_EQUAL(key_points.size(), key_points_count);

        auto distances = DistancesByRoute(poly);
        const auto timeDistanceIndex = MakeTimeDistanceIndex(poly);
        const double routeTimeDuration = timeDistanceIndex.back().Seconds;
        const double routeLength = timeDistanceIndex.back().Meters;
        const double maxDistance = 1000;

        UNIT_ASSERT_DOUBLES_EQUAL(routeTimeDuration, 1000.0, 1.0);
        UNIT_ASSERT_DOUBLES_EQUAL(routeLength, 100000.0, 1.0);

        NTaxi::NRouteMatcher::TRouteMatcher routeMatcher;
        UNIT_ASSERT(!routeMatcher.HasRoute());
        UNIT_ASSERT(routeMatcher.SetRoute(poly, key_points, timeDistanceIndex, routeTimeDuration, 100));
        UNIT_ASSERT(routeMatcher.HasRoute());

        {
            // Test first point at start of polyline
            const auto& point = poly.PointAt(0);
            UNIT_ASSERT(routeMatcher.SetRoute(poly, key_points, timeDistanceIndex, routeTimeDuration, 100));
            routeMatcher.Adjust(point, maxDistance);
            auto timeleftfull = routeMatcher.GetTimeDistanceLeft();
            UNIT_ASSERT(timeleftfull.has_value());
            const auto& timeleft = timeleftfull->TimeDistance;
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.Meters, routeLength, 1.0);
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.Seconds, routeTimeDuration, 1.0);

            const auto& etas = timeleftfull->all_etas;
            UNIT_ASSERT_EQUAL(key_points_count, etas.size());

            const auto expected_times = TVector<double>{0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000};
            for (size_t i = 0; i < key_points_count; ++i) {
                UNIT_ASSERT_DOUBLES_EQUAL(etas.at(i).Seconds, expected_times[i], 1.0);
            }

            const auto expected_distances = TVector<double>{0, 10000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000};
            for (size_t i = 0; i < key_points_count; ++i) {
                UNIT_ASSERT_DOUBLES_EQUAL(etas.at(i).Meters, expected_distances[i], 1.0);
            }
        }
        {
            // Test last point at end of polyline
            const auto& point = poly.PointAt(poly.PointsSize() - 1);
            UNIT_ASSERT(routeMatcher.SetRoute(poly, key_points, timeDistanceIndex, routeTimeDuration, 100));
            routeMatcher.Adjust(point, maxDistance);
            auto timeleftfull = routeMatcher.GetTimeDistanceLeft();
            UNIT_ASSERT(timeleftfull.has_value());
            const auto& timeleft = timeleftfull->TimeDistance;
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.Meters, 0, 1.0);
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.Seconds, 0.0, 1.0);

            const auto& etas = timeleftfull->all_etas;
            UNIT_ASSERT_EQUAL(key_points_count, etas.size());

            /// negative values mean that we passed this point
            const auto expected_times = TVector<double>{-1000, -900, -800, -700, -600, -500, -400, -300, -200, -100, 0};
            const auto expected_distances = TVector<double>{-100000, -90000, -80000, -70000, -60000, -50000, -40000, -30000, -20000, -10000, 0};

            for (size_t i = 0; i < key_points_count; ++i) {
                UNIT_ASSERT_DOUBLES_EQUAL(etas.at(i).Meters, expected_distances[i], 1.0);
            }

            for (size_t i = 0; i < key_points_count; ++i) {
                UNIT_ASSERT_DOUBLES_EQUAL(etas.at(i).Seconds, expected_times[i], 1.0);
            }
        }
        {
            // Test point to far from route
            const auto& point = NTaxi::NGraph2::TPoint(50, 50);
            UNIT_ASSERT(routeMatcher.SetRoute(poly, key_points, timeDistanceIndex, routeTimeDuration, 100));
            routeMatcher.Adjust(point, maxDistance);
            auto timeleft = routeMatcher.GetTimeDistanceLeft();
            UNIT_ASSERT(timeleft.has_value() == false);
        }

        {
            // Test point to far from route after success
            {
                // Successfull (middle point)
                const auto& point = poly.PointAt(poly.PointsSize() / 2);
                UNIT_ASSERT(routeMatcher.SetRoute(poly, key_points, timeDistanceIndex, routeTimeDuration, 100));
                routeMatcher.Adjust(point, maxDistance);
                auto timeleftfull = routeMatcher.GetTimeDistanceLeft();
                UNIT_ASSERT(timeleftfull.has_value());
            }

            const auto& point = NTaxi::NGraph2::TPoint(50, 50);
            routeMatcher.Adjust(point, maxDistance);
            auto timeleft = routeMatcher.GetTimeDistanceLeft();
            UNIT_ASSERT(timeleft.has_value() == false);
        }

        routeMatcher.ResetRoute();
        UNIT_ASSERT(!routeMatcher.HasRoute());
    }

    Y_UNIT_TEST(TestMatcherWithTimeDistancesSimple2) {
        using ::NTaxi::NRouteMatcher::DistancesByRoute;
        const auto poly = MakeTestPolyline(3);
        UNIT_ASSERT_EQUAL(poly.PointsSize(), 3);
        UNIT_ASSERT_EQUAL(poly.SegmentsSize(), 2);
        const auto timeDistanceIndex = MakeTimeDistanceIndex(poly);

        const double routeTimeDuration = timeDistanceIndex.back().Seconds;
        const double routeLength = timeDistanceIndex.back().Meters;
        const double maxDistance = 1000;

        UNIT_ASSERT_DOUBLES_EQUAL(routeTimeDuration, 20.0, 1.0);
        UNIT_ASSERT_DOUBLES_EQUAL(routeLength, 2000.0, 1.0);

        NTaxi::NRouteMatcher::TRouteMatcher routeMatcher;
        UNIT_ASSERT(!routeMatcher.HasRoute());
        routeMatcher.SetRoute(poly, timeDistanceIndex, routeTimeDuration);
        UNIT_ASSERT(routeMatcher.HasRoute());

        {
            // Test first point at start of polyline
            const auto& point = poly.PointAt(0);
            routeMatcher.SetRoute(poly, timeDistanceIndex, routeTimeDuration);
            routeMatcher.Adjust(point, maxDistance);
            auto timeleftfull = routeMatcher.GetTimeDistanceLeft();
            UNIT_ASSERT(timeleftfull.has_value());
            const auto& timeleft = timeleftfull->TimeDistance;
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.Meters, routeLength, 1.0);
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.Seconds, routeTimeDuration, 1.0);
        }
        {
            // Test last point at end of polyline
            const auto& point = poly.PointAt(poly.PointsSize() - 1);
            routeMatcher.SetRoute(poly, timeDistanceIndex, routeTimeDuration);
            routeMatcher.Adjust(point, maxDistance);
            auto timeleftfull = routeMatcher.GetTimeDistanceLeft();
            UNIT_ASSERT(timeleftfull.has_value());
            const auto& timeleft = timeleftfull->TimeDistance;
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.Meters, 0, 1.0);
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.Seconds, 0.0, 1.0);
        }
        {
            // Test point at midle of polyline
            const auto& point = poly.PointAt(poly.PointsSize() / 2);
            routeMatcher.SetRoute(poly, timeDistanceIndex, routeTimeDuration);
            routeMatcher.Adjust(point, maxDistance);
            auto timeleftfull = routeMatcher.GetTimeDistanceLeft();
            UNIT_ASSERT(timeleftfull.has_value());
            const auto& timeleft = timeleftfull->TimeDistance;
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.Seconds, routeTimeDuration / 2, 1.0);
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.Meters, routeLength / 2, 5.0);
        }

        routeMatcher.ResetRoute();
        UNIT_ASSERT(!routeMatcher.HasRoute());
    }

    Y_UNIT_TEST(TestMatcherWithTimeDistancesSimple1) {
        using ::NTaxi::NRouteMatcher::DistancesByRoute;
        const auto poly = MakeTestPolyline(2);
        UNIT_ASSERT_EQUAL(poly.PointsSize(), 2);
        UNIT_ASSERT_EQUAL(poly.SegmentsSize(), 1);
        const auto timeDistanceIndex = MakeTimeDistanceIndex(poly);

        const double routeTimeDuration = timeDistanceIndex.back().Seconds;
        const double routeLength = timeDistanceIndex.back().Meters;
        const double maxDistance = 1000;

        UNIT_ASSERT_DOUBLES_EQUAL(routeTimeDuration, 10.0, 1.0);
        UNIT_ASSERT_DOUBLES_EQUAL(routeLength, 1000.0, 1.0);

        NTaxi::NRouteMatcher::TRouteMatcher routeMatcher;
        UNIT_ASSERT(!routeMatcher.HasRoute());
        routeMatcher.SetRoute(poly, timeDistanceIndex, routeTimeDuration);
        UNIT_ASSERT(routeMatcher.HasRoute());

        {
            // Test first point at start of polyline
            const auto& point = poly.PointAt(0);
            routeMatcher.SetRoute(poly, timeDistanceIndex, routeTimeDuration);
            routeMatcher.Adjust(point, maxDistance);
            auto timeleftfull = routeMatcher.GetTimeDistanceLeft();
            UNIT_ASSERT(timeleftfull.has_value());
            const auto& timeleft = timeleftfull->TimeDistance;
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.Meters, routeLength, 1.0);
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.Seconds, routeTimeDuration, 1.0);
        }
        {
            // Test last point at end of polyline
            const auto& point = poly.PointAt(poly.PointsSize() - 1);
            routeMatcher.SetRoute(poly, timeDistanceIndex, routeTimeDuration);
            routeMatcher.Adjust(point, maxDistance);
            auto timeleftfull = routeMatcher.GetTimeDistanceLeft();
            UNIT_ASSERT(timeleftfull.has_value());
            const auto& timeleft = timeleftfull->TimeDistance;
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.Meters, 0, 1.0);
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.Seconds, 0.0, 1.0);
        }
        {
            // Test point at midle of polyline
            auto point = NTaxi::NGraph2::TPoint(
                (poly.PointAt(1).Lon + poly.PointAt(0).Lon) / 2,
                (poly.PointAt(1).Lat + poly.PointAt(0).Lat) / 2);
            routeMatcher.SetRoute(poly, timeDistanceIndex, routeTimeDuration);
            routeMatcher.Adjust(point, maxDistance);
            auto timeleftfull = routeMatcher.GetTimeDistanceLeft();
            UNIT_ASSERT(timeleftfull.has_value());
            const auto& timeleft = timeleftfull->TimeDistance;
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.Seconds, routeTimeDuration / 2, 1.0);
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.Meters, routeLength / 2, 1.0);
        }

        routeMatcher.ResetRoute();
        UNIT_ASSERT(!routeMatcher.HasRoute());
    }

    Y_UNIT_TEST(TestMatcherWithTimeDistancesNegativeDistaince) {
        using ::NTaxi::NRouteMatcher::DistancesByRoute;
        const auto poly = MakeTestPolyline(2, 0.00001);
        UNIT_ASSERT_EQUAL(poly.PointsSize(), 2);
        UNIT_ASSERT_EQUAL(poly.SegmentsSize(), 1);
        const auto timeDistanceIndex = MakeTimeDistanceIndex(poly);

        const double routeTimeDuration = timeDistanceIndex.back().Seconds;
        const double routeLength = timeDistanceIndex.back().Meters;
        const double maxDistance = 1000;

        UNIT_ASSERT_DOUBLES_EQUAL(routeTimeDuration, 10.0, 1.0);
        UNIT_ASSERT_DOUBLES_EQUAL(routeLength, 1000.0, 1.0);

        NTaxi::NRouteMatcher::TRouteMatcher routeMatcher;
        UNIT_ASSERT(!routeMatcher.HasRoute());
        routeMatcher.SetRoute(poly, timeDistanceIndex, routeTimeDuration);
        UNIT_ASSERT(routeMatcher.HasRoute());

        {
            // Test first point at start of polyline
            auto point = poly.PointAt(0);
            point.Lat -= 0.0001;
            routeMatcher.SetRoute(poly, timeDistanceIndex, routeTimeDuration);
            routeMatcher.Adjust(point, maxDistance);
            auto timeleftfull = routeMatcher.GetTimeDistanceLeft();
            UNIT_ASSERT(timeleftfull.has_value());
            const auto& timeleft = timeleftfull->TimeDistance;
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.Meters, routeLength, 1.0);
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.Seconds, routeTimeDuration, 1.0);
        }

        routeMatcher.ResetRoute();
        UNIT_ASSERT(!routeMatcher.HasRoute());
    }

    Y_UNIT_TEST(TestMatcherWithRouteWithSamePoints) {
        using ::NTaxi::NRouteMatcher::DistancesByRoute;
        const auto poly = MakeTestPolyline(2, 0.0);
        UNIT_ASSERT_EQUAL(poly.PointsSize(), 2);
        UNIT_ASSERT_EQUAL(poly.SegmentsSize(), 1);
        const auto timeDistanceIndex = MakeTimeDistanceIndex(poly);

        const double routeTimeDuration = timeDistanceIndex.back().Seconds;
        const double routeLength = timeDistanceIndex.back().Meters;
        const double maxDistance = 1000;

        UNIT_ASSERT_DOUBLES_EQUAL(routeTimeDuration, 10.0, 1.0);
        UNIT_ASSERT_DOUBLES_EQUAL(routeLength, 1000.0, 1.0);

        NTaxi::NRouteMatcher::TRouteMatcher routeMatcher;
        UNIT_ASSERT(!routeMatcher.HasRoute());
        routeMatcher.SetRoute(poly, timeDistanceIndex, routeTimeDuration);
        UNIT_ASSERT(routeMatcher.HasRoute());

        {
            // Test first point at start of polyline
            auto point = poly.PointAt(0);
            point.Lat -= 0.0001;
            routeMatcher.SetRoute(poly, timeDistanceIndex, routeTimeDuration);
            routeMatcher.Adjust(point, maxDistance);
            auto timeleftfull = routeMatcher.GetTimeDistanceLeft();
            UNIT_ASSERT(timeleftfull.has_value());
            const auto& timeleft = timeleftfull->TimeDistance;
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.Meters, routeLength, 1.0);
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.Seconds, routeTimeDuration, 1.0);
        }

        routeMatcher.ResetRoute();
        UNIT_ASSERT(!routeMatcher.HasRoute());
    }

    Y_UNIT_TEST(TestSelfIntersectedLoop) {
        using ::NTaxi::NRouteMatcher::DistancesByRoute;
        /// Make loop poly
        //             ____\_____
        //            /    /     \                //
        //            |          |                //
        //            \-----<----+--<-----        //
        //                       |
        const auto poly = MakeLoopPoly();
        const auto timeDistanceIndex = MakeTimeDistanceIndex(poly);

        const double routeTimeDuration = timeDistanceIndex.back().Seconds;
        const double routeLength = timeDistanceIndex.back().Meters;
        const double maxDistance = 50;
        // point at intersection
        // much closer to further segment
        const auto point0 = TPoint{37.4903552652465, 55.7316848739632};
        // point on loop after intersection
        const auto point1 = TPoint{37.4893808651075, 55.7314608758464};

        TEST_DEBUG(poly.PointsSize());
        UNIT_ASSERT_EQUAL(poly.PointsSize(), 21);
        UNIT_ASSERT_EQUAL(poly.SegmentsSize(), 20);
        UNIT_ASSERT_DOUBLES_EQUAL(routeTimeDuration, 200.0, 1.0);
        UNIT_ASSERT_DOUBLES_EQUAL(routeLength, 20000.0, 1.0);

        NTaxi::NRouteMatcher::TRouteMatcher routeMatcher;
        routeMatcher.SetMaxAdjustCandidates(4);
        UNIT_ASSERT(!routeMatcher.HasRoute());
        routeMatcher.SetRoute(poly, timeDistanceIndex, routeTimeDuration);
        UNIT_ASSERT(routeMatcher.HasRoute());

        {
            // Test first point at start of polyline
            routeMatcher.SetRoute(poly, timeDistanceIndex, routeTimeDuration);
            NTaxi::NRouteMatcher::TTimeDistance timeleft0;
            NTaxi::NRouteMatcher::TTimeDistance timeleft1;
            NTaxi::NRouteMatcher::TTimeDistance timeleft2;  // for same point as time_distance0
            {
                routeMatcher.Adjust(point0, maxDistance);
                auto timeleftfull = routeMatcher.GetTimeDistanceLeft();
                UNIT_ASSERT(timeleftfull.has_value());
                timeleft0 = timeleftfull->TimeDistance;
                TEST_DEBUG(timeleftfull->position_on_route.segmentIndex);
                UNIT_ASSERT_DOUBLES_EQUAL(timeleft0.Meters, 17520, 1.0);
                UNIT_ASSERT_DOUBLES_EQUAL(timeleft0.Seconds, 175, 1.0);
            }

            {
                routeMatcher.Adjust(point1, maxDistance);
                auto timeleftfull = routeMatcher.GetTimeDistanceLeft();
                UNIT_ASSERT(timeleftfull.has_value());
                timeleft1 = timeleftfull->TimeDistance;
                TEST_DEBUG(timeleftfull->position_on_route.segmentIndex);
                UNIT_ASSERT_DOUBLES_EQUAL(timeleft1.Meters, 16958, 1.0);
                UNIT_ASSERT_DOUBLES_EQUAL(timeleft1.Seconds, 169, 1.0);
            }

            {
                // Same point as in first time but now we advance by route
                routeMatcher.Adjust(point0, maxDistance);
                auto timeleftfull = routeMatcher.GetTimeDistanceLeft();
                UNIT_ASSERT(timeleftfull.has_value());
                timeleft2 = timeleftfull->TimeDistance;
                TEST_DEBUG(timeleftfull->position_on_route.segmentIndex);
                UNIT_ASSERT_DOUBLES_EQUAL(timeleft2.Meters, 4898, 1.0);
                UNIT_ASSERT_DOUBLES_EQUAL(timeleft2.Seconds, 49, 1.0);
            }
        }

        routeMatcher.ResetRoute();
        UNIT_ASSERT(!routeMatcher.HasRoute());
    }

    Y_UNIT_TEST(TestMatcherWithRouteWithSamePointsAtTheEnd) {
        /// Test for case when we was adjusted to end of route
        using ::NTaxi::NRouteMatcher::DistancesByRoute;
        const auto poly = MakeTestPolylineWithRepeatedLastPoint(10, 0.1);
        UNIT_ASSERT_EQUAL(poly.PointsSize(), 10 + 1);
        UNIT_ASSERT_EQUAL(poly.SegmentsSize(), 9 + 1);
        const auto timeDistanceIndex = MakeTimeDistanceIndex(poly);

        const double routeTimeDuration = timeDistanceIndex.back().Seconds;
        const double routeLength = timeDistanceIndex.back().Meters;
        const double maxDistance = 1000;

        UNIT_ASSERT_DOUBLES_EQUAL(routeTimeDuration, 100.0, 1.0);
        UNIT_ASSERT_DOUBLES_EQUAL(routeLength, 10000.0, 1.0);

        NTaxi::NRouteMatcher::TRouteMatcher routeMatcher;
        UNIT_ASSERT(!routeMatcher.HasRoute());
        routeMatcher.SetRoute(poly, timeDistanceIndex, routeTimeDuration);
        UNIT_ASSERT(routeMatcher.HasRoute());

        {
            // Far point that should not be adjusted
            auto point = TPoint();
            point.Lat = 20;
            point.Lat = 40;
            routeMatcher.SetRoute(poly, timeDistanceIndex, routeTimeDuration);
            routeMatcher.Adjust(point, maxDistance);
            auto timeleftfull = routeMatcher.GetTimeDistanceLeft();
            UNIT_ASSERT(!timeleftfull.has_value());
        }

        routeMatcher.ResetRoute();
        UNIT_ASSERT(!routeMatcher.HasRoute());
    }

    Y_UNIT_TEST(TestMatcherFailToAdjustRouteWithNearStartKeyPoints_1) {
        using ::NTaxi::NRouteMatcher::DistancesByRoute;
        const auto poly = MakePolyForCaseWithKeyPointsNearBegin();
        const auto timeDistanceIndex = MakeTimeDistanceIndex(poly);

        const double routeTimeDuration = timeDistanceIndex.back().Seconds;
        const double maxDistance = 10000;

        /// driver position
        const auto point0 = TPoint{37.582856, 55.806307};
        /// destination points
        const auto key_points = TVector<TPoint>{
            {37.582681, 55.806271},
            //{55.806069, 37.581379}
        };

        NTaxi::NRouteMatcher::TRouteMatcher routeMatcher;
        routeMatcher.SetMaxAdjustCandidates(5);
        routeMatcher.SetRoute(poly, key_points, timeDistanceIndex, routeTimeDuration, maxDistance);
        UNIT_ASSERT(routeMatcher.HasRoute());

        {
            routeMatcher.Adjust(point0, maxDistance);
            auto timeleftfull = routeMatcher.GetTimeDistanceLeft();
            UNIT_ASSERT(timeleftfull.has_value());
            UNIT_ASSERT_EQUAL(timeleftfull->all_etas.size(), 1ull);
            for (const auto& eta: timeleftfull->all_etas) {
                UNIT_ASSERT_GE(eta.Seconds, 0);
                UNIT_ASSERT_GE(eta.Meters, 0);
            }
        }
    }

    Y_UNIT_TEST(TestMatcherFailToAdjustRouteWithNearStartKeyPoints_2) {
        using ::NTaxi::NRouteMatcher::DistancesByRoute;
        const auto poly = MakePoly({
            {37.58685, 55.733864},
            {37.58685, 55.733864},
            {37.586849, 55.733864}                                  
        });
        const auto timeDistanceIndex = MakeTimeDistanceIndex(poly);

        const double routeTimeDuration = timeDistanceIndex.back().Seconds;
        const double maxDistance = 10000;

        /// driver position
        const auto point0 = TPoint{37.58685, 55.733863};

        /// legs
        auto legs = TVector<NTaxi::NRouteMatcher::TLeg>();
        {
            NTaxi::NRouteMatcher::TLeg leg;
            leg.PositionOnEdge = 0;
            leg.SegmentIndex = 1;

            legs.push_back(leg);
        }

        NTaxi::NRouteMatcher::TRouteMatcher routeMatcher;
        routeMatcher.SetMaxAdjustCandidates(5);
        routeMatcher.SetRoute(poly, legs, timeDistanceIndex, routeTimeDuration);
        UNIT_ASSERT(routeMatcher.HasRoute());

        {
            routeMatcher.Adjust(point0, maxDistance);
            auto timeleftfull = routeMatcher.GetTimeDistanceLeft();
            UNIT_ASSERT(timeleftfull.has_value());
            UNIT_ASSERT_EQUAL(timeleftfull->all_etas.size(), 1ull);
            for (const auto& eta: timeleftfull->all_etas) {
                UNIT_ASSERT_GE(eta.Seconds, 0);
                UNIT_ASSERT_GE(eta.Meters, 0);
            }
        }
    }
}
