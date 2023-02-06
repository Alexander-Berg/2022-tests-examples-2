
#include <array>

#include <userver/utest/utest.hpp>

#include <internal/displaced_percentile.hpp>

namespace {

constexpr size_t displacement = 100u;

using DisplacedPercentile =
    driver_route_responder::internal::DisplacedPercentile<displacement, 200u>;
using ValueType = DisplacedPercentile::ValueType;

inline auto ToRepresentation(ValueType value) {
  return driver_route_responder::internal::detail::ToRepresentation<
      ValueType, displacement>(value);
}

inline auto FromRepresentation(size_t value) {
  return driver_route_responder::internal::detail::FromRepresentation<
      ValueType, displacement>(value);
}

struct TestParam {
  ValueType actual;
  size_t representation;
};

auto MakeTestData() {
  return std::array{
      // clang-format off
      TestParam{-100, 0u},
      TestParam{0, 100u},
      TestParam{66, 166u}
      // clang-format on
  };
}

struct DisplacedPercentileTest : public ::testing::TestWithParam<TestParam> {};

TEST_P(DisplacedPercentileTest, Simple) {
  const auto [actual, representation] = GetParam();
  ASSERT_EQ(ToRepresentation(actual), representation);
  ASSERT_EQ(FromRepresentation(representation), actual);
}

INSTANTIATE_TEST_SUITE_P(DisplacedPercentileTest, DisplacedPercentileTest,
                         ::testing::ValuesIn(MakeTestData()));

TEST(DisplacedPercentileTest, NegativeValues) {
  DisplacedPercentile p;

  p.Account(-50);
  ASSERT_EQ(p.GetPercentile(100.0), -50);

  p.Account(-20);
  ASSERT_EQ(p.GetPercentile(100.0), -20);
  ASSERT_EQ(p.GetPercentile(40.0), -50);
}

TEST(DisplacedPercentileTest, PositiveValues) {
  DisplacedPercentile p;

  p.Account(20);
  ASSERT_EQ(p.GetPercentile(100.0), 20);

  p.Account(50);
  ASSERT_EQ(p.GetPercentile(100.0), 50);
  ASSERT_EQ(p.GetPercentile(40.0), 20);
}

TEST(DisplacedPercentileTest, MixedValues) {
  DisplacedPercentile p;

  p.Account(50);
  p.Account(-50);
  ASSERT_EQ(p.GetPercentile(100.0), 50);
  ASSERT_EQ(p.GetPercentile(40.0), -50);
}

TEST(DisplacedPercentileTest, Add) {
  DisplacedPercentile p;
  p.Account(-50);
  p.Account(20);

  DisplacedPercentile other;
  other.Account(-20);
  other.Account(50);

  p.Add(other);
  ASSERT_EQ(p.GetPercentile(100.0), 50);
  ASSERT_EQ(p.GetPercentile(70.0), 20);
}

TEST(DisplacedPercentileTest, Reset) {
  DisplacedPercentile p;

  p.Account(20);
  ASSERT_EQ(p.GetPercentile(100.0), 20);

  p.Reset();
  ASSERT_EQ(p.GetPercentile(100.0), -100);
}

}  // namespace
