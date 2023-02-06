#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include "order_meta.hpp"

namespace {

namespace bm = busy_drivers::models;

const geometry::Position kPointOne{12.34 * geometry::lat,
                                   56.78 * geometry::lon};
const geometry::Position kPointTwo{23.45 * geometry::lat,
                                   67.89 * geometry::lon};
const geometry::Position kPointThree{34.56 * geometry::lat,
                                     78.91 * geometry::lon};

MATCHER_P(IsClosePosition, position, "") {
  return geometry::AreClosePositions(arg, position);
}

void GetUnpassedDestinations(
    const std::vector<geometry::Position>& destinations,
    const std::vector<bool>& destinations_statuses,
    const std::vector<geometry::Position>& result) {
  bm::OrderMeta order;
  order.destinations = destinations;
  order.destinations_statuses = destinations_statuses;

  std::vector<testing::Matcher<geometry::Position>> matchers;
  std::transform(result.begin(), result.end(), std::back_inserter(matchers),
                 [](const auto& p) { return IsClosePosition(p); });

  EXPECT_THAT(order.GetUnpassedDestinations(),
              testing::ElementsAreArray(matchers));
}

}  // namespace

TEST(OrderMeta, GetSingleUnpassedDestination) {
  GetUnpassedDestinations({kPointOne, kPointTwo, kPointThree},
                          {true, false, false}, {kPointTwo, kPointThree});
  GetUnpassedDestinations({kPointOne, kPointTwo, kPointThree},
                          {true, true, false}, {kPointThree});
  GetUnpassedDestinations({kPointOne, kPointTwo, kPointThree},
                          {true, true, true}, {});
  GetUnpassedDestinations({kPointOne, kPointTwo, kPointThree},
                          {true, false, true}, {});
  GetUnpassedDestinations({kPointOne, kPointTwo, kPointThree},
                          {false, true, false}, {kPointThree});
  GetUnpassedDestinations({kPointOne, kPointTwo, kPointThree},
                          {false, false, true}, {});
  GetUnpassedDestinations({kPointOne, kPointTwo, kPointThree},
                          {false, false, false},
                          {kPointOne, kPointTwo, kPointThree});
  GetUnpassedDestinations({kPointOne, kPointTwo, kPointThree},
                          {true, true, true}, {});
  GetUnpassedDestinations({kPointOne, kPointTwo}, {true, false}, {kPointTwo});
  GetUnpassedDestinations({kPointOne, kPointTwo, kPointThree}, {true, true},
                          {kPointThree});
  GetUnpassedDestinations({kPointOne, kPointTwo, kPointThree}, {true, false},
                          {kPointTwo, kPointThree});
  GetUnpassedDestinations({kPointOne, kPointTwo}, {true}, {kPointTwo});
  GetUnpassedDestinations({kPointOne, kPointTwo}, {}, {kPointOne, kPointTwo});
  GetUnpassedDestinations({kPointOne}, {false}, {kPointOne});
  GetUnpassedDestinations({kPointOne}, {true}, {});
  GetUnpassedDestinations({kPointOne}, {}, {kPointOne});
  GetUnpassedDestinations({}, {}, {});
}
