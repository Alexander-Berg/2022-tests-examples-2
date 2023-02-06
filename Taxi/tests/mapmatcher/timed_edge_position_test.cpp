#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <yandex/taxi/graph2/mapmatcher/timed_edge_position.h>
#include <yandex/taxi/graph2/container.h>

using NTaxiExternal::NGraph2::TContainer;
using NTaxiExternal::NGraph2::TPositionOnEdge;
using NTaxiExternal::NGraph2::TTimestamp;
using NTaxiExternal::NGraph2::UNDEFINED;
using NTaxiExternal::NMapMatcher2::TTimedPositionOnEdge;

static constexpr TTimestamp SOME_TIMESTAMP = 100;

Y_UNIT_TEST_SUITE(TimedPositionOnEdge) {
    Y_UNIT_TEST(Default) {
        TPositionOnEdge pos;
        TTimedPositionOnEdge timedPos{pos, SOME_TIMESTAMP};
        UNIT_ASSERT_EQUAL(pos.EdgeId, UNDEFINED);
        UNIT_ASSERT_EQUAL(timedPos.PositionOnEdge.EdgeId, UNDEFINED);
        UNIT_ASSERT_EQUAL(timedPos.Timestamp, SOME_TIMESTAMP);
    }

    Y_UNIT_TEST(BaseCtor) {
        TPositionOnEdge pos{10, 10.};
        TTimedPositionOnEdge timedPos{pos, SOME_TIMESTAMP};
        UNIT_ASSERT_EQUAL(timedPos.PositionOnEdge.EdgeId, 10);
        UNIT_ASSERT_EQUAL(timedPos.PositionOnEdge.Position, 10.);
        UNIT_ASSERT_EQUAL(timedPos.Timestamp, SOME_TIMESTAMP);
    }

    Y_UNIT_TEST(MoveCtor) {
        TPositionOnEdge pos{10, 10.};
        TTimedPositionOnEdge timedPos{pos, SOME_TIMESTAMP};
        TTimedPositionOnEdge newTimedPos{std::move(timedPos)};
        UNIT_ASSERT_EQUAL(newTimedPos.PositionOnEdge.EdgeId, 10);
        UNIT_ASSERT_EQUAL(newTimedPos.PositionOnEdge.Position, 10.);
        UNIT_ASSERT_EQUAL(newTimedPos.Timestamp, SOME_TIMESTAMP);
    }

    Y_UNIT_TEST(Move) {
        TPositionOnEdge pos{10, 10.};
        TTimedPositionOnEdge timedPos{pos, SOME_TIMESTAMP};
        TTimedPositionOnEdge newTimedPos;
        UNIT_ASSERT_EQUAL(newTimedPos.PositionOnEdge.EdgeId, UNDEFINED);
        newTimedPos = std::move(timedPos);
        UNIT_ASSERT_EQUAL(newTimedPos.PositionOnEdge.Position, 10.);
        UNIT_ASSERT_EQUAL(newTimedPos.Timestamp, SOME_TIMESTAMP);
    }

    Y_UNIT_TEST(CopyCtor) {
        TPositionOnEdge pos{10, 10.};
        TTimedPositionOnEdge timedPos{pos, SOME_TIMESTAMP};
        TTimedPositionOnEdge newTimedPos{timedPos};

        UNIT_ASSERT_EQUAL(newTimedPos.PositionOnEdge.EdgeId, 10);
        UNIT_ASSERT_EQUAL(newTimedPos.PositionOnEdge.Position, 10.);
        UNIT_ASSERT_EQUAL(newTimedPos.Timestamp, SOME_TIMESTAMP);
    }

    Y_UNIT_TEST(Copy) {
        TPositionOnEdge pos{10, 10.};
        TTimedPositionOnEdge timedPos{pos, SOME_TIMESTAMP};
        TTimedPositionOnEdge newTimedPos;

        UNIT_ASSERT_EQUAL(newTimedPos.PositionOnEdge.EdgeId, UNDEFINED);

        newTimedPos = timedPos;
        UNIT_ASSERT_EQUAL(newTimedPos.PositionOnEdge.EdgeId, 10);
        UNIT_ASSERT_EQUAL(newTimedPos.PositionOnEdge.Position, 10.);
        UNIT_ASSERT_EQUAL(newTimedPos.Timestamp, SOME_TIMESTAMP);
    }
}
