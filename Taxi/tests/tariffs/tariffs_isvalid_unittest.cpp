#include <gtest/gtest.h>
#include <models/tariff_settings.hpp>
#include <tariffs/tariffs_builder.hpp>

#include "mongo/mongo.hpp"
#include "utils/json_compare.hpp"
#include "utils/jsonfixtures.hpp"
#include "utils/translation_mock.hpp"
#include "views/tariffs/tariffs.hpp"

class TariffIsValidTest : public ::testing::Test {
  tariff::Tariff LoadTariffFromFile(const std::string& tariff_file_name) {
    auto tariff_bson = JSONFixtures::GetFixtureBSON(tariff_file_name);
    const auto t = tariff_bson[0].Obj();
    return tariff::ParseTariff(t);
  }

  virtual void SetUp() override {
    tariff_ok_ = LoadTariffFromFile("interval_check/tariff_ok_interval.json");
    tariff_inversed_interval1_ = LoadTariffFromFile(
        "interval_check/tariff_with_reversed_interval1.json");
    tariff_inversed_interval2_ = LoadTariffFromFile(
        "interval_check/tariff_with_reversed_interval2.json");
  }

 protected:
  tariff::Tariff tariff_ok_;
  tariff::Tariff tariff_inversed_interval1_;
  tariff::Tariff tariff_inversed_interval2_;
};

TEST_F(TariffIsValidTest, TariffIsValid4StrightIntervals) {
  ASSERT_TRUE(tariff_ok_.IsValid(LogExtra{}));
}

TEST_F(TariffIsValidTest, TariffIsNotValid4reversedInterval1) {
  ASSERT_FALSE(tariff_inversed_interval1_.IsValid(LogExtra{}));
}

TEST_F(TariffIsValidTest, TariffIsNotValid4reversedInterval2) {
  ASSERT_FALSE(tariff_inversed_interval2_.IsValid(LogExtra{}));
}

TEST_F(TariffIsValidTest, ValidIntervalCheck) {
  tariff::Interval intvl{1.0, 2.0, 5.0, tariff::IntervalPaymentMode::Prepay,
                         1.0};
  ASSERT_TRUE(intvl.IsValid(LogExtra{}));
}

TEST_F(TariffIsValidTest, NonValidIntervalCheck) {
  tariff::Interval intvl{2.0, 1.0, 5.0, tariff::IntervalPaymentMode::Prepay,
                         1.0};
  ASSERT_FALSE(intvl.IsValid(LogExtra{}));
}
