#include <clients/helpers.hpp>

#include <userver/utest/utest.hpp>

#include <geobus/channels/edge_positions/listener.hpp>
#include <geobus/channels/positions/listener.hpp>

namespace {

TEST(HasSeparateStatsTest, Simple) {
  EXPECT_TRUE(
      geobus::clients::kHasSeparateStats<geobus::clients::PositionsListener>);

  EXPECT_TRUE(geobus::clients::kHasSeparateStats<
              geobus::clients::EdgePositionsListener>);
}

}  // namespace
