#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <yandex/taxi/graph2/route_matcher/route_matcher.h>
#include <yandex/taxi/graph2/container.h>
#include <taxi/graph/libs/graph/point.h>
#include <taxi/graph/external/graph2/lib/conversion.h>

using NTaxiExternal::NGraph2::TPoint;
using NTaxiExternal::NGraph2::TPolyline;
using NTaxiExternal::NGraph2::TRouteMatcher;
using TTimeDistanceIndex = NTaxiExternal::NGraph2::TRouteMatcher::TTimeDistanceIndex;
using NTaxiExternal::NGraph2::ToInternal;
using NTaxiExternal::NGraph2::TTimeDistance;

#define TEST_DEBUG(x) \
    { Cerr << #x << ": " << x << "\n"; }

namespace {
    TPolyline MakeTestPolyline(size_t maxPoints = 100, bool parallel_align = true, double step = 0.001) {
        TPolyline ret;
        ret.ReservePoints(maxPoints);

        static const TPoint point(37, 55);
        for (size_t i = 0; i < maxPoints; ++i) {
            auto p = point;
            p.Lat += i * step;
            if (!parallel_align) {
                p.Lon += i * step;
            }
            ret.AddPoint(p);
        }

        return ret;
    }
    ::NTaxiExternal::NGraph2::TContainer<NTaxiExternal::NGraph2::TRouteMatcher::TLeg> MakeLegs(size_t legs_count) {
        /// for first key point
        ::NTaxiExternal::NGraph2::TContainer<NTaxiExternal::NGraph2::TRouteMatcher::TLeg> ret;
        for (size_t i = 0; i < legs_count; ++i) {
            NTaxiExternal::NGraph2::TRouteMatcher::TLeg leg;
            leg.PositionOnEdge = 0;
            leg.SegmentIndex = i * 10;
            ret.PushBack(leg);
        }
        return ret;
    }

    /// Make line that returns to initial point and go further like this:
    //           A ------|--|-->-|---|->--|--|---|---|-\
    //    Driver                                        | B
    //  C---<----|--|---<---|------|---<--|------|---|-/
    //
    TPolyline MakeTestOverlappingReturningPolyline(double step = 0.001,
            size_t forward_points=5, size_t backward_points=8) {
        static const TPoint point(37, 55);
        TPolyline ret;
        for (size_t i = 0; i < forward_points; ++i) {
            auto p = point;
            p.Lat += i * step;
            ret.AddPoint(p);
        }
        for (size_t i = 0; i < backward_points; ++i) {
            auto p = ret.PointAt(ret.PointsSize() - 1);
            p.Lat -= step;
            ret.AddPoint(p);
        }

        return ret;
    }

    TRouteMatcher::TKeyPoints MakeKeyPoints(TPolyline poly) {
        TRouteMatcher::TKeyPoints ret;
        ret.Reserve(poly.PointsSize());
        for (size_t i = 0; i < poly.PointsSize(); ++i) {
            ret.PushBack(poly.PointAt(i));
        }
        return ret;
    }
}

Y_UNIT_TEST_SUITE(external_route_matcher_test) {
    TTimeDistanceIndex MakeTimeDistanceIndex(const TPolyline& poly) {
        TTimeDistanceIndex ret;
        const size_t pointsCount = poly.PointsSize();
        const size_t distanceUnit = 1000;
        const size_t timeUnit = 10;
        ret.Reserve(pointsCount);

        for (size_t i = 0; i < pointsCount; ++i) {
            TTimeDistance timeDistance;
            timeDistance.Distance = i * distanceUnit;
            timeDistance.Time = i * timeUnit;
            ret.PushBack(timeDistance);
        }

        return ret;
    }

    Y_UNIT_TEST(TestMatcherWithTimeDistances) {
        const auto poly = MakeTestPolyline(11);
        UNIT_ASSERT_EQUAL(poly.PointsSize(), 11);
        UNIT_ASSERT_EQUAL(poly.SegmentsSize(), 10);
        const auto timeDistanceIndex = MakeTimeDistanceIndex(poly);

        const auto& back = timeDistanceIndex[timeDistanceIndex.Size() - 1];
        const double routeTimeDuration = back.Time;
        const double routeLength = back.Distance;
        const double maxDistance = 1000;

        UNIT_ASSERT_DOUBLES_EQUAL(routeTimeDuration, 100.0, 1.0);
        UNIT_ASSERT_DOUBLES_EQUAL(routeLength, 10000.0, 1.0);

        TRouteMatcher routeMatcher;
        UNIT_ASSERT(!routeMatcher.HasRoute());
        routeMatcher.SetRoute(poly, timeDistanceIndex, routeTimeDuration);
        UNIT_ASSERT(routeMatcher.HasRoute());

        {
            // Test first point at start of polyline
            const auto& point = poly.PointAt(0);
            auto timeleft = routeMatcher.GetTimeDistanceLeft(point, maxDistance);
            auto full = routeMatcher.GetRouteAdjustInfo(point, maxDistance);
            UNIT_ASSERT(timeleft.isInitialized);
            UNIT_ASSERT(full.isInitialized);
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.value.Distance, routeLength, 1.0);
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.value.Time, routeTimeDuration, 1.0);

            UNIT_ASSERT_EQUAL(full.value.TimeDistance, timeleft.value);
            UNIT_ASSERT_EQUAL(full.value.SegmentIndex, 0);
            UNIT_ASSERT_EQUAL(full.value.Distance, 0);
            UNIT_ASSERT_DOUBLES_EQUAL(full.value.Direction, 0, 0.5);

            const ::NTaxi::NGraph2::TPoint expected = ToInternal(point);
            UNIT_ASSERT(NTaxi::NGraph2::TPoint::IsSamePoint(ToInternal(full.value.Point), expected));
        }
        {
            // Test last point at end of polyline
            const auto& point = poly.PointAt(poly.PointsSize() - 1);
            routeMatcher.SetRoute(poly, timeDistanceIndex, routeTimeDuration);
            auto timeleft = routeMatcher.GetTimeDistanceLeft(point, maxDistance);
            auto full = routeMatcher.GetRouteAdjustInfo(point, maxDistance);
            UNIT_ASSERT(timeleft.isInitialized);
            UNIT_ASSERT(full.isInitialized);
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.value.Distance, 0, 1.0);
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.value.Time, 0.0, 1.0);

            UNIT_ASSERT_EQUAL(full.value.TimeDistance, timeleft.value);
            UNIT_ASSERT_EQUAL(full.value.SegmentIndex, poly.SegmentsSize() - 1);
            UNIT_ASSERT_EQUAL(full.value.Distance, 0);
            UNIT_ASSERT_DOUBLES_EQUAL(full.value.Direction, 0, 0.5);

            const ::NTaxi::NGraph2::TPoint expected = ToInternal(point);
            UNIT_ASSERT(NTaxi::NGraph2::TPoint::IsSamePoint(ToInternal(full.value.Point), expected));
        }
        {
            // Test point at midle of polyline
            const auto& point = poly.PointAt(poly.PointsSize() / 2);
            const auto& segmentIndex = (poly.SegmentsSize() - 1) / 2;
            routeMatcher.SetRoute(poly, timeDistanceIndex, routeTimeDuration);
            auto timeleft = routeMatcher.GetTimeDistanceLeft(point, maxDistance);
            auto full = routeMatcher.GetRouteAdjustInfo(point, maxDistance);
            UNIT_ASSERT(timeleft.isInitialized);
            UNIT_ASSERT(full.isInitialized);
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.value.Distance, routeLength / 2, 5.0);
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.value.Time, routeTimeDuration / 2, 1.0);

            UNIT_ASSERT_EQUAL(full.value.TimeDistance, timeleft.value);
            UNIT_ASSERT_EQUAL(full.value.SegmentIndex, segmentIndex);
            UNIT_ASSERT_EQUAL(full.value.Distance, 0);
            UNIT_ASSERT_DOUBLES_EQUAL(full.value.Direction, 0, 0.5);

            const ::NTaxi::NGraph2::TPoint expected = ToInternal(point);
            UNIT_ASSERT(NTaxi::NGraph2::TPoint::IsSamePoint(ToInternal(full.value.Point), expected));
        }
        {
            // Test point to far from route
            const auto& point = TPoint(50, 50);
            routeMatcher.SetRoute(poly, timeDistanceIndex, routeTimeDuration);
            auto timeleft = routeMatcher.GetTimeDistanceLeft(point, maxDistance);
            auto full = routeMatcher.GetRouteAdjustInfo(point, maxDistance);
            UNIT_ASSERT(!timeleft.isInitialized);
            UNIT_ASSERT(!full.isInitialized);
        }

        {
            // Test displaced last point at end of polyline (test Distance to
            // original point)
            const auto& point = poly.PointAt(poly.PointsSize() - 1);
            auto displased_point = point;
            displased_point.Lon += 0.00001;

            routeMatcher.SetRoute(poly, timeDistanceIndex, routeTimeDuration);
            auto timeleft = routeMatcher.GetTimeDistanceLeft(displased_point, maxDistance);
            auto full = routeMatcher.GetRouteAdjustInfo(displased_point, maxDistance);
            UNIT_ASSERT(timeleft.isInitialized);
            UNIT_ASSERT(full.isInitialized);
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.value.Distance, 0, 1.0);
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.value.Time, 0.0, 1.0);

            UNIT_ASSERT_EQUAL(full.value.TimeDistance, timeleft.value);
            UNIT_ASSERT_EQUAL(full.value.SegmentIndex, poly.SegmentsSize() - 1);
            UNIT_ASSERT_DOUBLES_EQUAL(full.value.Distance, 0.63834, 0.0005);
            UNIT_ASSERT_DOUBLES_EQUAL(full.value.Direction, 0, 0.5);

            const ::NTaxi::NGraph2::TPoint expected = ToInternal(point);
            UNIT_ASSERT(NTaxi::NGraph2::TPoint::IsSamePoint(ToInternal(full.value.Point), expected));
        }

        routeMatcher.ResetRoute();
        UNIT_ASSERT(!routeMatcher.HasRoute());
    }

    Y_UNIT_TEST(TestIntermediatePoints) {
        auto poly = MakeTestPolyline(101);
        const auto key_points_count = 11;
        auto key_points = MakeKeyPoints(MakeTestPolyline(key_points_count, true, 0.01));
        UNIT_ASSERT_EQUAL(key_points.size(), key_points_count);

        const auto timeDistanceIndex = MakeTimeDistanceIndex(poly);
        const auto& timeDistanceIndexBack = timeDistanceIndex[timeDistanceIndex.size() - 1];
        const double routeTimeDuration = timeDistanceIndexBack.Time;
        const double routeLength = timeDistanceIndexBack.Distance;
        const double maxDistance = 1000;

        UNIT_ASSERT_DOUBLES_EQUAL(routeTimeDuration, 1000.0, 1.0);
        UNIT_ASSERT_DOUBLES_EQUAL(routeLength, 100000.0, 1.0);

        TRouteMatcher routeMatcher;
        UNIT_ASSERT(!routeMatcher.HasRoute());
        UNIT_ASSERT(routeMatcher.SetRoute(poly, key_points, timeDistanceIndex, routeTimeDuration, 100));
        UNIT_ASSERT(routeMatcher.HasRoute());

        {
            // Test first point at start of polyline
            const auto& point = poly.PointAt(0);
            UNIT_ASSERT(routeMatcher.SetRoute(poly, key_points, timeDistanceIndex, routeTimeDuration, 100));
            auto full = routeMatcher.GetRouteAdjustInfo(point, maxDistance);
            UNIT_ASSERT(full.isInitialized);
            const auto& etas = full.value.etas;
            UNIT_ASSERT_EQUAL(key_points_count, etas.size());

            const auto expected_times = TVector<double>{0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000};
            for (size_t i = 0; i < key_points_count; ++i) {
                UNIT_ASSERT_DOUBLES_EQUAL(etas[i].Time, expected_times[i], 1.0);
            }

            const auto expected_distances = TVector<double>{0, 10000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000};
            for (size_t i = 0; i < key_points_count; ++i) {
                UNIT_ASSERT_DOUBLES_EQUAL(etas[i].Distance, expected_distances[i], 1.0);
            }
        }
        {
            // Test point to far from route
            const auto& point = TPoint(50, 50);
            UNIT_ASSERT(routeMatcher.SetRoute(poly, key_points, timeDistanceIndex, routeTimeDuration, 100));
            auto timeleft = routeMatcher.GetRouteAdjustInfo(point, maxDistance);
            UNIT_ASSERT(timeleft.isInitialized == false);
        }

        routeMatcher.ResetRoute();
        UNIT_ASSERT(!routeMatcher.HasRoute());
    }

    Y_UNIT_TEST(TestMatcherWithTimeDistancesNoParallelAligned) {
        /// Test direction not alwais zero
        const auto poly = MakeTestPolyline(11, false);
        UNIT_ASSERT_EQUAL(poly.PointsSize(), 11);
        UNIT_ASSERT_EQUAL(poly.SegmentsSize(), 10);
        const auto timeDistanceIndex = MakeTimeDistanceIndex(poly);

        const auto& back = timeDistanceIndex[timeDistanceIndex.Size() - 1];
        const double routeTimeDuration = back.Time;
        const double routeLength = back.Distance;
        const double maxDistance = 1000;

        UNIT_ASSERT_DOUBLES_EQUAL(routeTimeDuration, 100.0, 1.0);
        UNIT_ASSERT_DOUBLES_EQUAL(routeLength, 10000.0, 1.0);

        TRouteMatcher routeMatcher;
        UNIT_ASSERT(!routeMatcher.HasRoute());
        routeMatcher.SetRoute(poly, timeDistanceIndex, routeTimeDuration);
        UNIT_ASSERT(routeMatcher.HasRoute());

        {
            // Test first point at start of polyline
            const auto& point = poly.PointAt(0);
            auto timeleft = routeMatcher.GetTimeDistanceLeft(point, maxDistance);
            auto full = routeMatcher.GetRouteAdjustInfo(point, maxDistance);
            UNIT_ASSERT(timeleft.isInitialized);
            UNIT_ASSERT(full.isInitialized);
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.value.Distance, routeLength, 1.0);
            UNIT_ASSERT_DOUBLES_EQUAL(timeleft.value.Time, routeTimeDuration, 1.0);

            UNIT_ASSERT_EQUAL(full.value.TimeDistance, timeleft.value);
            UNIT_ASSERT_EQUAL(full.value.SegmentIndex, 0);
            UNIT_ASSERT_EQUAL(full.value.Distance, 0);
            UNIT_ASSERT_DOUBLES_EQUAL(full.value.Direction, 30, 0.5);

            const ::NTaxi::NGraph2::TPoint expected = ToInternal(point);
            UNIT_ASSERT(NTaxi::NGraph2::TPoint::IsSamePoint(ToInternal(full.value.Point), expected));
        }
        routeMatcher.ResetRoute();
        UNIT_ASSERT(!routeMatcher.HasRoute());
    }

    Y_UNIT_TEST(TestReturningRoute) {
        auto poly = MakeTestOverlappingReturningPolyline();
        TPolyline keyPointsPoly;
        keyPointsPoly.AddPoint(poly.PointAt(4));
        keyPointsPoly.AddPoint(poly.PointAt(12));
        const auto key_points_count = keyPointsPoly.PointsSize();
        const auto key_points = MakeKeyPoints(keyPointsPoly);

        const auto timeDistanceIndex = MakeTimeDistanceIndex(poly);
        const auto& timeDistanceIndexBack = timeDistanceIndex[timeDistanceIndex.size() - 1];
        const double routeTimeDuration = timeDistanceIndexBack.Time;
        const double routeLength = timeDistanceIndexBack.Distance;
        const double maxDistance = 1000;

        UNIT_ASSERT_DOUBLES_EQUAL(routeTimeDuration, 120.0, 1.0);
        UNIT_ASSERT_DOUBLES_EQUAL(routeLength, 12000.0, 1.0);

        TRouteMatcher routeMatcher;
        routeMatcher.SetMaxAdjustCandidates(5);
        UNIT_ASSERT(!routeMatcher.HasRoute());
        UNIT_ASSERT(routeMatcher.SetRoute(poly, key_points, timeDistanceIndex, routeTimeDuration, 100));
        UNIT_ASSERT(routeMatcher.HasRoute());

        {
            // Test first point at start of polyline
            const auto& point = poly.PointAt(0);
            UNIT_ASSERT(routeMatcher.SetRoute(poly, key_points, timeDistanceIndex, routeTimeDuration, 100));
            auto full = routeMatcher.GetRouteAdjustInfo(point, maxDistance);
            UNIT_ASSERT(full.isInitialized);
            const auto& etas = full.value.etas;
            UNIT_ASSERT_EQUAL(key_points_count, etas.size());

            const auto expected_times = TVector<double>{40, 120};
            for (size_t i = 0; i < key_points_count; ++i) {
                UNIT_ASSERT_DOUBLES_EQUAL(etas[i].Time, expected_times[i], 1.0);
            }

            const auto expected_distances = TVector<double>{4000, 12000};
            for (size_t i = 0; i < key_points_count; ++i) {
                UNIT_ASSERT_DOUBLES_EQUAL(etas[i].Distance, expected_distances[i], 1.0);
            }
        }
        {
            // Test first point at end of polyline
            // In this test we expect that first we must adjust to start of
            // route.
            const auto& point = poly.PointAt(12);
            UNIT_ASSERT(routeMatcher.SetRoute(poly, key_points, timeDistanceIndex, routeTimeDuration, 100));
            auto full = routeMatcher.GetRouteAdjustInfo(point, maxDistance);
            UNIT_ASSERT(full.isInitialized);
            const auto& etas = full.value.etas;
            UNIT_ASSERT_EQUAL(key_points_count, etas.size());

            const auto expected_times = TVector<double>{40, 120};
            for (size_t i = 0; i < key_points_count; ++i) {
                UNIT_ASSERT_DOUBLES_EQUAL(etas[i].Time, expected_times[i], 1.0);
            }

            const auto expected_distances = TVector<double>{4000, 12000};
            for (size_t i = 0; i < key_points_count; ++i) {
                UNIT_ASSERT_DOUBLES_EQUAL(etas[i].Distance, expected_distances[i], 1.0);
            }
        }

        {
            // Test driver moves along route
            const auto& point = poly.PointAt(1);
            UNIT_ASSERT(routeMatcher.SetRoute(poly, key_points, timeDistanceIndex, routeTimeDuration, 100));
            auto full = routeMatcher.GetRouteAdjustInfo(point, maxDistance);
            UNIT_ASSERT(full.isInitialized);
            const auto& etas = full.value.etas;
            UNIT_ASSERT_EQUAL(key_points_count, etas.size());

            const auto expected_times = TVector<double>{30.0, 110.0};
            for (size_t i = 0; i < key_points_count; ++i) {
                UNIT_ASSERT_DOUBLES_EQUAL(etas[i].Time, expected_times[i], 1.0);
            }

            const auto expected_distances = TVector<double>{3000.0, 11000.0};
            for (size_t i = 0; i < key_points_count; ++i) {
                UNIT_ASSERT_DOUBLES_EQUAL(etas[i].Distance, expected_distances[i], 1.0);
            }
        }

        routeMatcher.ResetRoute();
        UNIT_ASSERT(!routeMatcher.HasRoute());
    }

    Y_UNIT_TEST(TestIntermediatePointsWithLegs) {
        auto poly = MakeTestPolyline(101, true, 0.001);
        const auto legs_count = 10;
        auto legs = MakeLegs(legs_count);

        const auto timeDistanceIndex = MakeTimeDistanceIndex(poly);
        const auto& timeDistanceIndexBack = timeDistanceIndex[timeDistanceIndex.size() - 1];
        const double routeTimeDuration = timeDistanceIndexBack.Time;
        const double routeLength = timeDistanceIndexBack.Distance;
        const double maxDistance = 1000;

        UNIT_ASSERT_DOUBLES_EQUAL(routeTimeDuration, 1000.0, 1.0);
        UNIT_ASSERT_DOUBLES_EQUAL(routeLength, 100000.0, 1.0);

        TRouteMatcher routeMatcher;
        UNIT_ASSERT(!routeMatcher.HasRoute());
        UNIT_ASSERT(routeMatcher.SetRoute(poly, legs, timeDistanceIndex, routeTimeDuration));
        UNIT_ASSERT(routeMatcher.HasRoute());

        {
            // Test first point at start of polyline
            const auto& point = poly.PointAt(0);
            UNIT_ASSERT(routeMatcher.SetRoute(poly, legs, timeDistanceIndex, routeTimeDuration));
            auto full = routeMatcher.GetRouteAdjustInfo(point, maxDistance);
            UNIT_ASSERT(full.isInitialized);
            const auto& etas = full.value.etas;
            UNIT_ASSERT_EQUAL(legs.size(), etas.size());

            const auto expected_times = TVector<double>{0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000};
            for (size_t i = 0; i < legs_count; ++i) {
                UNIT_ASSERT_DOUBLES_EQUAL(etas[i].Time, expected_times[i], 1.0);
            }

            const auto expected_distances = TVector<double>{0, 10000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000};
            for (size_t i = 0; i < legs_count; ++i) {
                UNIT_ASSERT_DOUBLES_EQUAL(etas[i].Distance, expected_distances[i], 1.0);
            }
        }

        routeMatcher.ResetRoute();
        UNIT_ASSERT(!routeMatcher.HasRoute());
    }

    Y_UNIT_TEST(TestIntermediatePointsWithNoLegs) {
        auto poly = MakeTestPolyline(101, true, 0.001);
        const auto legs_count = 0;
        auto legs = MakeLegs(legs_count);

        const auto timeDistanceIndex = MakeTimeDistanceIndex(poly);
        const auto& timeDistanceIndexBack = timeDistanceIndex[timeDistanceIndex.size() - 1];
        const double routeTimeDuration = timeDistanceIndexBack.Time;
        const double routeLength = timeDistanceIndexBack.Distance;
        const double maxDistance = 1000;

        UNIT_ASSERT_DOUBLES_EQUAL(routeTimeDuration, 1000.0, 1.0);
        UNIT_ASSERT_DOUBLES_EQUAL(routeLength, 100000.0, 1.0);

        TRouteMatcher routeMatcher;
        UNIT_ASSERT(!routeMatcher.HasRoute());
        UNIT_ASSERT(routeMatcher.SetRoute(poly, legs, timeDistanceIndex, routeTimeDuration));
        UNIT_ASSERT(routeMatcher.HasRoute());

        {
            // Test first point at start of polyline
            const auto& point = poly.PointAt(0);
            UNIT_ASSERT(routeMatcher.SetRoute(poly, legs, timeDistanceIndex, routeTimeDuration));
            auto full = routeMatcher.GetRouteAdjustInfo(point, maxDistance);
            UNIT_ASSERT(full.isInitialized);
            const auto& etas = full.value.etas;
            UNIT_ASSERT_EQUAL(legs.size(), etas.size());
            UNIT_ASSERT(etas.Empty());

            UNIT_ASSERT_DOUBLES_EQUAL(routeTimeDuration, full.value.TimeDistance.Time, 1.0);
            UNIT_ASSERT_DOUBLES_EQUAL(routeLength, full.value.TimeDistance.Distance, 1.0);
        }

        routeMatcher.ResetRoute();
        UNIT_ASSERT(!routeMatcher.HasRoute());
    }

    Y_UNIT_TEST(TestIntermediatePointsWithLegs1pRoute) {
        auto poly = MakeTestPolyline(1, true, 0.001);
        const auto legs_count = 1;
        auto legs = MakeLegs(legs_count);

        const auto timeDistanceIndex = MakeTimeDistanceIndex(poly);
        const auto& timeDistanceIndexBack = timeDistanceIndex[timeDistanceIndex.size() - 1];
        const double routeTimeDuration = timeDistanceIndexBack.Time;
        const double routeLength = timeDistanceIndexBack.Distance;
        const double maxDistance = 1000;

        UNIT_ASSERT_DOUBLES_EQUAL(routeTimeDuration, 0.0, 1.0);
        UNIT_ASSERT_DOUBLES_EQUAL(routeLength, 0.0, 1.0);

        TRouteMatcher routeMatcher;
        UNIT_ASSERT(!routeMatcher.HasRoute());
        UNIT_ASSERT(routeMatcher.SetRoute(poly, legs, timeDistanceIndex, routeTimeDuration));
        UNIT_ASSERT(routeMatcher.HasRoute());

        {
            // Test first point at start of polyline
            const auto& point = poly.PointAt(0);
            UNIT_ASSERT(routeMatcher.SetRoute(poly, legs, timeDistanceIndex, routeTimeDuration));
            auto full = routeMatcher.GetRouteAdjustInfo(point, maxDistance);
            UNIT_ASSERT(full.isInitialized);
            const auto& etas = full.value.etas;
            UNIT_ASSERT_EQUAL(legs.size(), etas.size());

            UNIT_ASSERT_DOUBLES_EQUAL(etas[0].Time, 0, 1.0);
            UNIT_ASSERT_DOUBLES_EQUAL(etas[0].Distance, 0, 1.0);
            UNIT_ASSERT_DOUBLES_EQUAL(full.value.TimeDistance.Time, 0, 1.0);
            UNIT_ASSERT_DOUBLES_EQUAL(full.value.TimeDistance.Distance, 0, 1.0);
        }

        routeMatcher.ResetRoute();
        UNIT_ASSERT(!routeMatcher.HasRoute());
    }
}
