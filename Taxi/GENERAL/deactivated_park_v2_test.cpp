#include <gtest/gtest.h>

#include <filters/infrastructure/fetch_park_activation/fetch_park_activation.hpp>
#include "deactivated_park_v2.hpp"

#include <userver/rcu/rcu.hpp>

namespace cf = candidates::filters;
namespace cfi = cf::infrastructure;

const cf::FilterInfo kEmptyInfo;

TEST(DeactivatedParkV2Filter, Active) {
  parks_activation::models::Park park;
  park.deactivated = false;
  cf::Context context;
  cfi::FetchParkActivation::Set(context, park);
  rcu::Variable<cfi::ParkIds> ignore_parks_ids{};
  auto ignore_parks_ids_ptr = ignore_parks_ids.Read();
  cfi::DeactivatedParkV2 filter{kEmptyInfo, std::move(ignore_parks_ids_ptr)};
  ASSERT_EQ(cf::Result::kAllow, filter.Process({}, context));
}

TEST(DeactivatedParkV2Filter, NotActive) {
  parks_activation::models::Park park;
  park.deactivated = true;
  cf::Context context;
  cfi::FetchParkActivation::Set(context, park);
  rcu::Variable<cfi::ParkIds> ignore_parks_ids{};
  auto ignore_parks_ids_ptr = ignore_parks_ids.Read();
  cfi::DeactivatedParkV2 filter{kEmptyInfo, std::move(ignore_parks_ids_ptr)};
  ASSERT_EQ(cf::Result::kDisallow, filter.Process({}, context));
}

TEST(DeactivatedParkV2Filter, NotActiveButInEatsCourierServiceMapping) {
  parks_activation::models::Park park;
  park.deactivated = true;
  cf::Context context;
  cfi::FetchParkActivation::Set(context, park);

  // Courier
  const std::string courier_service_park_id{"courierserviceparkid"};
  const candidates::GeoMember courier_member{{},
                                             "courierserviceparkid_driverid"};

  {
    rcu::Variable<cfi::ParkIds> ignore_parks_ids(
        cfi::ParkIds{courier_service_park_id});
    auto ignore_parks_ids_ptr = ignore_parks_ids.Read();
    cfi::DeactivatedParkV2 filter{kEmptyInfo, std::move(ignore_parks_ids_ptr)};
    ASSERT_EQ(cf::Result::kAllow, filter.Process(courier_member, context));
  }

  {
    rcu::Variable<cfi::ParkIds> ignore_parks_ids(
        cfi::ParkIds{"not_courier_service_park_id"});
    auto ignore_parks_ids_ptr = ignore_parks_ids.Read();
    cfi::DeactivatedParkV2 filter{kEmptyInfo, std::move(ignore_parks_ids_ptr)};
    ASSERT_EQ(cf::Result::kDisallow, filter.Process(courier_member, context));
  }
}
