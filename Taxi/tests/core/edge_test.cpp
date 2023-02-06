#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <yandex/taxi/graph2/edge.h>
#include <yandex/taxi/graph2/container.h>

using NTaxiExternal::NGraph2::TContainer;
using NTaxiExternal::NGraph2::TPositionOnEdge;
using NTaxiExternal::NGraph2::TPositionOnGraph;
using NTaxiExternal::NGraph2::UNDEFINED;

Y_UNIT_TEST_SUITE(PositionOnGraph) {
    Y_UNIT_TEST(Default) {
        TPositionOnGraph pos;
        UNIT_ASSERT_EQUAL(pos.EdgeId, UNDEFINED);
        UNIT_ASSERT_EQUAL(pos.SegmentIndex, 0u);
        UNIT_ASSERT_DOUBLES_EQUAL(pos.Position, 0., 1e-2);
    }

    Y_UNIT_TEST(BaseCtor) {
        TPositionOnGraph pos{10, 3, 10.};
        UNIT_ASSERT_EQUAL(pos.EdgeId, 10);
        UNIT_ASSERT_EQUAL(pos.SegmentIndex, 3u);
        UNIT_ASSERT_DOUBLES_EQUAL(pos.Position, 10., 1e-2);
    }

    Y_UNIT_TEST(Setters) {
        TPositionOnGraph pos;
        pos.EdgeId = 10;
        pos.SegmentIndex = 3;
        pos.Position = 10.;
        UNIT_ASSERT_EQUAL(pos.EdgeId, 10);
        UNIT_ASSERT_EQUAL(pos.SegmentIndex, 3u);
        UNIT_ASSERT_DOUBLES_EQUAL(pos.Position, 10., 1e-2);
    }

    Y_UNIT_TEST(MoveCtor) {
        TPositionOnGraph pos{10, 3, 10.};
        TPositionOnGraph newPos{std::move(pos)};
        UNIT_ASSERT_EQUAL(newPos.EdgeId, 10);
        UNIT_ASSERT_EQUAL(newPos.SegmentIndex, 3u);
        UNIT_ASSERT_DOUBLES_EQUAL(newPos.Position, 10., 1e-2);
    }

    Y_UNIT_TEST(Move) {
        TPositionOnGraph pos{10, 3, 10.};
        TPositionOnGraph newPos;
        UNIT_ASSERT_EQUAL(newPos.EdgeId, UNDEFINED);
        newPos = std::move(pos);
        UNIT_ASSERT_EQUAL(newPos.EdgeId, 10);
        UNIT_ASSERT_EQUAL(newPos.SegmentIndex, 3u);
        UNIT_ASSERT_DOUBLES_EQUAL(newPos.Position, 10., 1e-2);
    }

    Y_UNIT_TEST(CopyCtor) {
        TPositionOnGraph pos{10, 3, 10.};
        TPositionOnGraph newPos{pos};
        UNIT_ASSERT_EQUAL(newPos.EdgeId, pos.EdgeId);
        UNIT_ASSERT_EQUAL(newPos.SegmentIndex, pos.SegmentIndex);
        UNIT_ASSERT_DOUBLES_EQUAL(newPos.Position, pos.Position, 1e-2);
    }

    Y_UNIT_TEST(Copy) {
        TPositionOnGraph pos{10, 3, 10.};
        TPositionOnGraph newPos;
        UNIT_ASSERT_EQUAL(newPos.EdgeId, UNDEFINED);
        newPos = pos;
        UNIT_ASSERT_EQUAL(newPos.EdgeId, pos.EdgeId);
        UNIT_ASSERT_EQUAL(newPos.SegmentIndex, pos.SegmentIndex);
        UNIT_ASSERT_DOUBLES_EQUAL(newPos.Position, pos.Position, 1e-2);
    }
}

Y_UNIT_TEST_SUITE(PositionOnEdge) {
    Y_UNIT_TEST(Default) {
        TPositionOnEdge pos;
        UNIT_ASSERT_EQUAL(pos.EdgeId, UNDEFINED);
        UNIT_ASSERT_DOUBLES_EQUAL(pos.Position, 0., 1e-2);
    }

    Y_UNIT_TEST(BaseCtor) {
        TPositionOnEdge pos{10, 10.};
        UNIT_ASSERT_EQUAL(pos.EdgeId, 10);
        UNIT_ASSERT_DOUBLES_EQUAL(pos.Position, 10., 1e-2);
    }

    Y_UNIT_TEST(Setters) {
        TPositionOnEdge pos;
        pos.EdgeId = 10;
        pos.Position = 10.;
        UNIT_ASSERT_EQUAL(pos.EdgeId, 10);
        UNIT_ASSERT_DOUBLES_EQUAL(pos.Position, 10., 1e-2);
    }

    Y_UNIT_TEST(MoveCtor) {
        TPositionOnEdge pos{10, 10.};
        TPositionOnEdge newPos{std::move(pos)};
        UNIT_ASSERT_EQUAL(newPos.EdgeId, 10);
        UNIT_ASSERT_DOUBLES_EQUAL(newPos.Position, 10., 1e-2);
    }

    Y_UNIT_TEST(Move) {
        TPositionOnEdge pos{10, 10.};
        TPositionOnEdge newPos;
        UNIT_ASSERT_EQUAL(newPos.EdgeId, UNDEFINED);
        newPos = std::move(pos);
        UNIT_ASSERT_EQUAL(newPos.EdgeId, 10);
        UNIT_ASSERT_DOUBLES_EQUAL(newPos.Position, 10., 1e-2);
    }

    Y_UNIT_TEST(CopyCtor) {
        TPositionOnEdge pos{10, 10.};
        TPositionOnEdge newPos{pos};
        UNIT_ASSERT_EQUAL(newPos.EdgeId, pos.EdgeId);
        UNIT_ASSERT_DOUBLES_EQUAL(newPos.Position, pos.Position, 1e-2);
    }

    Y_UNIT_TEST(Copy) {
        TPositionOnEdge pos{10, 10.};
        TPositionOnEdge newPos;
        UNIT_ASSERT_EQUAL(newPos.EdgeId, UNDEFINED);
        newPos = pos;
        UNIT_ASSERT_EQUAL(newPos.EdgeId, pos.EdgeId);
        UNIT_ASSERT_DOUBLES_EQUAL(newPos.Position, pos.Position, 1e-2);
    }
}
