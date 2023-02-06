#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>
#include <taxi/graph/libs/graph/graph.h>
#include <taxi/graph/libs/graph/geolib3_helpers.h>

namespace {
#define TEST_DEBUG(x) \
    { Cerr << #x << ": " << x << "\n"; }

using NTaxi::NGraph2::TPoint;
using NTaxi::NGraph2::TPolyline;

TPolyline MakePolyline(TPoint p0, TPoint p1) {
    TPolyline ret;
    ret.AddPoint(p0);
    ret.AddPoint(p1);
    return ret;
}
}

Y_UNIT_TEST_SUITE(segment_direction_test) {
    Y_UNIT_TEST(TestBase) {
        {
            // North
            const auto poly = MakePolyline({37, 55}, {37, 56});
            const auto dir = NTaxi::NUtils::SegmentDirection(poly.AsGeolibPolyline(), 0);
            TEST_DEBUG(dir);
            UNIT_ASSERT_DOUBLES_EQUAL(dir, 0, 1.0);
        }

        {
            // South
            const auto poly = MakePolyline({37, 56}, {37, 55});
            const auto dir = NTaxi::NUtils::SegmentDirection(poly.AsGeolibPolyline(), 0);
            TEST_DEBUG(dir);
            UNIT_ASSERT_DOUBLES_EQUAL(dir, 180, 1.0);
        }
        {
            // East
            const auto poly = MakePolyline({37, 55}, {38, 55});
            const auto dir = NTaxi::NUtils::SegmentDirection(poly.AsGeolibPolyline(), 0);
            TEST_DEBUG(dir);
            UNIT_ASSERT_DOUBLES_EQUAL(dir, 90, 1.0);
        }
        {
            // West
            const auto poly = MakePolyline({38, 55}, {37, 55});
            const auto dir = NTaxi::NUtils::SegmentDirection(poly.AsGeolibPolyline(), 0);
            TEST_DEBUG(dir);
            UNIT_ASSERT_DOUBLES_EQUAL(dir, 270, 1.0);
        }
    }
}
