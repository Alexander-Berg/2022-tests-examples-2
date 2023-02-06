#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <taxi/graph/libs/graph/edge.h>
#include <taxi/graph/libs/graph/types.h>
#include <taxi/graph/libs/graph/position_on_edge.h>
#include <taxi/graph/libs/graph/position_on_graph.h>
#include <taxi/graph/libs/graph/possible_position_on_edge.h>

using NTaxi::NGraph2::TPositionOnEdge;
using NTaxi::NGraph2::TPositionOnGraph;
using NTaxi::NGraph2::TPossiblePositionOnEdge;
using NTaxi::NGraph2::UNDEFINED;
using namespace NTaxi::NGraph2Literals;

bool operator==(const TPositionOnEdge& first, const TPositionOnEdge& second) noexcept {
    return first.GetEdgeId() == second.GetEdgeId() && first.GetPosition() == second.GetPosition();
}

bool operator==(const TPositionOnGraph& first, const TPositionOnGraph& second) noexcept {
    return second.GetSegmentPosition() == first.GetSegmentPosition() && second.GetEdgeId() == first.GetEdgeId() && second.GetSegmentIdx() == first.GetSegmentIdx();
}

Y_UNIT_TEST_SUITE(PositionOnGraph) {
    Y_UNIT_TEST(Default) {
        TPositionOnGraph pos;
        UNIT_ASSERT_EQUAL(pos.GetEdgeId(), UNDEFINED);
        UNIT_ASSERT_EQUAL(pos.GetSegmentIdx(), 0u);
        UNIT_ASSERT_DOUBLES_EQUAL(pos.GetSegmentPosition(), 0., 1e-2);
    }

    Y_UNIT_TEST(BaseCtor) {
        TPositionOnGraph pos{10_eid, 3, 0.1};
        UNIT_ASSERT_EQUAL(pos.GetEdgeId(), 10_eid);
        UNIT_ASSERT_EQUAL(pos.GetSegmentIdx(), 3u);
        UNIT_ASSERT_DOUBLES_EQUAL(pos.GetSegmentPosition(), 0.1, 1e-2);
    }

    Y_UNIT_TEST(Setters) {
        TPositionOnGraph pos;
        pos.SetEdgeId(10_eid);
        pos.SetSegmentIdx(3);
        pos.SetSegmentPosition(0.1);
        UNIT_ASSERT_EQUAL(pos.GetEdgeId(), 10_eid);
        UNIT_ASSERT_EQUAL(pos.GetSegmentIdx(), 3u);
        UNIT_ASSERT_DOUBLES_EQUAL(pos.GetSegmentPosition(), 0.1, 1e-2);
    }

    Y_UNIT_TEST(MoveCtor) {
        TPositionOnGraph pos{10_eid, 3, 0.1};
        TPositionOnGraph newPos{std::move(pos)};
        UNIT_ASSERT_EQUAL(newPos.GetEdgeId(), 10_eid);
        UNIT_ASSERT_EQUAL(newPos.GetSegmentIdx(), 3u);
        UNIT_ASSERT_DOUBLES_EQUAL(newPos.GetSegmentPosition(), 0.1, 1e-2);
    }

    Y_UNIT_TEST(Move) {
        TPositionOnGraph pos{10_eid, 3, 0.1};
        TPositionOnGraph newPos;
        UNIT_ASSERT_EQUAL(newPos.GetEdgeId(), UNDEFINED);
        newPos = std::move(pos);
        UNIT_ASSERT_EQUAL(newPos.GetEdgeId(), 10_eid);
        UNIT_ASSERT_EQUAL(newPos.GetSegmentIdx(), 3u);
        UNIT_ASSERT_DOUBLES_EQUAL(newPos.GetSegmentPosition(), 0.1, 1e-2);
    }

    Y_UNIT_TEST(CopyCtor) {
        TPositionOnGraph pos{10_eid, 3, 0.1};
        TPositionOnGraph newPos{pos};
        UNIT_ASSERT_EQUAL(newPos.GetEdgeId(), pos.GetEdgeId());
        UNIT_ASSERT_EQUAL(newPos.GetSegmentIdx(), pos.GetSegmentIdx());
        UNIT_ASSERT_DOUBLES_EQUAL(newPos.GetSegmentPosition(), pos.GetSegmentPosition(), 1e-2);
    }

    Y_UNIT_TEST(Copy) {
        TPositionOnGraph pos{10_eid, 3, 0.1};
        TPositionOnGraph newPos;
        UNIT_ASSERT_EQUAL(newPos.GetEdgeId(), UNDEFINED);
        newPos = pos;
        UNIT_ASSERT_EQUAL(newPos.GetEdgeId(), pos.GetEdgeId());
        UNIT_ASSERT_EQUAL(newPos.GetSegmentIdx(), pos.GetSegmentIdx());
        UNIT_ASSERT_DOUBLES_EQUAL(newPos.GetSegmentPosition(), pos.GetSegmentPosition(), 1e-2);
    }
}

