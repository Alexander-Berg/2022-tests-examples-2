#include <gtest/gtest.h>

#include <defs/definitions.hpp>

#include <models/address_type.hpp>

namespace pm = personal::models;

namespace {
struct TestCase {
  handlers::Address as_address;
  std::string as_string;
};
}  // namespace

TestCase CountryOnlyCase() {
  TestCase result;
  result.as_address.extra["country"] = "Russia";

  result.as_string = "{\"country\":\"Russia\"}";
  return result;
}

TestCase CountryAndCityCase() {
  TestCase result;
  result.as_address.extra["country"] = "Russia";
  result.as_address.extra["city"] = "Москва";

  result.as_string = "{\"city\":\"Москва\",\"country\":\"Russia\"}";
  return result;
}

const std::vector<TestCase> cases = {
    CountryOnlyCase(),
    CountryAndCityCase(),
};

TEST(AddressTypeTest, AddressToStringTest) {
  for (const auto& address : cases) {
    auto output = pm::AddressToString(address.as_address);
    EXPECT_EQ(output, address.as_string);
  }
}

TEST(AddressTypeTest, AddressFromStringTest) {
  for (const auto& address : cases) {
    auto output = pm::AddressFromString(address.as_string);
    EXPECT_EQ(output, address.as_address);
  }
}
