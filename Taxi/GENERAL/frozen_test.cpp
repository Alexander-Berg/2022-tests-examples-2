#include <gtest/gtest.h>

#include <filters/infrastructure/fetch_car/fetch_car.hpp>
#include <filters/infrastructure/fetch_unique_driver/fetch_unique_driver.hpp>
#include "frozen.hpp"

namespace {

const candidates::filters::FilterInfo kEmptyInfo;

void AddToContext(models::Car&& car, candidates::filters::Context& context) {
  candidates::filters::infrastructure::FetchCar::Set(
      context, std::make_shared<const models::Car>(std::move(car)));
}

void AddToContext(models::UniqueDriver&& driver,
                  candidates::filters::Context& context) {
  candidates::filters::infrastructure::FetchUniqueDriver::Set(
      context, std::make_shared<models::UniqueDriver>(std::move(driver)));
}

}  // namespace

TEST(Frozen, NoProfile) {
  auto frozen = std::make_shared<models::FrozenDrivers>();
  candidates::filters::infrastructure::Frozen filter(kEmptyInfo, frozen);
  candidates::GeoMember member;
  candidates::filters::Context context;
  EXPECT_ANY_THROW(filter.Process(member, context));
}

TEST(Frozen, NoUnique) {
  auto frozen = std::make_shared<models::FrozenDrivers>();
  candidates::filters::infrastructure::Frozen filter(kEmptyInfo, frozen);
  candidates::GeoMember member;
  candidates::filters::Context context;

  models::Car car;
  car.number = "number";
  AddToContext(std::move(car), context);

  EXPECT_ANY_THROW(filter.Process(member, context));
}

TEST(Frozen, Sample) {
  auto frozen = std::make_shared<models::FrozenDrivers>();
  candidates::filters::infrastructure::Frozen filter(kEmptyInfo, frozen);
  candidates::GeoMember member;
  candidates::filters::Context context;

  models::Car car;
  car.number = "number";
  AddToContext(std::move(car), context);

  models::UniqueDriver unique_driver;
  unique_driver.id = "id";
  unique_driver.licenses_ids.push_back("lic");
  AddToContext(std::move(unique_driver), context);

  EXPECT_EQ(filter.Process(member, context),
            candidates::filters::Result::kAllow);

  frozen->AddUniqueDriverId("id");
  frozen->AddCarId("number");
  EXPECT_EQ(filter.Process(member, context),
            candidates::filters::Result::kDisallow);
}
