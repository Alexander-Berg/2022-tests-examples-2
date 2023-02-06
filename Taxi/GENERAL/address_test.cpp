#include "address.hpp"

#include <gtest/gtest.h>

using models::address::ToYandexAddress;
using models::address::ToYandexAddressArray;

TEST(ToYandexAddress, One) {
  Json::Value addr_obj(Json::objectValue);

  ToYandexAddress(addr_obj);
  EXPECT_TRUE(addr_obj["Street"].isNull());
  EXPECT_TRUE(addr_obj["House"].isNull());

  addr_obj["Street"] = "street";
  ToYandexAddress(addr_obj);
  EXPECT_STREQ("street", addr_obj["Street"].asCString());
  EXPECT_TRUE(addr_obj["House"].isNull());

  addr_obj["Street"] = "street";
  addr_obj["House"] = "house";
  ToYandexAddress(addr_obj);
  EXPECT_STREQ("street, house", addr_obj["Street"].asCString());
  EXPECT_TRUE(addr_obj["House"].isNull());
}

TEST(ToYandexAddress, DoNotAddNullValue) {
  Json::Value address(Json::objectValue);
  const std::string name = "address_to";
  ToYandexAddress(address, name);
  EXPECT_FALSE(address.isMember(name));
}

TEST(ToYandexAddress, DoNotAllowNullValue) {
  Json::Value address(Json::objectValue);
  const std::string name = "address_to";
  address[name] = Json::Value(Json::nullValue);
  EXPECT_THROW(ToYandexAddress(address, name), std::runtime_error);
}

TEST(ToYandexAddressArray, DoNotAddNullValue) {
  Json::Value addresses(Json::objectValue);
  const std::string name = "route_points";
  ToYandexAddressArray(addresses, name);
  EXPECT_FALSE(addresses.isMember(name));
}

TEST(ToYandexAddressArray, DoNotAllowNullValue) {
  Json::Value addresses(Json::objectValue);
  const std::string name = "route_points";
  addresses[name] = Json::Value(Json::nullValue);
  EXPECT_THROW(ToYandexAddressArray(addresses, name), std::runtime_error);
}
