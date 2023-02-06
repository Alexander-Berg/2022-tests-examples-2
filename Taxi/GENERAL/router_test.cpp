#ifdef ARCADIA_ROOT
#include <gtest/gtest.h>

#include <chrono>

#include <graph/routing/router.hpp>
#include <graph/tests/graph_fixture.hpp>
#include <graph/tests/graph_fixture_config.hpp>
#include <graph/tests/print_to.hpp>
#include <userver/utest/utest.hpp>

namespace graph::test {

namespace {
static int leptideaCount = 1;
}  // namespace

class RouterFixture : public graph::test::GraphTestFixture {
 public:
  void SetUp() override {
    graph::test::GraphTestFixture::PluginSetUpTestSuite();
  }
  void TearDown() override {
    graph::test::GraphTestFixture::PluginTearDownTestSuite();
  }
};

UTEST_F(RouterFixture, TestLinePath) {
  using namespace std::chrono_literals;
  using namespace ::geometry::literals;
  const auto& graph = GetGraph();
  auto router = Router(*graph, kTestGraphDataDir, leptideaCount);

  routing_base::Point from{37.529272_lon, 55.697285_lat},
      to{37.526510_lon, 55.698854_lat};

  const auto& result = router.RoutesInfo(from, to);

  ASSERT_EQ(result.size(), 1);
  ASSERT_TRUE(result.front().time);
  ASSERT_EQ(*result.front().time, 18s);
  ASSERT_TRUE(result.front().distance);
  ASSERT_NEAR(result.front().distance->value(), 246.0, 1.0);
}

UTEST_F(RouterFixture, TestSameEdgePath) {
  using namespace std::chrono_literals;
  using namespace ::geometry::literals;
  auto graph = GetGraph();
  auto router = Router(*graph, kTestGraphDataDir, leptideaCount);

  routing_base::Point from{37.527497_lon, 55.698309_lat},
      to{37.522926_lon, 55.700941_lat};

  const auto& result = router.RoutesInfo(from, to);

  ASSERT_EQ(result.size(), 1);
  ASSERT_TRUE(result.front().time);
  ASSERT_EQ(*result.front().time, 31s);
  ASSERT_TRUE(result.front().distance);
  ASSERT_NEAR(result.front().distance->value(), 410.0, 1.0);
}

UTEST_F(RouterFixture, TestManyPaths) {
  using namespace std::chrono_literals;
  using namespace ::geometry::literals;
  auto graph = GetGraph();
  auto router = Router(*graph, kTestGraphDataDir, leptideaCount);

  routing_base::Point from{37.541258_lon, 55.703967_lat},
      to{37.521246_lon, 55.702218_lat};

  const auto& result = router.RoutesPath(from, to);

  ASSERT_EQ(result.size(), 2);
  ASSERT_TRUE(result.front().info.time);
  ASSERT_EQ(*result.front().info.time, 197s);
  ASSERT_TRUE(result.front().info.distance);
  ASSERT_NEAR(result.front().info.distance->value(), 1775.0, 1.0);
  ASSERT_EQ(result.front().path.size(), 34);
  ASSERT_EQ(result.front().legs.size(), 1);
  EXPECT_EQ(result.front().legs[0].point_index, 0);
}

UTEST_F(RouterFixture, TestNoPath) {
  auto graph = GetGraph();
  auto router = Router(*graph, kTestGraphDataDir, leptideaCount);

  using namespace ::geometry::literals;
  routing_base::Point from{0.0_lon, 0.0_lat}, to{37.521246_lon, 55.702218_lat};

  const auto& result = router.RoutesPath(from, to);

  ASSERT_EQ(result.size(), 0);
}

UTEST_F(RouterFixture, TestVia) {
  using namespace std::chrono_literals;
  using namespace ::geometry::literals;
  auto graph = GetGraph();
  auto router = Router(*graph, kTestGraphDataDir, leptideaCount);

  // https://yandex.ru/maps/-/CKuZUBJc
  routing_base::Path path{{37.537827_lon, 55.703361_lat},
                          {37.528398_lon, 55.705305_lat},
                          {37.516642_lon, 55.704832_lat}};

  const auto& result = router.BestRoutePath(path);

  ASSERT_TRUE(result.info.time);
  ASSERT_EQ(*(result.info.time), 277s);
  ASSERT_TRUE(result.info.distance);
  ASSERT_NEAR(result.info.distance->value(), 2318.0, 1.0);
  ASSERT_EQ(result.path.size(), 37);
  ASSERT_EQ(result.legs.size(), 2);

  const auto& last_point = result.path.back();
  ASSERT_NEAR(result.info.distance->value(),
              last_point.distance_since_ride_start.value(), 1.0);
  ASSERT_EQ(result.info.time, last_point.time_since_ride_start);

  EXPECT_EQ(result.legs[0].point_index, 0);
  EXPECT_EQ(result.legs[1].point_index, 20);
  EXPECT_NEAR(result.path[20].GetLatitudeAsDouble(), 55.705305, 0.00001);
  EXPECT_NEAR(result.path[20].GetLongitudeAsDouble(), 37.528398, 0.00001);
}

}  // namespace graph::test
#endif
