#include "ignore_eta_after_changes_filter.hpp"

#include <userver/utils/mock_now.hpp>
#include "userver/utest/utest.hpp"

namespace {
using IgnoreEtaAfterChangesFilter =
    driver_route_responder::filters::IgnoreEtaAfterChangesFilter;

using Timelefts = driver_route_responder::models::Timelefts;
using Position = driver_route_responder::internal::Position;
using InternalTimelefts = driver_route_responder::models::InternalTimelefts;
using OrderCoreInfo = driver_route_responder::internal::OrderCoreInfo;

void WithoutFallbackChecking(InternalTimelefts& timelefts,
                             const OrderCoreInfo& order_core_info,
                             std::chrono::seconds threshold) {
  IgnoreEtaAfterChangesFilter filter(std::chrono::seconds{threshold});
  filter.VisitOrderCoreInfo(order_core_info);
  filter.ApplyFilter(timelefts);
};

void FallbackChecking(InternalTimelefts& timelefts,
                      const OrderCoreInfo& order_core_info,
                      std::chrono::seconds threshold) {
  IgnoreEtaAfterChangesFilter filter(std::chrono::seconds{threshold});
  filter.VisitFallback();
  filter.VisitOrderCoreInfo(order_core_info);
  filter.ApplyFilter(timelefts);
};
}  // namespace

TEST(IgnoreEtaAfterChangesFilter, BaseTest) {
  utils::datetime::MockNowSet(
      std::chrono::system_clock::time_point{std::chrono::seconds{1654501075}});
  // Check driving status
  {
    InternalTimelefts timelefts;
    OrderCoreInfo order_core_info;
    order_core_info.last_status_info = {"driving", utils::datetime::Now()};

    // Without fallback. It won't affect on ignore_eta.
    WithoutFallbackChecking(timelefts, order_core_info,
                            std::chrono::seconds{1});
    ASSERT_FALSE(timelefts.ignore_eta);

    // With fallback, but threshold is 0s.
    FallbackChecking(timelefts, order_core_info, std::chrono::seconds{0});
    ASSERT_FALSE(timelefts.ignore_eta);

    // With fallback. It will enable filter.
    FallbackChecking(timelefts, order_core_info, std::chrono::seconds{1});
    ASSERT_TRUE(timelefts.ignore_eta);
  }

  // Check transporting status
  {
    InternalTimelefts timelefts;
    OrderCoreInfo order_core_info;
    order_core_info.last_status_info = {"transporting", utils::datetime::Now()};

    // Without fallback. It won't affect on ignore_eta.
    WithoutFallbackChecking(timelefts, order_core_info,
                            std::chrono::seconds{1});
    ASSERT_FALSE(timelefts.ignore_eta);

    // With fallback, but threshold is 0s.
    FallbackChecking(timelefts, order_core_info, std::chrono::seconds{0});
    ASSERT_FALSE(timelefts.ignore_eta);

    // With fallback. It will enable filter.
    FallbackChecking(timelefts, order_core_info, std::chrono::seconds{1});
    ASSERT_TRUE(timelefts.ignore_eta);
  }

  // Check other status
  {
    InternalTimelefts timelefts;
    OrderCoreInfo order_core_info;
    order_core_info.last_status_info = {"waiting", utils::datetime::Now()};

    // Without fallback. It won't affect on ignore_eta.
    WithoutFallbackChecking(timelefts, order_core_info,
                            std::chrono::seconds{1});
    ASSERT_FALSE(timelefts.ignore_eta);

    // With fallback. It will enable filter.
    FallbackChecking(timelefts, order_core_info, std::chrono::seconds{1});
    ASSERT_FALSE(timelefts.ignore_eta);
  }
}
