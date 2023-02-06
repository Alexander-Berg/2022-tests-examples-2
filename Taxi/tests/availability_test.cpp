#include <partners/availability/availability_checker.hpp>

#include <userver/utest/utest.hpp>
#include <userver/utils/datetime.hpp>
#include <userver/utils/mock_now.hpp>

namespace nmn = eats_nomenclature;

namespace {

const std::string kDumpFilenameDateFormat = "%Y-%m-%dT%H-%M-%S";
const std::chrono::system_clock::time_point kMockNow =
    ::utils::datetime::Stringtime("2020-08-25T12-00-00", "UTC",
                                  kDumpFilenameDateFormat);
const std::chrono::system_clock::time_point kMockPast =
    kMockNow - std::chrono::hours{100};
const std::chrono::system_clock::time_point kMockFuture =
    kMockNow + std::chrono::hours{100};

}  // namespace

namespace {

struct IsAvailableTestParam {
  std::optional<uint32_t> stock_opt;
  std::optional<std::chrono::system_clock::time_point> available_from_opt;
  std::optional<std::chrono::system_clock::time_point>
      force_unavailable_until_opt;
  uint32_t available_from_offset_in_mins;
  uint32_t stock_reset_limit;
  std::optional<bool> is_available_by_autodisable_algorithms_opt;
  bool ignore_available_from;
};

class AvailabilityTestBase
    : public ::testing::TestWithParam<IsAvailableTestParam> {
 public:
  void SetUp() override { ::utils::datetime::MockNowSet(kMockNow); }
  void TearDown() override { ::utils::datetime::MockNowUnset(); }
};

class IsAvailableTest : public AvailabilityTestBase {};

class IsNotAvailableTest : public AvailabilityTestBase {};

}  // namespace

namespace {

template <typename T>
std::optional<T> ConvertBoolOpt(const std::optional<bool>& flag_opt) {
  if (!flag_opt) {
    return std::nullopt;
  }
  return T{*flag_opt};
}

bool IsAvailable(const IsAvailableTestParam& test_param) {
  return nmn::partners::availability::IsAvailable(
      std::optional<nmn::clients::models::Stock>{test_param.stock_opt},
      std::optional<nmn::clients::models::AvailableFrom>{
          test_param.available_from_opt},
      std::optional<nmn::autodisable_items::models::ForceUnavailableUntil>{
          test_param.force_unavailable_until_opt},
      std::chrono::minutes{test_param.available_from_offset_in_mins},
      nmn::models::StockResetLimit{test_param.stock_reset_limit},
      ConvertBoolOpt<nmn::models::IsAvailable>(
          test_param.is_available_by_autodisable_algorithms_opt),
      test_param.ignore_available_from);
}

}  // namespace

namespace eats_nomenclature::partners::processing::tests {

TEST_P(IsAvailableTest, Test) { ASSERT_TRUE(::IsAvailable(GetParam())); }

INSTANTIATE_TEST_SUITE_P(
    IsAvailableInst, IsAvailableTest,
    ::testing::Values(
        // null stocks
        IsAvailableTestParam{std::nullopt, kMockPast, std::nullopt, 0, 0,
                             std::nullopt, false},
        // nonzero stocks
        IsAvailableTestParam{1, kMockPast, std::nullopt, 0, 0, std::nullopt,
                             false},
        // stock reset limit
        IsAvailableTestParam{3, kMockPast, std::nullopt, 0, 2, std::nullopt,
                             false},
        // offset
        IsAvailableTestParam{std::nullopt, kMockNow + std::chrono::minutes{1},
                             std::nullopt, 2, 0, std::nullopt, false},
        // force_unavailable
        IsAvailableTestParam{std::nullopt, kMockPast, kMockPast, 0, 0,
                             std::nullopt, false},
        // available by autodisable algorithms
        IsAvailableTestParam{std::nullopt, kMockPast, std::nullopt, 0, 0, true,
                             false},
        // ignore available_from
        IsAvailableTestParam{std::nullopt, kMockFuture, std::nullopt, 0, 0,
                             std::nullopt, true},
        IsAvailableTestParam{std::nullopt, std::nullopt, std::nullopt, 0, 0,
                             std::nullopt, true}));

TEST_P(IsNotAvailableTest, Test) { ASSERT_FALSE(::IsAvailable(GetParam())); }

INSTANTIATE_TEST_SUITE_P(
    IsNotAvailableInst, IsNotAvailableTest,
    ::testing::Values(
        // zero stocks
        IsAvailableTestParam{0, kMockPast, std::nullopt, 0, 0, std::nullopt,
                             false},
        // stock reset limit
        IsAvailableTestParam{3, kMockPast, std::nullopt, 0, 5, std::nullopt,
                             false},
        // available_from in future
        IsAvailableTestParam{std::nullopt, kMockFuture, std::nullopt, 0, 0,
                             std::nullopt, false},
        // null available_from
        IsAvailableTestParam{std::nullopt, std::nullopt, std::nullopt, 0, 0,
                             std::nullopt, false},
        // offset
        IsAvailableTestParam{std::nullopt, kMockNow + std::chrono::minutes{2},
                             std::nullopt, 1, 0, std::nullopt, false},
        // force_unavailable
        IsAvailableTestParam{std::nullopt, kMockPast, kMockFuture, 0, 0,
                             std::nullopt, false},
        // not available by autodisable algorithms
        IsAvailableTestParam{std::nullopt, kMockPast, std::nullopt, 0, 0, false,
                             false}));

}  // namespace eats_nomenclature::partners::processing::tests
