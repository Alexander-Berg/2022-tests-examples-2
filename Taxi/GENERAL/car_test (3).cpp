#include <gtest/gtest.h>

#include "car.hpp"

class CarNumber
    : public ::testing::TestWithParam<std::pair<std::string, std::string>> {};

TEST_P(CarNumber, Normalization) {
  const auto& [number, normalized] = GetParam();
  ASSERT_EQ(models::NormalizeCarNumber(number), normalized);
}

INSTANTIATE_TEST_SUITE_P(
    CarNumber, CarNumber,
    ::testing::Values(std::make_pair("12AB7843ХЕТ", "12АВ7843ХЕТ"),        //
                      std::make_pair("abcehkmoptxy", "АВСЕНКМОРТХУ"),      //
                      std::make_pair("авсенкмортху", "АВСЕНКМОРТХУ"),      //
                      std::make_pair("#$123<>?AbcАвС", "#$123<>?АВСАВС"),  //
                      std::make_pair("12   AB78 43ХЕТ ", "12АВ7843ХЕТ")    //
                      ));
