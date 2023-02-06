#include <gtest/gtest.h>

#include <models/classes.hpp>
#include <userver/utest/utest.hpp>

#include <filters/infrastructure/fetch_car/fetch_car.hpp>
#include <filters/infrastructure/fetch_categories/fetch_categories.hpp>
#include <filters/infrastructure/fetch_categories/models/categories.hpp>
#include <filters/infrastructure/fetch_driver/fetch_driver.hpp>

namespace {

using candidates::GeoMember;
using candidates::filters::Context;
using candidates::filters::Result;
using candidates::filters::infrastructure::FetchCar;
using candidates::filters::infrastructure::FetchCategories;
using candidates::filters::infrastructure::FetchDriver;

const candidates::filters::FilterInfo kEmptyInfo;

}  // namespace

UTEST(FetchCategories, Sample) {
  Context context;
  auto driver = std::make_shared<models::Driver>();
  driver->car_id = "carid";
  driver->id = {"dbid", "uuid"};
  FetchDriver::Set(context, driver);
  auto car = std::make_shared<models::Car>();
  FetchCar::Set(context, car);
  auto categories_cache = std::make_shared<models::Categories>();
  FetchCategories filter(kEmptyInfo, categories_cache);
  EXPECT_EQ(filter.Process({}, context), Result::kAllow);
  EXPECT_NO_THROW(FetchCategories::Get(context));
}

UTEST(FetchCategories, AvailableCategories) {
  Context context;
  auto driver = std::make_shared<models::Driver>();
  driver->car_id = "carid";
  driver->id = {"dbid", "uuid"};
  FetchDriver::Set(context, driver);
  auto car = std::make_shared<models::Car>();
  FetchCar::Set(context, car);
  auto categories_cache = std::make_shared<models::Categories>();

  auto& park = categories_cache->parks["dbid"].GetForWrite();
  park.available_in_park = {"econom", "business"};
  park.cars_classes_in_park.GetForWrite()["carid"] = {"econom"};

  FetchCategories filter(kEmptyInfo, categories_cache);
  EXPECT_EQ(filter.Process({}, context), Result::kAllow);
  auto const& categories = FetchCategories::Get(context);
  EXPECT_EQ(categories.size(), 1);
  const auto& names = categories.GetNames();
  EXPECT_NE(std::find(names.begin(), names.end(), "econom"), names.end());
}

UTEST(FetchCategories, ParkOnly) {
  Context context;
  auto driver = std::make_shared<models::Driver>();
  driver->car_id = "carid";
  driver->id = {"dbid", "uuid"};
  FetchDriver::Set(context, driver);
  auto car = std::make_shared<models::Car>();
  FetchCar::Set(context, car);
  auto categories_cache = std::make_shared<models::Categories>();

  auto& park = categories_cache->parks["dbid"].GetForWrite();
  park.available_in_park = {"econom"};

  FetchCategories filter(kEmptyInfo, categories_cache);
  EXPECT_EQ(filter.Process({}, context), Result::kAllow);
  auto const& categories = FetchCategories::Get(context);
  EXPECT_EQ(categories.size(), 0);
}

UTEST(FetchCategories, CarOnly) {
  Context context;
  auto driver = std::make_shared<models::Driver>();
  driver->car_id = "carid";
  driver->id = {"dbid", "uuid"};
  FetchDriver::Set(context, driver);
  auto car = std::make_shared<models::Car>();
  FetchCar::Set(context, car);
  auto categories_cache = std::make_shared<models::Categories>();

  auto& park = categories_cache->parks["dbid"].GetForWrite();
  park.cars_classes_in_park.GetForWrite()["carid"] = {"econom"};

  FetchCategories filter(kEmptyInfo, categories_cache);
  EXPECT_EQ(filter.Process({}, context), Result::kAllow);
  auto const& categories = FetchCategories::Get(context);
  EXPECT_GT(categories.size(), 0);
}

