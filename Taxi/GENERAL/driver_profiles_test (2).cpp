#include <gtest/gtest.h>

#include <sstream>
#include <vector>

#include <utils/scope_guard.hpp>

#include <caches/driver_profiles.hpp>
#include <models/driver_profile.hpp>
#include <utils/helpers/params.hpp>

namespace caches {

namespace {

models::DriverProfiles BuildTestData() {
  mongo::BSONObj d1;
  mongo::BSONObj d2;
  {
    mongo::BSONObjBuilder builder;
    builder.append("park_id", "p1");
    builder.append("driver_id", "d1");
    d1 = builder.obj();
  }
  {
    mongo::BSONObjBuilder builder;
    builder.append("park_id", "p1");
    builder.append("driver_id", "d2");
    d2 = builder.obj();
  }

  models::DriverProfiles result;
  std::unordered_set<std::string> seen_park_ids;
  TimeStorage ts{"test-ts"};
  LogExtra log_extra;
  caches::details::AppendDriver(result, seen_park_ids, d1,
                                DriverProfiles::UpdateType::Clean, ts,
                                log_extra);
  caches::details::AppendDriver(result, seen_park_ids, d2,
                                DriverProfiles::UpdateType::Clean, ts,
                                log_extra);

  result.phone_pd_ids = {{"1", "1"}, {"2", "2"}};

  return result;
}

}  // namespace

TEST(DriverProfiles, DumpTest) {
  auto data = BuildTestData();
  TimeStorage ts{"test-ts"};
  LogExtra log_extra;
  utils::AsyncStatus status;

  std::stringstream os;
  details::SaveToStreamImpl(data, os, status, ts, log_extra);

  models::DriverProfiles loaded;
  models::PdMapType pd_phones_loaded;
  std::istringstream is(os.str());
  details::ReadFromStreamImpl(loaded, is, status, ts, log_extra);

  ASSERT_EQ(data.profiles.size(), static_cast<size_t>(1));
  ASSERT_EQ(data.profiles.size(), loaded.profiles.size());
  ASSERT_TRUE(data.profiles.count("p1") == 1);
  ASSERT_TRUE(loaded.profiles.count("p1") == 1);

  const auto& drivers1 = data.profiles["p1"]->data;
  const auto& drivers2 = loaded.profiles["p1"]->data;
  ASSERT_EQ(drivers1.size(), static_cast<size_t>(2));
  ASSERT_EQ(drivers1.size(), drivers2.size());
  ASSERT_EQ(drivers1[0].GetId(), drivers2[0].GetId());
  ASSERT_EQ(drivers1[1].GetId(), drivers2[1].GetId());

  ASSERT_EQ(data.phone_pd_ids, loaded.phone_pd_ids);
}

TEST(DriverProfiles, SubstitutePhones) {
  std::unordered_set<std::string> phones0{"1", "2"};
  std::unordered_set<std::string> phones1{};
  std::unordered_set<std::string> phones2{"3", "4"};

  mongo::BSONObjBuilder inner_builder;
  inner_builder.append("inner_field", "some_value");
  inner_builder.append("inner_array",
                       std::vector<std::string>{"i1", "i2", "i3"});

  mongo::BSONObjBuilder builder;
  builder.append("park_id", "p1");
  builder.append("driver_id", "d1");
  builder.append("some_array", std::vector<std::string>{"a1", "a2"});
  builder.append("phones",
                 std::vector<std::string>{phones0.begin(), phones0.end()});
  builder.append("inner", inner_builder.obj());
  mongo::BSONObj doc = builder.obj();

  auto profile = models::DriverProfile{doc};
  auto phones = profile.GetPhones();
  auto phones_set =
      std::unordered_set<std::string>(phones.begin(), phones.end());
  ASSERT_EQ(phones_set, phones0);

  doc = internal::SubstitutePhones(doc, std::move(phones1));

  profile = models::DriverProfile{doc};
  phones = profile.GetPhones();
  phones_set = std::unordered_set<std::string>(phones.begin(), phones.end());
  ASSERT_EQ(phones_set, phones1);

  doc = internal::SubstitutePhones(doc, std::move(phones2));

  profile = models::DriverProfile{doc};
  phones = profile.GetPhones();
  phones_set = std::unordered_set<std::string>(phones.begin(), phones.end());
  ASSERT_EQ(phones_set, phones2);

  using utils::helpers::FetchMember;

  std::string val;
  std::vector<std::string> arr_val;

  FetchMember(val, doc, "driver_id");
  ASSERT_EQ(val, "d1");

  FetchMember(arr_val, doc, "some_array");
  ASSERT_EQ(arr_val.size(), 2u);
  ASSERT_EQ(arr_val[0], "a1");
  ASSERT_EQ(arr_val[1], "a2");

  mongo::BSONObj inner = doc.getObjectField("inner");

  FetchMember(val, inner, "inner_field");
  ASSERT_EQ(val, "some_value");

  arr_val.clear();

  FetchMember(arr_val, inner, "inner_array");
  ASSERT_EQ(arr_val.size(), 3u);
  ASSERT_EQ(arr_val[0], "i1");
  ASSERT_EQ(arr_val[1], "i2");
  ASSERT_EQ(arr_val[2], "i3");
}

}  // namespace caches
