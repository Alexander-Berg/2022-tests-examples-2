#include <gtest/gtest.h>

#include <sstream>

#include <utils/scope_guard.hpp>

#include <caches/cars.hpp>

namespace caches {

namespace {

models::Cars BuildTestData() {
  mongo::BSONObj c1;
  mongo::BSONObj c2;
  {
    mongo::BSONObjBuilder builder;
    builder.append("park_id", "p1");
    builder.append("car_id", "c1");
    c1 = builder.obj();
  }
  {
    mongo::BSONObjBuilder builder;
    builder.append("park_id", "p1");
    builder.append("car_id", "c2");
    c2 = builder.obj();
  }

  models::Cars result;
  std::unordered_set<std::string> seen_park_ids;
  TimeStorage ts{"test-ts"};
  LogExtra log_extra;
  caches::details::AppendCar(result, seen_park_ids, c1, Cars::UpdateType::Clean,
                             ts, log_extra);
  caches::details::AppendCar(result, seen_park_ids, c2, Cars::UpdateType::Clean,
                             ts, log_extra);

  return result;
}

}  // namespace

TEST(Cars, DumpTest) {
  auto data = BuildTestData();
  TimeStorage ts{"test-ts"};
  LogExtra log_extra;
  utils::AsyncStatus status;

  std::stringstream os;
  details::SaveToStreamImpl(data, os, status, ts, log_extra);

  models::Cars loaded;
  std::istringstream is(os.str());
  details::ReadFromStreamImpl(loaded, is, status, ts, log_extra);

  ASSERT_EQ(data.size(), static_cast<size_t>(1));
  ASSERT_EQ(data.size(), loaded.size());
  ASSERT_TRUE(data.count("p1") == 1);
  ASSERT_TRUE(loaded.count("p1") == 1);

  const auto& cars1 = data["p1"]->data;
  const auto& cars2 = loaded["p1"]->data;
  ASSERT_EQ(cars1.size(), static_cast<size_t>(2));
  ASSERT_EQ(cars1.size(), cars2.size());
  ASSERT_EQ(cars1[0].GetId(), cars1[0].GetId());
  ASSERT_EQ(cars1[1].GetId(), cars1[1].GetId());
}

}  // namespace caches
