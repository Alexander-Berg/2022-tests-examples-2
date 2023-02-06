#include <gtest/gtest.h>

#include <filters/infrastructure/fetch_car/fetch_car.hpp>
#include "cargo_limits.hpp"

namespace cf = candidates::filters;
namespace cfi = cf::infrastructure;
namespace cfp = cf::product;

const cf::FilterInfo kEmptyInfo;

TEST(CargoLimitsFilter, Sample) {
  models::Car car;
  car.car_id = "car_id";
  car.park_id = "dbid";
  car.allowed_requirements = {};
  car.cargo_limits = {100, 100, 100, 100};
  cf::Context context;
  cfi::FetchCar::Set(context,
                     std::make_shared<const models::Car>(std::move(car)));

  candidates::GeoMember driver;

  {
    models::cargo_limits::ClientLimits cargo_requirement{
        {50, 150}, {50, 150}, {50, 150}, {50, 150}};
    cfp::CargoLimits filter{kEmptyInfo, std::move(cargo_requirement)};
    ASSERT_EQ(cf::Result::kAllow, filter.Process(driver, context));
  }

  {
    models::cargo_limits::ClientLimits cargo_requirement{
        {50, 150}, {50, 150}, {10, 20}, {50, 150}};
    cfp::CargoLimits filter{kEmptyInfo, std::move(cargo_requirement)};
    ASSERT_EQ(cf::Result::kDisallow, filter.Process(driver, context));
  }
}
