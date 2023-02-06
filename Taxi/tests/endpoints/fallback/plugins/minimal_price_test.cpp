#include <userver/utest/utest.hpp>

#include "build_default_test.hpp"

#include <endpoints/fallback/plugins/main_fallback/minimal_price/minimal_price.hpp>
#include <userver/utils/mock_now.hpp>

namespace routestats::fallback::main {

void TestGetMinimalPrice(const core::Zone& zone,
                         std::optional<decimal64::Decimal<4>> expected) {
  // 9:15 Wed
  const auto now =
      std::chrono::system_clock::time_point(std::chrono::seconds(1605075300));
  utils::datetime::MockNowSet(now);

  auto result = GetMinimalPrice(zone, "econom");
  ASSERT_EQ(result, expected);
}

// TODO(gerus]): add tests for happy-path, maximum(minimal, minimal_price),
// not-match-day-type, not-match-time-interval
// it's probably problem with mock now()

TEST(GetMinimalPrice, NotMatchCategoryType) {
  auto zone = BuildDefaultZone();
  zone.tariff.minimal_prices[0].category_type =
      MinimalPrice::CategoryType::kCallCenter;
  TestGetMinimalPrice(zone, std::nullopt);
}

}  // namespace routestats::fallback::main
