#include <virtual-tariffs/utils/from_string.hpp>

#include <gtest/gtest.h>

#include <string>

using namespace virtual_tariffs::utils;

TEST(VirtualTariffs, FromString) {
  EXPECT_THROW(FromString<std::string::value_type>("4.99"),
               std::invalid_argument);
  EXPECT_EQ('4', FromString<std::string::value_type>("4"));
  EXPECT_EQ(1, FromString<int>("1.99"));
}
