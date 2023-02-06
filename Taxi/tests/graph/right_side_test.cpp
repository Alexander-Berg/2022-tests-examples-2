#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <maps/libs/geolib/include/distance.h>
#include <taxi/graph/libs/graph/graph.h>
#include <taxi/graph/libs/graph/right_side_detector.h>
#include <taxi/graph/libs/graph-test/graph_test_data.h>

using TaxiGraph = NTaxi::NGraph2::TGraph;
using NTaxi::NGraph2::TEdgeAccess;
using NTaxi::NGraph2::TEdgeCategory;
using NTaxi::NGraph2::TPoint;
using NTaxi::NGraph2::TPolyline;
using NTaxi::NGraph2::TPositionOnEdge;
using NTaxi::NGraph2::TPositionOnGraph;
using NTaxi::NGraph2::TRightSideDetector;
using NTaxi::NGraph2::TRoadGraphDataStorage;

struct RightSideFixture: public ::NUnitTest::TBaseTestCase,
                          public NTaxi::NGraph2::TGraphTestData {
};

Y_UNIT_TEST_SUITE_F(right_side_detector, RightSideFixture) {
    Y_UNIT_TEST(meridian_aligned) {
        TPoint start{37, 55};
        TPoint end{37, 56};

        TPoint right_point{37.5, 55.5};
        TPoint left_point{36.5, 55.5};
        UNIT_ASSERT(TRightSideDetector{}.IsPointOnRightSide(start, end, right_point));
        UNIT_ASSERT(!(TRightSideDetector{}.IsPointOnRightSide(start, end, left_point)));
    }

    Y_UNIT_TEST(parallel_aligned) {
        TPoint start{36, 55};
        TPoint end{37, 55};

        TPoint top_point{36.5, 55.5};
        TPoint bottom_point{36.5, 54.5};
        UNIT_ASSERT(!(TRightSideDetector{}.IsPointOnRightSide(start, end, top_point)));
        UNIT_ASSERT(TRightSideDetector{}.IsPointOnRightSide(start, end, bottom_point));
    }

    Y_UNIT_TEST(precision) {
        {
            TPoint start{37.4759047, 55.7178388};
            TPoint end{37.476334, 55.718281};

            TPoint left_point{37.475904, 55.717966};
            TPoint right_point{37.476092, 55.717923};
            UNIT_ASSERT(
                TRightSideDetector{}.IsPointOnRightSide(start, end, right_point));
            UNIT_ASSERT(!(
                TRightSideDetector{}.IsPointOnRightSide(start, end, left_point)));
        }

        {
            // oposite edge direction
            TPoint end{37.4759047, 55.7178388};
            TPoint start{37.476334, 55.718281};

            TPoint left_point{37.475904, 55.717966};
            TPoint right_point{37.476092, 55.717923};
            UNIT_ASSERT(!(
                TRightSideDetector{}.IsPointOnRightSide(start, end, right_point)));
            UNIT_ASSERT(TRightSideDetector{}.IsPointOnRightSide(start, end, left_point));
        }
    }
}
