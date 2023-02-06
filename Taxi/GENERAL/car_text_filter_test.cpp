#include <gtest/gtest.h>

#include <helpers/car_builder_test.hpp>

#include "car_text_filter.hpp"

namespace {

using utils::CarTextFilter;

void TestRank(const utils::TextRank expected_rank, const models::Car& car,
              const std::string& query_text) {
  EXPECT_EQ(expected_rank, (CarTextFilter{query_text}.GetRank(car)))
      << "rank differ at query text: `" << query_text << "`";
}

}  // namespace

TEST(CarTextFilter, GetRank) {
  const auto& car = CarBuilder()
                        .VIN("W1NW0NW1NW0NW1NHP")
                        .Brand("Audi")
                        .Model("A8")
                        .NormalizedNumber("X001AM97")
                        .CallSign("James007")
                        .PermitDoc("JQ 026224")
                        .PermitNum("11234")
                        .PermitSeries(u8"МСК")
                        .RegistrationCertificate("5060 122445")
                        .Build();

  using utils::kZeroTextRank;
  const auto& kIdMatch = CarTextFilter::kIdMatch;
  const auto& kVinMatch = CarTextFilter::kVinMatch;
  const auto& kBrandMatch = CarTextFilter::kBrandMatch;
  const auto& kModelMatch = CarTextFilter::kModelMatch;
  const auto& kNumberMatch = CarTextFilter::kNumberMatch;
  const auto& kCallSignMatch = CarTextFilter::kCallSignMatch;
  const auto& kPermitDocMatch = CarTextFilter::kPermitDocMatch;
  const auto& kPermitNumMatch = CarTextFilter::kPermitNumMatch;
  const auto& kPermitSeriesMatch = CarTextFilter::kPermitSeriesMatch;
  const auto& kRegistrationCertMatch = CarTextFilter::kRegistrationCertMatch;

  // id
  TestRank(kIdMatch.substring, car, "car");
  TestRank(kIdMatch.prefix, car, "test_");
  TestRank(kIdMatch.exact, car, "test_car_id");
  TestRank(kIdMatch.exact, car, "TEST_CAR_ID");

  // VIN
  TestRank(kZeroTextRank, car, "W1");
  TestRank(kZeroTextRank, car, "W0");
  TestRank(kVinMatch.substring, car, "NW0N");
  TestRank(kVinMatch.substring, car, "NWON");
  TestRank(kVinMatch.substring, car, "WONW");
  TestRank(kVinMatch.substring, car, "0NWINW");
  TestRank(kVinMatch.prefix, car, "W1N");
  TestRank(kVinMatch.prefix, car, "W1NW0");
  TestRank(kVinMatch.exact, car, "W1NW0NW1NW0NW1NHP");
  TestRank(kVinMatch.exact, car, u8"W1NW0NW1NW0NW1NНР");

  // brand
  TestRank(kZeroTextRank, car, "Au");
  TestRank(kZeroTextRank, car, "di");
  TestRank(kBrandMatch.substring, car, "uDI");
  TestRank(kBrandMatch.substring, car, "UDI");
  TestRank(kBrandMatch.prefix, car, "Aud");
  TestRank(kBrandMatch.prefix, car, "AUD");
  TestRank(kBrandMatch.exact, car, "audi");
  TestRank(kBrandMatch.exact, car, "Audi");
  TestRank(kBrandMatch.exact, car, "AUDI");

  // model
  TestRank(kZeroTextRank, car, "a");
  TestRank(kZeroTextRank, car, "8");
  TestRank(kModelMatch.exact, car, "A8");
  TestRank(kModelMatch.exact, car, "a8");

  // number
  TestRank(kZeroTextRank, car, "1");
  TestRank(kNumberMatch.substring, car, "01");
  TestRank(kNumberMatch.prefix, car, "AM");
  TestRank(kNumberMatch.substring, car, "97");
  TestRank(kNumberMatch.substring, car, "001");
  TestRank(kNumberMatch.substring, car, u8"1АM");
  TestRank(kNumberMatch.substring, car, u8"001Ам");
  TestRank(kNumberMatch.prefix, car, "x00");
  TestRank(kNumberMatch.prefix, car, u8"х001Ам");
  TestRank(kNumberMatch.exact, car, "X001AM97");
  TestRank(kNumberMatch.exact, car, u8"Х001АМ97");

  // call sign
  TestRank(kZeroTextRank, car, "J");
  TestRank(kCallSignMatch.prefix, car, "Ja");
  TestRank(kCallSignMatch.substring, car, "s0");
  TestRank(kCallSignMatch.substring, car, "AMES");
  TestRank(kCallSignMatch.substring, car, u8"007");
  TestRank(kCallSignMatch.prefix, car, "jam");
  TestRank(kCallSignMatch.prefix, car, u8"JAM");
  TestRank(kCallSignMatch.exact, car, "James007");
  TestRank(kCallSignMatch.exact, car, "jamEs007");

  // permit doc
  TestRank(kZeroTextRank, car, "JQ");
  TestRank(kPermitDocMatch.substring, car, "622");
  TestRank(kPermitDocMatch.substring, car, "026224");
  TestRank(kPermitDocMatch.prefix, car, "JQ0");
  TestRank(kPermitDocMatch.prefix, car, "JQ0262");
  TestRank(kPermitDocMatch.exact, car, "JQ026224");

  // permit num
  TestRank(kZeroTextRank, car, "11");
  TestRank(kPermitNumMatch.substring, car, "123");
  TestRank(kPermitNumMatch.prefix, car, "112");
  TestRank(kPermitNumMatch.prefix, car, "1123");
  TestRank(kPermitNumMatch.exact, car, "11234");

  // permit series
  TestRank(kZeroTextRank, car, "CK");
  TestRank(kZeroTextRank, car, "MCK");
  TestRank(kZeroTextRank, car, u8"СК");
  TestRank(kZeroTextRank, car, u8"МС");
  TestRank(kPermitSeriesMatch.exact, car, u8"МСК");

  // registration cert
  TestRank(kZeroTextRank, car, "60");
  TestRank(kZeroTextRank, car, "50");
  TestRank(kRegistrationCertMatch.substring, car, "5060");
  TestRank(kRegistrationCertMatch.substring, car, "6012");
  TestRank(kRegistrationCertMatch.substring, car, "122445");
  TestRank(kRegistrationCertMatch.prefix, car, "506");
  TestRank(kRegistrationCertMatch.prefix, car, "50601");
  TestRank(kRegistrationCertMatch.exact, car, "5060122445");

  // aggregate
  {
    const auto& rank = kVinMatch.exact + kNumberMatch.exact +
                       kPermitDocMatch.exact + kPermitSeriesMatch.exact;
    TestRank(rank, car, u8"W1NW0NW1NW0NW1NHP X001AM97 JQ026224 МСК");
  }
}
