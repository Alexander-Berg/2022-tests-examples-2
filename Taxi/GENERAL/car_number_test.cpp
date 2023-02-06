#include <gtest/gtest.h>

#include <filters/infrastructure/fetch_car/fetch_car.hpp>
#include "car_number.hpp"

namespace cf = candidates::filters;
namespace cfi = cf::infrastructure;

static cf::FilterInfo kEmptyInfo;

class CarNumberTest : public testing::Test {
 protected:
  void SetUp() override {
    cars = std::make_shared<models::CarMap>(
        [](const std::string&) { return models::CarPtr{}; });

    {
      auto car = std::make_shared<models::Car>();
      car->number = "car1";
      car->car_id = "car_id1";
      cars->Insert(car->car_id, models::CarPtr(car));
    }

    {
      auto car = std::make_shared<models::Car>();
      car->car_id = "car_id2";
      cars->Insert(car->car_id, models::CarPtr(car));
    }

    {
      auto car = std::make_shared<models::Car>();
      car->number = "car3";
      car->car_id = "car_id3";
      cars->Insert(car->car_id, models::CarPtr(car));
    }
  }

  cf::Context& GetContext(const std::string& driver_id) {
    context.ClearData();
    std::string car_id = std::string("car_id") + driver_id.back();
    cfi::FetchCar::Set(context, cars->Find(car_id, models::CarMap::kCache));
    return context;
  }

  std::shared_ptr<models::CarMap> cars;
  cf::Context context;
};

TEST_F(CarNumberTest, Basic) {
  cf::infrastructure::CarNumber filter(kEmptyInfo, {"car1", "car2"});
  EXPECT_EQ(filter.Process({}, GetContext("dbid_uuid1")),
            cf::Result::kDisallow);
  EXPECT_EQ(filter.Process({}, GetContext("dbid_uuid2")), cf::Result::kAllow);
  EXPECT_EQ(filter.Process({}, GetContext("dbid_uuid3")), cf::Result::kAllow);
}
