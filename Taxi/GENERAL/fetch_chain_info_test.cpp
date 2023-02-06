#include <gtest/gtest.h>

#include <list>

#include <userver/utest/utest.hpp>

#include <filters/grocery/fetch_shifts/fetch_shifts.hpp>
#include <filters/infrastructure/fetch_driver/fetch_driver.hpp>
#include <filters/infrastructure/fetch_driver_orders/fetch_driver_orders.hpp>
#include <filters/infrastructure/fetch_driver_status/fetch_driver_status.hpp>
#include <filters/partners/fetch_eats_shifts/fetch_eats_shifts.hpp>
#include "fetch_chain_info.hpp"

namespace filters = candidates::filters;
using filters::efficiency::FetchChainInfo;

namespace {

filters::Context CreateContext(const bool on_order,
                               const bool is_eats_shift = false,
                               const bool is_grocery_shift = false) {
  filters::Context context;
  filters::infrastructure::FetchDriverStatus::Set(
      context, models::DriverStatus::kOnline);

  if (is_eats_shift) {
    filters::partners::FetchEatsShifts::Set(
        context, std::make_shared<models::EatsShift>(models::EatsShift{}));
  }
  if (is_grocery_shift) {
    filters::grocery::FetchShifts::Set(
        context,
        std::make_shared<models::GroceryShift>(models::GroceryShift{}));
  }

  if (on_order) {
    const auto orders = std::make_shared<models::driver_orders::Orders>();
    orders->emplace_back("1", "yandex", models::driver_orders::Status::Driving,
                         std::chrono::system_clock::now());
    filters::infrastructure::FetchDriverOrders::Set(context, orders);
  }
  return context;
}

const filters::FilterInfo kEmptyInfo;
}  // namespace

UTEST(FetchChainInfo, One) {
  auto chain_busy_drivers = std::make_shared<models::ChainBusyDrivers>();
  chain_busy_drivers->emplace(
      std::string("dbid_uuid"),
      std::make_shared<const models::ChainBusyDriver>());

  candidates::GeoMember member{{}, "dbid_uuid"};

  candidates::models::ChainSettings zone_class;
  auto context = CreateContext(false);
  FetchChainInfo filter(
      kEmptyInfo, zone_class, chain_busy_drivers,
      ::utils::SharedReadablePtr<::models::ComboFree>(nullptr));

  EXPECT_EQ(filters::Result::kAllow, filter.Process(member, context));
  EXPECT_THROW(FetchChainInfo::Get(context), std::runtime_error);

  context = CreateContext(true);
  EXPECT_EQ(filters::Result::kAllow, filter.Process(member, context));
  EXPECT_NO_THROW(FetchChainInfo::Get(context));
}

UTEST(FetchChainInfo, Two) {
  auto chain_busy_drivers = std::make_shared<models::ChainBusyDrivers>();

  candidates::models::ChainSettings zone_class;
  zone_class.max_route_distance = 100;
  zone_class.max_line_distance = 100;
  zone_class.max_route_time = 100;
  FetchChainInfo filter(
      kEmptyInfo, zone_class, chain_busy_drivers,
      ::utils::SharedReadablePtr<::models::ComboFree>(nullptr));

  auto context = CreateContext(true);

  models::ChainBusyDriver chain_busy_driver;

  chain_busy_driver.left_dist = 150;
  chain_busy_driver.left_time = 150;
  chain_busy_driver.approximate = true;
  (*chain_busy_drivers)["dbid_uuid"] =
      std::make_shared<models::ChainBusyDriver>(chain_busy_driver);

  EXPECT_EQ(filter.Process({}, context), filters::Result::kAllow);
  EXPECT_TRUE(FetchChainInfo::TryGet(context) == nullptr);

  chain_busy_driver.left_dist = 50;
  chain_busy_driver.left_time = 50;
  chain_busy_driver.approximate = true;
  (*chain_busy_drivers)["dbid_uuid"] =
      std::make_shared<models::ChainBusyDriver>(chain_busy_driver);

  candidates::GeoMember member{{}, "dbid_uuid"};

  EXPECT_EQ(filter.Process(member, context), filters::Result::kAllow);
  EXPECT_TRUE(FetchChainInfo::TryGet(context) != nullptr);
}