Y_UNIT_TEST_SUITE(PositionOnEdge) {
    Y_UNIT_TEST(Default) {
        TPositionOnEdge pos;
        UNIT_ASSERT_EQUAL(pos.GetEdgeId(), UNDEFINED);
        UNIT_ASSERT_DOUBLES_EQUAL(pos.GetPosition(), 0., 1e-2);
    }

    Y_UNIT_TEST(BaseCtor) {
        TPositionOnEdge pos{10_eid, 0.1};
        UNIT_ASSERT_EQUAL(pos.GetEdgeId(), 10_eid);
        UNIT_ASSERT_DOUBLES_EQUAL(pos.GetPosition(), 0.1, 1e-2);
    }

    Y_UNIT_TEST(Setters) {
        TPositionOnEdge pos;
        pos.SetEdgeId(10_eid);
        pos.SetPosition(0.1);
        UNIT_ASSERT_EQUAL(pos.GetEdgeId(), 10_eid);
        UNIT_ASSERT_DOUBLES_EQUAL(pos.GetPosition(), 0.1, 1e-2);
    }

    Y_UNIT_TEST(MoveCtor) {
        TPositionOnEdge pos{10_eid, 0.1};
        TPositionOnEdge newPos{std::move(pos)};
        UNIT_ASSERT_EQUAL(newPos.GetEdgeId(), 10_eid);
        UNIT_ASSERT_DOUBLES_EQUAL(newPos.GetPosition(), 0.1, 1e-2);
    }

    Y_UNIT_TEST(Move) {
        TPositionOnEdge pos{10_eid, 0.1};
        TPositionOnEdge newPos;
        UNIT_ASSERT_EQUAL(newPos.GetEdgeId(), UNDEFINED);
        newPos = std::move(pos);
        UNIT_ASSERT_EQUAL(newPos.GetEdgeId(), 10_eid);
        UNIT_ASSERT_DOUBLES_EQUAL(newPos.GetPosition(), 0.1, 1e-2);
    }

    Y_UNIT_TEST(CopyCtor) {
        TPositionOnEdge pos{10_eid, 0.1};
        TPositionOnEdge newPos{pos};
        UNIT_ASSERT_EQUAL(newPos.GetEdgeId(), pos.GetEdgeId());
        UNIT_ASSERT_DOUBLES_EQUAL(newPos.GetPosition(), pos.GetPosition(), 1e-2);
    }

    Y_UNIT_TEST(Copy) {
        TPositionOnEdge pos{10_eid, 0.1};
        TPositionOnEdge newPos;
        UNIT_ASSERT_EQUAL(newPos.GetEdgeId(), UNDEFINED);
        newPos = pos;
        UNIT_ASSERT_EQUAL(newPos.GetEdgeId(), pos.GetEdgeId());
        UNIT_ASSERT_DOUBLES_EQUAL(newPos.GetPosition(), pos.GetPosition(), 1e-2);
    }
}

