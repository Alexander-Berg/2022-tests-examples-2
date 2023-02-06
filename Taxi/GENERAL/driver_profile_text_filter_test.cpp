#include <gtest/gtest.h>

#include <helpers/car_builder_test.hpp>
#include <helpers/driver_profile_builder_test.hpp>

#include "driver_profile_text_filter.hpp"

namespace {

using TextFilter = utils::DriverProfileTextFilter;

void TestRank(const utils::TextRank expected_rank,
              const models::DriverProfile& dp, const std::string& query_text,
              const models::Car* car = nullptr) {
  EXPECT_EQ(expected_rank, (TextFilter{query_text}.GetRank(dp, car)))
      << "rank differ at query text: `" << query_text << "`";
}

}  // namespace

TEST(DriverProfileTextFilter, GetRank) {
  const auto& dp = DriverProfileBuilder()
                       .LastName("Тодуа")
                       .FirstName("Антон")
                       .MiddleName("Романович")
                       .License("77АА55577")
                       .LicenseNormalized("77AA55577")
                       .Phones({"+79104607457", "+79273336666"})
                       .Build();

  const auto& car =
      CarBuilder().NormalizedNumber("X001AM97").CallSign("bond007").Build();

  using utils::kZeroTextRank;

  const auto& kIdMatch = TextFilter::kIdMatch;
  const auto& kLastNameMatch = TextFilter::kLastNameMatch;
  const auto& kFirstNameMatch = TextFilter::kFirstNameMatch;
  const auto& kMiddleNameMatch = TextFilter::kMiddleNameMatch;
  const auto& kLicenseMatch = TextFilter::kLicenseMatch;
  const auto& kPhoneMatch = TextFilter::kPhoneMatch;
  const auto& kCarNumberMatch = TextFilter::kCarNumberMatch;
  const auto& kCarCallSignMatch = TextFilter::kCarCallSignMatch;

  // driver_id
  TestRank(kIdMatch.substring, dp, "driver");
  TestRank(kIdMatch.prefix, dp, "test_");
  TestRank(kIdMatch.exact, dp, "test_driver_id");
  TestRank(kIdMatch.exact, dp, "TEST_DRIVER_ID");

  // last name
  TestRank(kLastNameMatch.substring, dp, u8"дуа");
  TestRank(kLastNameMatch.prefix, dp, u8"тод");
  TestRank(kLastNameMatch.prefix, dp, u8"ТОД");
  TestRank(kLastNameMatch.exact, dp, u8"Тодуа");
  TestRank(kLastNameMatch.exact, dp, u8"ТОДУА");

  // first name
  TestRank(kFirstNameMatch.substring, dp, u8"тон");
  TestRank(kFirstNameMatch.prefix, dp, u8"Ант");
  TestRank(kFirstNameMatch.prefix, dp, u8"ант");
  TestRank(kFirstNameMatch.exact, dp, u8"антон");
  TestRank(kFirstNameMatch.exact, dp, u8"аНтОН");

  // middle name
  TestRank(kMiddleNameMatch.substring, dp, u8"омaнович");
  TestRank(kMiddleNameMatch.prefix, dp, u8"Ром");
  TestRank(kMiddleNameMatch.prefix, dp, u8"ром");
  TestRank(kMiddleNameMatch.exact, dp, u8"РОМАНОВИЧ");
  TestRank(kMiddleNameMatch.exact, dp, u8"романовИЧ");

  // license
  TestRank(kZeroTextRank, dp, "777555");
  TestRank(kLicenseMatch.substring, dp, "555");
  TestRank(kLicenseMatch.substring, dp, "577");
  TestRank(kLicenseMatch.prefix, dp, "77aa");
  TestRank(kLicenseMatch.prefix, dp, "77aA");
  TestRank(kLicenseMatch.prefix, dp, "77Aa");
  TestRank(kLicenseMatch.prefix, dp, "77AA");
  TestRank(kLicenseMatch.prefix, dp, u8"77аа");
  TestRank(kLicenseMatch.prefix, dp, u8"77аА");
  TestRank(kLicenseMatch.prefix, dp, u8"77Аа");
  TestRank(kLicenseMatch.prefix, dp, u8"77АА");
  TestRank(kLicenseMatch.exact, dp, u8"77aа55577");
  TestRank(kLicenseMatch.exact, dp, u8"77aА55577");
  TestRank(kLicenseMatch.exact, dp, u8"77Aа55577");
  TestRank(kLicenseMatch.exact, dp, u8"77AА55577");
  TestRank(kLicenseMatch.exact, dp, u8"77аa55577");
  TestRank(kLicenseMatch.exact, dp, u8"77аA55577");
  TestRank(kLicenseMatch.exact, dp, u8"77Аa55577");
  TestRank(kLicenseMatch.exact, dp, u8"77АA55577");

  // phones
  TestRank(kPhoneMatch.substring, dp, "791");
  TestRank(kPhoneMatch.substring, dp, "792");
  TestRank(kPhoneMatch.prefix, dp, "+79");
  TestRank(kPhoneMatch.exact, dp, "+79104607457");
  TestRank(kPhoneMatch.exact, dp, "+79273336666");

  // car number
  TestRank(kCarNumberMatch.substring, dp, "01", &car);
  TestRank(kCarNumberMatch.substring, dp, "AM", &car);
  TestRank(kCarNumberMatch.substring, dp, "97", &car);
  TestRank(kCarNumberMatch.substring, dp, "001", &car);
  TestRank(kCarNumberMatch.substring, dp, u8"1АM", &car);
  TestRank(kCarNumberMatch.substring, dp, u8"001Ам", &car);
  TestRank(kCarNumberMatch.prefix, dp, "x00", &car);
  TestRank(kCarNumberMatch.prefix, dp, u8"х001Ам", &car);
  TestRank(kCarNumberMatch.exact, dp, "X001AM97", &car);
  TestRank(kCarNumberMatch.exact, dp, u8"Х001АМ97", &car);

  // car call sign
  TestRank(kZeroTextRank, dp, "bond007");
  TestRank(kCarCallSignMatch.substring, dp, "ond0", &car);
  TestRank(kCarCallSignMatch.substring, dp, "oNd0", &car);
  TestRank(kCarCallSignMatch.substring, dp, "OND0", &car);
  TestRank(kCarCallSignMatch.prefix, dp, "bon", &car);
  TestRank(kCarCallSignMatch.exact, dp, "bond007", &car);
  TestRank(kCarCallSignMatch.exact, dp, "BOND007", &car);
  TestRank(kCarCallSignMatch.exact, dp, "BonD007", &car);

  // aggregate name
  {
    const auto& rank =
        kLastNameMatch.exact + kFirstNameMatch.exact + kMiddleNameMatch.exact;
    TestRank(rank, dp, u8"ТоДУа аНТОн романович");
  }

  // aggregate with car
  {
    const auto& rank = kIdMatch.exact + kLicenseMatch.exact +
                       kPhoneMatch.exact + kCarNumberMatch.exact +
                       kCarCallSignMatch.exact;
    TestRank(rank, dp,
             u8"bond007 +79104607457 77AA55577 test_DRIVER_iD x001AM97", &car);
  }
}
