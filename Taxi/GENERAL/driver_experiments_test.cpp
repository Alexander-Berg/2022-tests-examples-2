#include <gtest/gtest.h>

#include "driver_experiments.hpp"

class DriverRequiredVersionParams
    : public ::testing::Test,
      public ::testing::WithParamInterface<std::tuple<bool, std::string>> {};

TEST_P(DriverRequiredVersionParams, One) {
  static const TaximeterVersion version("8.8");

  const bool check = std::get<0>(GetParam());
  const experiments::DriverRequiredVersion expected_url{
      std::get<1>(GetParam())};

  ASSERT_EQ(check, expected_url.Check(version));
}

INSTANTIATE_TEST_CASE_P(
    TestRequiredGeneration, DriverRequiredVersionParams,
    ::testing::Values(
        std::make_tuple(true, ">8.7"), std::make_tuple(false, ">8.8"),
        std::make_tuple(true, ">=8.8"), std::make_tuple(false, ">=8.9"),
        std::make_tuple(true, "<8.9"), std::make_tuple(false, "<8.8"),
        std::make_tuple(true, "<=8.8"), std::make_tuple(false, "<=8.7"),
        std::make_tuple(true, "=8.8"), std::make_tuple(true, "==8.8"),
        std::make_tuple(false, "=8.9"), std::make_tuple(false, "==8.7"),
        std::make_tuple(true, "  = 8.8  "),
        std::make_tuple(true, "  = 8.8 (0) "),
        std::make_tuple(true, "> 8.7 (14) ")), );
