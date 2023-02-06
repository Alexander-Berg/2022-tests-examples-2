#include <gtest/gtest.h>
#include <mongo/names/db_cars/cars.hpp>

#include "car.hpp"

namespace names = utils::mongo::db::cars;

void AppendOptions(mongo::BSONObjBuilder& builder, const std::string& member,
                   const std::initializer_list<std::string> options) {
  if (options.size() > 0) {
    mongo::BSONObjBuilder options_builder;
    for (const auto& option : options) {
      options_builder.append(option, true);
    }
    builder.append(member, options_builder.obj());
  }
}

models::Car CreateCar(const std::string& id, const std::string& park_id,
                      const std::initializer_list<std::string> categories = {},
                      const std::initializer_list<std::string> amenities = {}) {
  mongo::BSONObjBuilder builder;
  builder.append(names::kCarId, id);
  builder.append(names::kParkId, park_id);
  AppendOptions(builder, names::kCategory, categories);
  AppendOptions(builder, names::kService, amenities);

  models::Car result;
  result.raw_data = builder.obj();
  return result;
}

template <typename T, typename Container>
void CheckIndicesMap(const utils::IndicesMap<T>& map, const Container& values,
                     const utils::Index index) {
  for (const auto& value : values) {
    const auto& map_key = static_cast<T>(value);
    for (const auto& [key, indices] : map) {
      if (key == map_key) {
        ASSERT_TRUE(indices.find(index) != indices.end());
      } else {
        ASSERT_TRUE(indices.find(index) == indices.end());
      }
    }
  }
}

void CheckCarInPark(const models::ParkCars& park_cars, const models::Car& car) {
  const auto& it = park_cars.id_map.find(car.GetId());
  ASSERT_TRUE(it != park_cars.id_map.end());
  const auto index = it->second;
  const auto& park_car = park_cars.data.at(index);
  ASSERT_EQ(car.GetId(), park_car.GetId());
  ASSERT_EQ(car.GetParkId(), park_car.GetParkId());
  ASSERT_EQ(car.GetAmenities(), park_car.GetAmenities());
  ASSERT_EQ(car.GetCategories(), park_car.GetCategories());
  CheckIndicesMap(park_cars.amenity_map, car.GetAmenities(), index);
  CheckIndicesMap(park_cars.category_map, car.GetCategories(), index);
}

TEST(TestUpsertCar, UpdateCar) {
  models::ParkCars cache;

  const std::string kId = "anton";
  const std::string kParkId = "mospark";
  const std::string kC1 = "c1";
  const std::string kC2 = "c2";
  const std::string kA1 = "a1";

  const auto& car_v1 = CreateCar(kId, kParkId, {kC1});

  UpsertCar(cache, models::Car{car_v1});
  ASSERT_EQ(1u, cache.data.size());
  CheckCarInPark(cache, car_v1);

  UpsertCar(cache, models::Car{car_v1});
  ASSERT_EQ(1u, cache.data.size());
  CheckCarInPark(cache, car_v1);

  const auto& car_v2 = CreateCar(kId, kParkId, {kC2});

  UpsertCar(cache, models::Car{car_v2});
  ASSERT_EQ(1u, cache.data.size());
  CheckCarInPark(cache, car_v2);

  const auto& car_v3 = CreateCar(kId, kParkId, {kC1}, {kA1});

  UpsertCar(cache, models::Car{car_v3});
  ASSERT_EQ(1u, cache.data.size());
  CheckCarInPark(cache, car_v3);

  const auto& car_v4 = CreateCar(kId, kParkId, {}, {kA1});

  UpsertCar(cache, models::Car{car_v4});
  ASSERT_EQ(1u, cache.data.size());
  CheckCarInPark(cache, car_v4);
}
