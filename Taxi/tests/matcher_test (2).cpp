#include <gtest/gtest.h>

#include <geometry/position.hpp>

#include <internal/match_orders_drivers/matcher.hpp>
#include <internal/yt_logger_wrapper.hpp>
#include <models/deviation_formulas.hpp>

namespace {

const std::string kDummy{};
const geometry::Position kDummyPoint{};
const auto kNow = utils::datetime::Now();

}  // namespace

using clients::routing::RouteInfo;
using interlayers::routing::RouteInfoFuturesFallback;
using interlayers::routing::RouteInfos;

TEST(DeviationFormula, RegularEnRoute) {
  internal::YtLoggerWrapper yt_logger{nullptr};

  const double t0 = 600.;
  const double d0 = 2100.;

  models::deviation_formulas::RegularMode config{};

  config.min_home_time_ratio = -0.5;
  config.home_time_ratio = 1.5;
  config.min_home_dist_ratio = -0.5;
  config.home_dist_ratio = 1.5;
  config.da_time_ratio = 0.99;
  config.da_dist_ratio = 0.99;
  config.home_cancel_prob = 0.1;
  config.min_order_distance = d0;
  config.min_order_time = t0;

  // full testing for:
  //    time_check && distance_check && order_time && order_distance
  for (int i = 0; i <= 0b111111; i++) {
    const double t1 = (i & 0b010000) ? t0 - 1. : t0 + 1.;
    const double d1 = (i & 0b100000) ? d0 - 1. : d0 + 1.;
    const double dh_t =
        std::round(t1 * ((i & 0b000001) ? ((i & 0b000100) ? 3.3501 : 3.3399)
                                        : ((i & 0b000100) ? 1.5399 : 1.5501)));
    const double dh_d =
        std::round(d1 * ((i & 0b000010) ? ((i & 0b001000) ? 3.3501 : 3.3399)
                                        : ((i & 0b001000) ? 1.5399 : 1.5501)));

    RouteInfos routes{
        RouteInfo(t1, d1),  // bh
        RouteInfo(t1, d1)   // ah
    };

    models::match_orders_drivers::regular_mode::Data data{
        models::match_orders_drivers::VerdictId{"order_id", "session_id",
                                                "formula_id"},
        kDummy,
        kDummy,
        kDummy,
        kDummyPoint,
        kDummyPoint,
        kDummyPoint,
        config,
        std::make_unique<RouteInfoFuturesFallback>(std::move(routes)),
        std::nullopt,
        std::nullopt,
        std::nullopt,
    };

    std::optional<RouteInfo> ab_route{RouteInfo(t1, d1)};
    std::optional<RouteInfo> da_route{RouteInfo(t1, d1)};
    std::optional<RouteInfo> dh_route{RouteInfo(dh_t, dh_d)};

    internal::match_orders_drivers::Matcher matcher{
        kDummy,      kDummy,      {},
        kDummyPoint, kDummyPoint, utils::datetime::Now(),
        ab_route,    da_route,    dh_route,
        kDummy,      kNow,        yt_logger,
    };

    EXPECT_EQ((i & 0b111100) == 0, matcher(data).en_route.suitable);
  }
}