UTEST(FetchChainInfo, Shifts) {
  using ShiftType = FetchChainInfo::ShiftType;
  auto chain_busy_drivers = std::make_shared<models::ChainBusyDrivers>();

  candidates::models::ChainSettings zone_class;
  zone_class.max_route_distance = 100;
  zone_class.max_line_distance = 100;
  zone_class.max_route_time = 100;

  models::ChainBusyDriver chain_busy_driver;
  chain_busy_driver.left_dist = 50;
  chain_busy_driver.left_time = 50;
  chain_busy_driver.approximate = true;
  (*chain_busy_drivers)["dbid_uuid"] =
      std::make_shared<models::ChainBusyDriver>(chain_busy_driver);

  candidates::GeoMember member{{}, "dbid_uuid"};

  for (bool eats_shift : {false, true}) {
    for (bool grocery_shift : {false, true}) {
      auto context = CreateContext(true, eats_shift, grocery_shift);
      filters::infrastructure::FetchDriverStatus::Set(
          context, models::DriverStatus::kBusy);
      FetchChainInfo::SetMode(context, FetchChainInfo::Mode::kChain);
      for (auto shift_type : std::list<std::optional<ShiftType>>{
               std::nullopt, ShiftType::kEats, ShiftType::kGrocery}) {
        const bool eats_params = shift_type && *shift_type == ShiftType::kEats;
        const bool grocery_params =
            shift_type && *shift_type == ShiftType::kGrocery;
        FetchChainInfo filter(
            kEmptyInfo, zone_class, chain_busy_drivers,
            ::utils::SharedReadablePtr<::models::ComboFree>(nullptr),
            shift_type);
        auto result =
            ((eats_shift && eats_params) || (grocery_shift && grocery_params))
                ? filters::Result::kAllow
                : filters::Result::kDisallow;

        EXPECT_EQ(filter.Process(member, context), result);
        if (result == filters::Result::kAllow) {
          EXPECT_TRUE(FetchChainInfo::TryGet(context) != nullptr);
        }
      }
    }
  }
}

struct FetchChainInfoParam {
  FetchChainInfo::Mode mode;
  bool on_order;
  filters::Result result;
};

class FetchChainInfoMode
    : public ::testing::TestWithParam<FetchChainInfoParam> {};

UTEST_P(FetchChainInfoMode, Sample) {
  const auto& param = GetParam();

  auto chain_busy_drivers = std::make_shared<models::ChainBusyDrivers>();
  chain_busy_drivers->emplace(
      std::string("dbid_uuid"),
      std::make_shared<const models::ChainBusyDriver>());

  candidates::models::ChainSettings zone_class;

  auto context = CreateContext(param.on_order);
  FetchChainInfo::SetMode(context, param.mode);

  FetchChainInfo filter(
      kEmptyInfo, zone_class, chain_busy_drivers,
      ::utils::SharedReadablePtr<::models::ComboFree>(nullptr));

  candidates::GeoMember member{{}, "dbid_uuid"};

  EXPECT_EQ(param.result, filter.Process(member, context));
}

INSTANTIATE_UTEST_SUITE_P(
    FetchMode, FetchChainInfoMode,
    ::testing::Values(FetchChainInfoParam{FetchChainInfo::Mode::kDefault, false,
                                          filters::Result::kAllow},
                      FetchChainInfoParam{FetchChainInfo::Mode::kDefault, true,
                                          filters::Result::kAllow},
                      FetchChainInfoParam{FetchChainInfo::Mode::kNoChain, false,
                                          filters::Result::kAllow},
                      FetchChainInfoParam{FetchChainInfo::Mode::kNoChain, true,
                                          filters::Result::kDisallow},
                      FetchChainInfoParam{FetchChainInfo::Mode::kChain, false,
                                          filters::Result::kDisallow},
                      FetchChainInfoParam{FetchChainInfo::Mode::kChain, true,
                                          filters::Result::kAllow}));