UTEST(FetchCategories, RestrictedByDriver) {
  Context context;
  auto driver = std::make_shared<models::Driver>();
  driver->car_id = "carid";
  driver->id = {"dbid", "uuid"};
  FetchDriver::Set(context, driver);
  auto car = std::make_shared<models::Car>();
  FetchCar::Set(context, car);
  auto categories_cache = std::make_shared<models::Categories>();

  auto& park = categories_cache->parks["dbid"].GetForWrite();
  park.available_in_park = {"business", "econom"};
  park.cars_classes_in_park.GetForWrite()["carid"] = {"econom"};
  park.blocked_by_driver.GetForWrite()["uuid"] = {"econom"};

  FetchCategories filter(kEmptyInfo, categories_cache);
  EXPECT_EQ(filter.Process({}, context), Result::kAllow);
  auto const& categories = FetchCategories::Get(context);
  EXPECT_EQ(categories.size(), 0);
}

UTEST(FetchCategories, OverridenParkRestrictableCategories) {
  Context context;
  auto driver = std::make_shared<models::Driver>();
  driver->car_id = "carid";
  driver->id = {"dbid", "uuid"};
  FetchDriver::Set(context, driver);
  auto car = std::make_shared<models::Car>();
  FetchCar::Set(context, car);
  auto categories_cache = std::make_shared<models::Categories>();

  auto& park = categories_cache->parks["dbid"].GetForWrite();
  park.available_in_park = {"econom"};
  park.cars_classes_in_park.GetForWrite()["carid"] = {"business", "econom"};
  park.blocked_by_driver.GetForWrite()["uuid"] = {"business", "econom"};

  models::Classes overriden_park_restrictions{"business"};
  FetchCategories filter(kEmptyInfo, categories_cache,
                         overriden_park_restrictions);
  EXPECT_EQ(filter.Process({}, context), Result::kAllow);
  auto const& categories = FetchCategories::Get(context);
  EXPECT_EQ(categories.size(), 0);
}

UTEST(FetchCategories, ChildTariff) {
  Context context;
  auto driver = std::make_shared<models::Driver>();
  driver->car_id = "carid";
  driver->id = {"dbid", "uuid"};
  FetchDriver::Set(context, driver);
  auto car = std::make_shared<models::Car>();
  car->chairs_info.boosters = 1;
  car->chairs_info.confirmed_boosters = 1;
  FetchCar::Set(context, car);
  auto categories_cache = std::make_shared<models::Categories>();

  auto& park = categories_cache->parks["dbid"].GetForWrite();
  park.available_in_park = {};
  park.cars_classes_in_park.GetForWrite()["carid"] = {};
  park.blocked_by_driver.GetForWrite()["uuid"] = {};

  FetchCategories filter(kEmptyInfo, categories_cache);
  EXPECT_EQ(filter.Process({}, context), Result::kAllow);
  auto const& categories = FetchCategories::Get(context);
  EXPECT_EQ(categories.size(), 1);
  const auto& names = categories.GetNames();
  EXPECT_EQ(names, std::vector<std::string>{"child_tariff"});
}

UTEST(FetchCategories, ChildTariffDisabled) {
  Context context;
  auto driver = std::make_shared<models::Driver>();
  driver->car_id = "carid";
  driver->id = {"dbid", "uuid"};
  FetchDriver::Set(context, driver);
  auto car = std::make_shared<models::Car>();
  car->chairs_info.boosters = 1;
  car->chairs_info.confirmed_boosters = 1;
  FetchCar::Set(context, car);
  auto categories_cache = std::make_shared<models::Categories>();

  auto& park = categories_cache->parks["dbid"].GetForWrite();
  park.available_in_park = {"child_tariff"};
  park.cars_classes_in_park.GetForWrite()["carid"] = {"econom"};
  park.blocked_by_driver.GetForWrite()["uuid"] = {"child_tariff"};

  FetchCategories filter(kEmptyInfo, categories_cache);
  EXPECT_EQ(filter.Process({}, context), Result::kAllow);
  auto const& categories = FetchCategories::Get(context);
  EXPECT_EQ(categories.size(), 1);
  const auto& names = categories.GetNames();
  EXPECT_EQ(names, std::vector<std::string>{"econom"});
}
