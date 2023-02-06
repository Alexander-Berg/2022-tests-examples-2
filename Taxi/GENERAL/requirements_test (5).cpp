#include <gtest/gtest.h>

#include "requirements.hpp"

#include <filters/infrastructure/fetch_car/fetch_car.hpp>
#include <filters/infrastructure/fetch_car/models/car_requirements.hpp>

namespace cf = candidates::filters;
namespace cfi = cf::infrastructure;

const cf::FilterInfo kEmptyInfo;

TEST(RequirementsFilter, Sample) {
  models::Car car;
  car.car_id = "car_id";
  car.park_id = "dbid";
  car.allowed_requirements = {
      {"ski", true},
      {"bicycle", short(2)},
  };
  cf::Context context;
  cfi::FetchCar::Set(context,
                     std::make_shared<const models::Car>(std::move(car)));

  candidates::GeoMember driver;

  {
    cfi::Requirements filter{kEmptyInfo,
                             {{"bicycle", short(1)}, {"ski", true}}};
    ASSERT_EQ(cf::Result::kAllow, filter.Process(driver, context));
  }

  {
    cfi::Requirements filter{kEmptyInfo,
                             {{"bicycle", short(2)}, {"ski", false}}};
    ASSERT_EQ(cf::Result::kAllow, filter.Process(driver, context));
  }

  {
    cfi::Requirements filter{kEmptyInfo,
                             {{"bicycle", short(3)}, {"ski", true}}};
    ASSERT_EQ(cf::Result::kDisallow, filter.Process(driver, context));
  }
}
