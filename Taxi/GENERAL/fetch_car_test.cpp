#include <userver/utest/utest.hpp>

#include <userver/engine/sleep.hpp>

#include <filters/infrastructure/fetch_driver/fetch_driver.hpp>
#include "fetch_car.hpp"

namespace filters = candidates::filters;

namespace {

models::CarPtr DummyLoader(const std::string&) {
  engine::SleepFor(std::chrono::milliseconds(20));
  return {};
}

const filters::FilterInfo kEmptyInfo;

}  // namespace

UTEST_MT(FetchCarProfileTest, Sample, 2) {
  auto car = std::make_shared<models::Car>();
  auto cars = std::make_shared<models::CarMap>(&DummyLoader);
  cars->Insert("dbid_car_id", car);

  filters::Context context;
  models::Driver driver;
  driver.park_id_car_id = "dbid_car_id";
  filters::infrastructure::FetchDriver::Set(
      context, std::make_shared<const models::Driver>(driver));

  filters::infrastructure::FetchCar filter(kEmptyInfo, cars);
  candidates::GeoMember member{{}, "dbid_uuid"};

  EXPECT_EQ(filters::Result::kAllow, filter.Process(member, context));
  EXPECT_NO_THROW(filters::infrastructure::FetchCar::Get(context));
}