TEST(DeviationFormula, RegularOfferEnRoute) {
  internal::YtLoggerWrapper yt_logger{nullptr};

  const double t0 = 600.;
  const double d0 = 2100.;
  const double s0 = 1.;

  models::deviation_formulas::RegularOfferMode config{};

  config.min_home_time_ratio = -0.5;
  config.home_time_ratio = 1.5;
  config.min_home_dist_ratio = -0.5;
  config.home_dist_ratio = 1.5;
  config.da_time_ratio = 0.99;
  config.da_dist_ratio = 0.99;
  config.home_cancel_prob = 0.1;
  config.min_order_distance = d0;
  config.min_order_time = t0;
  config.min_b_surge = s0;
  config.min_surge_gradient = s0;

  // full testing for:
  // time_check && distance_check &&
  // order_time && order_distance &&
  // min_b_surge && min_surge_gradient
  for (int i = 0; i <= 0b11111111; i++) {
    const double t1 = (i & 0b00010000) ? t0 - 1. : t0 + 1.;
    const double d1 = (i & 0b00100000) ? d0 - 1. : d0 + 1.;
    const double dh_t =
        std::round(t1 * ((i & 0b000001) ? ((i & 0b000100) ? 3.3501 : 3.3399)
                                        : ((i & 0b000100) ? 1.5399 : 1.5501)));
    const double dh_d =
        std::round(d1 * ((i & 0b000010) ? ((i & 0b001000) ? 3.3501 : 3.3399)
                                        : ((i & 0b001000) ? 1.5399 : 1.5501)));
    const double s_b = (i & 0b01000000) ? s0 + 1. : s0;
    const double s_d = (i & 0b10000000) ? s_b - 0.5 : s_b + 1.;

    RouteInfos routes{
        RouteInfo(t1, d1),  // bh
        RouteInfo(t1, d1)   // ah
    };

    models::match_orders_drivers::regular_offer_mode::Data data{
        models::match_orders_drivers::VerdictId{"order_id", "session_id",
                                                "formula_id"},
        kDummy,
        kDummy,
        kDummy,
        kDummyPoint,
        kDummyPoint,
        kDummyPoint,
        config,
        s_b,
        s_d,
        std::make_unique<RouteInfoFuturesFallback>(std::move(routes)),
        std::nullopt,
        std::nullopt,
        std::nullopt,
    };

    std::optional<RouteInfo> ab_route{RouteInfo(t1, d1)};
    std::optional<RouteInfo> da_route{RouteInfo(t1, d1)};
    std::optional<RouteInfo> dh_route{RouteInfo(dh_t, dh_d)};

    internal::match_orders_drivers::Matcher matcher{
        kDummy,      kDummy,      {},
        kDummyPoint, kDummyPoint, utils::datetime::Now(),
        ab_route,    da_route,    dh_route,
        kDummy,      kNow,        yt_logger,
    };

    const bool en_route = matcher(data).en_route.suitable;
    const bool route_check = (i & 0b00111100) == 0;
    const bool surge_check = (i & 0b01000000) && (i & 0b10000000);

    EXPECT_EQ(route_check && surge_check, en_route);
  }
}

TEST(DeviationFormula, SurgeEnRoute) {
  internal::YtLoggerWrapper yt_logger{nullptr};

  const double t0 = 600.;
  const double d0 = 2100.;
  const double s0 = 1.;

  models::deviation_formulas::SurgeMode config{};

  config.min_b_surge = s0;
  config.min_b_lrsp_time = t0;
  config.min_order_distance = d0;
  config.min_order_time = t0;

  // full testing for:
  // order_time && order_distance && min_b_lrsp_time && min_b_surge
  for (int i = 0; i <= 0b1111; i++) {
    const double t1 = (i & 0b0001) ? t0 + 1. : t0 - 1.;
    const double d1 = (i & 0b0010) ? d0 + 1. : d0 - 1.;
    const double t2 = (i & 0b0100) ? t0 + 1. : t0 - 1.;
    const double s_b = (i & 0b1000) ? s0 + 1. : s0 - 1.;

    RouteInfos routes{
        RouteInfo(t2, d0)  // blrsp
    };

    models::match_orders_drivers::surge_mode::Data data{
        models::match_orders_drivers::VerdictId{"order_id", "session_id",
                                                "formula_id"},
        kDummy,
        kDummy,
        kDummy,
        kDummyPoint,
        kDummyPoint,
        kDummyPoint,
        config,
        s_b,
        std::make_unique<RouteInfoFuturesFallback>(std::move(routes)),
    };

    std::optional<RouteInfo> ab_route{RouteInfo(t1, d1)};
    std::optional<RouteInfo> da_route;
    std::optional<RouteInfo> dh_route;

    internal::match_orders_drivers::Matcher matcher{
        kDummy,      kDummy,      {},
        kDummyPoint, kDummyPoint, utils::datetime::Now(),
        ab_route,    da_route,    dh_route,
        kDummy,      kNow,        yt_logger,
    };

    EXPECT_EQ(i == 0b1111, matcher(data).en_route.suitable);
  }
}