Y_UNIT_TEST_SUITE(PossiblePositionOnEdge) {
    Y_UNIT_TEST(Default) {
        TPositionOnEdge pos;
        TPossiblePositionOnEdge possiblePos{pos, 0.5};
        UNIT_ASSERT_EQUAL(pos.GetEdgeId(), UNDEFINED);
        UNIT_ASSERT_EQUAL(possiblePos.GetPositionOnEdge().GetEdgeId(), UNDEFINED);
        UNIT_ASSERT_DOUBLES_EQUAL(possiblePos.GetProbability(), 0.5, 1e-2);
    }

    Y_UNIT_TEST(BaseCtor) {
        TPositionOnEdge pos{10_eid, 0.1};
        TPossiblePositionOnEdge possiblePos{pos, 0.5};
        UNIT_ASSERT_EQUAL(possiblePos.GetPositionOnEdge().GetEdgeId(), 10_eid);
        UNIT_ASSERT_DOUBLES_EQUAL(possiblePos.GetPositionOnEdge().GetPosition(), 0.1, 1e-2);
        UNIT_ASSERT_DOUBLES_EQUAL(possiblePos.GetProbability(), .5, 1e-2);
    }

    Y_UNIT_TEST(MoveCtor) {
        TPositionOnEdge pos{10_eid, 0.1};
        TPossiblePositionOnEdge possiblePos{pos, 0.5};
        TPossiblePositionOnEdge newPossiblePos{std::move(possiblePos)};
        UNIT_ASSERT_EQUAL(newPossiblePos.GetPositionOnEdge().GetEdgeId(), 10_eid);
        UNIT_ASSERT_DOUBLES_EQUAL(newPossiblePos.GetPositionOnEdge().GetPosition(), 0.1, 1e-2);
        UNIT_ASSERT_DOUBLES_EQUAL(newPossiblePos.GetProbability(), .5, 1e-2);
    }

    Y_UNIT_TEST(Move) {
        TPositionOnEdge pos{10_eid, 0.1};
        TPossiblePositionOnEdge possiblePos{pos, 0.5};
        TPossiblePositionOnEdge newPossiblePos;
        UNIT_ASSERT_EQUAL(newPossiblePos.GetPositionOnEdge().GetEdgeId(), UNDEFINED);
        newPossiblePos = std::move(possiblePos);
        UNIT_ASSERT_DOUBLES_EQUAL(newPossiblePos.GetPositionOnEdge().GetPosition(), 0.1, 1e-2);
        UNIT_ASSERT_DOUBLES_EQUAL(newPossiblePos.GetProbability(), .5, 1e-2);
    }

    Y_UNIT_TEST(CopyCtor) {
        TPositionOnEdge pos{10_eid, 0.1};
        TPossiblePositionOnEdge possiblePos{pos, 0.5};
        TPossiblePositionOnEdge newPossiblePos{possiblePos};

        UNIT_ASSERT_EQUAL(newPossiblePos.GetPositionOnEdge().GetEdgeId(), 10_eid);
        UNIT_ASSERT_DOUBLES_EQUAL(newPossiblePos.GetPositionOnEdge().GetPosition(), 0.1, 1e-2);
        UNIT_ASSERT_DOUBLES_EQUAL(newPossiblePos.GetProbability(), .5, 1e-2);
    }

    Y_UNIT_TEST(Copy) {
        TPositionOnEdge pos{10_eid, 0.1};
        TPossiblePositionOnEdge possiblePos{pos, 0.5};
        TPossiblePositionOnEdge newPossiblePos;

        UNIT_ASSERT_EQUAL(newPossiblePos.GetPositionOnEdge().GetEdgeId(), UNDEFINED);

        newPossiblePos = possiblePos;
        UNIT_ASSERT_EQUAL(newPossiblePos.GetPositionOnEdge().GetEdgeId(), 10_eid);
        UNIT_ASSERT_DOUBLES_EQUAL(newPossiblePos.GetPositionOnEdge().GetPosition(), 0.1, 1e-2);
        UNIT_ASSERT_DOUBLES_EQUAL(newPossiblePos.GetProbability(), .5, 1e-2);
    }

    Y_UNIT_TEST(Container) {
        TPositionOnEdge pos{10_eid, 0.1};
        TPossiblePositionOnEdge possiblePos{pos, 0.5};

        {
            TVector<TPossiblePositionOnEdge> positions;
        }

        {
            TVector<TPossiblePositionOnEdge> positions;
            positions.push_back(possiblePos);
        }

        {
            TVector<TPossiblePositionOnEdge> positions;
            positions.push_back(possiblePos);
            TVector<TPossiblePositionOnEdge> copy;
            copy = positions;
            UNIT_ASSERT_EQUAL(copy[0].GetPositionOnEdge().GetEdgeId(), 10_eid);
            UNIT_ASSERT_DOUBLES_EQUAL(copy[0].GetPositionOnEdge().GetPosition(), 0.1, 1e-2);
            UNIT_ASSERT_DOUBLES_EQUAL(copy[0].GetProbability(), .5, 1e-2);
        }

        {
            TVector<TPossiblePositionOnEdge> positions;
            positions.push_back(possiblePos);
            TVector<TPossiblePositionOnEdge> copy{positions};
            UNIT_ASSERT_EQUAL(copy[0].GetPositionOnEdge().GetEdgeId(), 10_eid);
            UNIT_ASSERT_DOUBLES_EQUAL(copy[0].GetPositionOnEdge().GetPosition(), 0.1, 1e-2);
            UNIT_ASSERT_DOUBLES_EQUAL(copy[0].GetProbability(), .5, 1e-2);
        }

        {
            TVector<TPossiblePositionOnEdge> positions;
            positions.push_back(possiblePos);
            TVector<TPossiblePositionOnEdge> moved;
            moved = std::move(positions);
            UNIT_ASSERT_EQUAL(moved[0].GetPositionOnEdge().GetEdgeId(), 10_eid);
            UNIT_ASSERT_DOUBLES_EQUAL(moved[0].GetPositionOnEdge().GetPosition(), 0.1, 1e-2);
            UNIT_ASSERT_DOUBLES_EQUAL(moved[0].GetProbability(), .5, 1e-2);
        }

        {
            TVector<TPossiblePositionOnEdge> positions;
            positions.push_back(possiblePos);
            TVector<TPossiblePositionOnEdge> moved{std::move(positions)};
            UNIT_ASSERT_EQUAL(moved[0].GetPositionOnEdge().GetEdgeId(), 10_eid);
            UNIT_ASSERT_DOUBLES_EQUAL(moved[0].GetPositionOnEdge().GetPosition(), 0.1, 1e-2);
            UNIT_ASSERT_DOUBLES_EQUAL(moved[0].GetProbability(), .5, 1e-2);
        }
    }
}
