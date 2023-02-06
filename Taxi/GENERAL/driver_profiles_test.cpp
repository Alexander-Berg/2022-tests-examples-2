#include <gtest/gtest.h>

#include <models/parks/driver_profiles/driver_profiles.hpp>
#include <utils/json_serializers.hpp>

namespace models {
namespace parks {
namespace driver_profiles {

DriverProfile TestProfile(const std::string& id, const std::string& name) {
  DriverProfile profile;

  profile.park = Json::Value(Json::objectValue);
  profile.park.get()["id"] = Json::Value("af43ed");
  profile.park.get()["name"] = Json::Value("park");

  profile.driver = Json::Value(Json::objectValue);
  profile.driver.get()["id"] = Json::Value("driver#" + id);
  profile.driver.get()["name"] = Json::Value(name);

  profile.accounts = std::vector<Json::Value>{Json::Value(Json::objectValue)};
  profile.accounts.get().back()["id"] = Json::Value("account#" + id);
  profile.accounts.get().back()["type"] = Json::Value("current");
  profile.accounts.get().back()["balance"] = Json::Value("13.7269");
  profile.accounts.get().back()["currency"] = Json::Value("RUB");

  return profile;
}

DriverProfiles TestProfiles() {
  DriverProfiles driver_profiles;
  driver_profiles.has_more = false;
  driver_profiles.profiles.emplace_back(TestProfile("da23ff", "Anton"));
  driver_profiles.profiles.emplace_back(TestProfile("bbed76", "Todua"));
  return driver_profiles;
}

void AssertEq(const Json::Value& expected, const Json::Value& actual) {
  ASSERT_EQ(0, expected.compare(actual));
}

template <typename T>
void AssertEq(const std::vector<T>& expected, const std::vector<T>& actual) {
  ASSERT_EQ(expected.size(), actual.size());
  for (size_t i = 0; i < expected.size(); i++) {
    AssertEq(expected[i], actual[i]);
  }
}

template <typename T>
void AssertEq(const boost::optional<T>& expected,
              const boost::optional<T>& actual) {
  ASSERT_EQ(static_cast<bool>(expected), static_cast<bool>(actual));
  if (expected) {
    ASSERT_EQ(expected.get(), actual.get());
  }
}

void AssertEq(const DriverProfile& expected, const DriverProfile& actual) {
  AssertEq(expected.park, actual.park);
  AssertEq(expected.driver, actual.driver);
  AssertEq(expected.accounts, actual.accounts);
}

TEST(DriverProfiles, Serialization) {
  const auto& expected = TestProfiles();
  const auto& json_text = serializers::Serialize(expected);
  const auto& actual = serializers::Deserialize<DriverProfiles>(json_text);
  AssertEq(expected.has_more, actual.has_more);
  AssertEq(expected.profiles, actual.profiles);
}

}  // namespace driver_profiles
}  // namespace parks
}  // namespace models
