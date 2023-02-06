#include "driver_profile_text_filter.hpp"

#include <gtest/gtest.h>

#include <normalization/normalization.hpp>
#include <utils/text_rank.hpp>

#include <api_over_db/api_over_db_model.hpp>

namespace {

using TextFilter = utils::DriverProfileTextFilter;

void TestRank(const utils::TextRank expected_rank,
              const std::string& query_text,
              const api_over_db::models::driver_profiles::DriverProfiles& dp,
              const models::PdCache& pd_cache,
              const std::shared_ptr<
                  const api_over_db::models::fleet_vehicles::FleetVehicles>&
                  car = nullptr) {
  EXPECT_EQ(expected_rank, (TextFilter{query_text}.GetRank(dp, car, pd_cache)))
      << "rank differ at query text: `" << query_text << "`";
}

}  // namespace

TEST(DriverProfileTextFilter, GetRank) {
  api_over_db::models::driver_profiles::DriverProfiles dp;
  dp.uuid = "test_driver_id";
  dp.last_name = "Тодуа";
  dp.first_name = "Антон";
  dp.middle_name = "Романович";
  dp.driver_license_pd_id = "pd_driver_id1";
  dp.phone_pd_ids = {{"pd_phone_id1"}, {"pd_phone_id2"}};

  models::PdCache pd_cache;
  pd_cache["pd_phone_id1"] = std::make_shared<std::string>("+79104607457");
  pd_cache["pd_phone_id2"] = std::make_shared<std::string>("+79273336666");
  pd_cache["pd_driver_id1"] = std::make_shared<std::string>("77AA55577");

  auto car =
      std::make_shared<api_over_db::models::fleet_vehicles::FleetVehicles>();
  car->callsign = "bond007";
  car->number_normalized = "X001CM97";

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
  TestRank(kIdMatch.substring, "driver", dp, pd_cache);
  TestRank(kIdMatch.prefix, "test_", dp, pd_cache);
  TestRank(kIdMatch.exact, "test_driver_id", dp, pd_cache);
  TestRank(kIdMatch.exact, "TEST_DRIVER_ID", dp, pd_cache);

  // last name
  TestRank(kLastNameMatch.substring, "дуа", dp, pd_cache);
  TestRank(kLastNameMatch.prefix, "тод", dp, pd_cache);
  TestRank(kLastNameMatch.prefix, "ТОД", dp, pd_cache);
  TestRank(kLastNameMatch.exact, "Тодуа", dp, pd_cache);
  TestRank(kLastNameMatch.exact, "ТОДУА", dp, pd_cache);

  // first name
  TestRank(kFirstNameMatch.substring, "тон", dp, pd_cache);
  TestRank(kFirstNameMatch.prefix, "Ант", dp, pd_cache);
  TestRank(kFirstNameMatch.prefix, "ант", dp, pd_cache);
  TestRank(kFirstNameMatch.exact, "антон", dp, pd_cache);
  TestRank(kFirstNameMatch.exact, "аНтОН", dp, pd_cache);

  // middle name
  TestRank(kMiddleNameMatch.substring, "омaнович", dp, pd_cache);
  TestRank(kMiddleNameMatch.prefix, "Ром", dp, pd_cache);
  TestRank(kMiddleNameMatch.prefix, "ром", dp, pd_cache);
  TestRank(kMiddleNameMatch.exact, "РОМАНОВИЧ", dp, pd_cache);
  TestRank(kMiddleNameMatch.exact, "романовИЧ", dp, pd_cache);

  // license
  TestRank(kZeroTextRank, "777555", dp, pd_cache);
  TestRank(kLicenseMatch.substring, "555", dp, pd_cache);
  TestRank(kLicenseMatch.substring, "577", dp, pd_cache);
  TestRank(kLicenseMatch.prefix, "77aa", dp, pd_cache);
  TestRank(kLicenseMatch.prefix, "77aA", dp, pd_cache);
  TestRank(kLicenseMatch.prefix, "77Aa", dp, pd_cache);
  TestRank(kLicenseMatch.prefix, "77AA", dp, pd_cache);
  TestRank(kLicenseMatch.prefix, "77аа", dp, pd_cache);
  TestRank(kLicenseMatch.prefix, "77аА", dp, pd_cache);
  TestRank(kLicenseMatch.prefix, "77Аа", dp, pd_cache);
  TestRank(kLicenseMatch.prefix, "77АА", dp, pd_cache);
  TestRank(kLicenseMatch.exact, "77aа55577", dp, pd_cache);
  TestRank(kLicenseMatch.exact, "77aА55577", dp, pd_cache);
  TestRank(kLicenseMatch.exact, "77Aа55577", dp, pd_cache);
  TestRank(kLicenseMatch.exact, "77AА55577", dp, pd_cache);
  TestRank(kLicenseMatch.exact, "77аa55577", dp, pd_cache);
  TestRank(kLicenseMatch.exact, "77аA55577", dp, pd_cache);
  TestRank(kLicenseMatch.exact, "77Аa55577", dp, pd_cache);
  TestRank(kLicenseMatch.exact, "77АA55577", dp, pd_cache);
  TestRank(kLicenseMatch.exact, "77+-][АA55577", dp, pd_cache);

  // phones
  TestRank(kPhoneMatch.substring, "791", dp, pd_cache);
  TestRank(kPhoneMatch.substring, "792", dp, pd_cache);
  TestRank(kPhoneMatch.prefix, "+79", dp, pd_cache);
  TestRank(kPhoneMatch.exact, "+79104607457", dp, pd_cache);
  TestRank(kPhoneMatch.exact, "+79273336666", dp, pd_cache);

  // car number
  TestRank(kZeroTextRank, "1", dp, pd_cache, car);
  TestRank(kZeroTextRank, "A", dp, pd_cache, car);
  TestRank(kCarNumberMatch.substring, "01", dp, pd_cache, car);
  TestRank(kCarNumberMatch.substring, "CM", dp, pd_cache, car);
  TestRank(kCarNumberMatch.substring, "97", dp, pd_cache, car);
  TestRank(kCarNumberMatch.substring, "001", dp, pd_cache, car);
  TestRank(kCarNumberMatch.substring, "1ЦM", dp, pd_cache, car);
  TestRank(kCarNumberMatch.substring, "001См", dp, pd_cache, car);
  TestRank(kCarNumberMatch.prefix, "x00", dp, pd_cache, car);
  TestRank(kCarNumberMatch.prefix, "х001См", dp, pd_cache, car);
  TestRank(kCarNumberMatch.exact, "X001CM97", dp, pd_cache, car);
  TestRank(kCarNumberMatch.exact, "Х001СМ97", dp, pd_cache, car);
  TestRank(kCarNumberMatch.exact, "Х+-][001СМ97", dp, pd_cache, car);

  // car call sign
  TestRank(kZeroTextRank, "bond007", dp, pd_cache);
  TestRank(kCarCallSignMatch.substring, "ond0", dp, pd_cache, car);
  TestRank(kCarCallSignMatch.substring, "oNd0", dp, pd_cache, car);
  TestRank(kCarCallSignMatch.substring, "OND0", dp, pd_cache, car);
  TestRank(kCarCallSignMatch.prefix, "bon", dp, pd_cache, car);
  TestRank(kCarCallSignMatch.exact, "bond007", dp, pd_cache, car);
  TestRank(kCarCallSignMatch.exact, "BOND007", dp, pd_cache, car);
  TestRank(kCarCallSignMatch.exact, "BonD007", dp, pd_cache, car);

  // aggregate name
  {
    const auto& rank =
        kLastNameMatch.exact + kFirstNameMatch.exact + kMiddleNameMatch.exact;
    TestRank(rank, "ТоДУа аНТОн романович", dp, pd_cache);
  }

  // aggregate with car
  {
    const auto& rank = kIdMatch.exact + kLicenseMatch.exact +
                       kPhoneMatch.exact + kCarNumberMatch.exact +
                       kCarCallSignMatch.exact;
    TestRank(rank, "bond007 +79104607457 77AA55577 test_DRIVER_iD x001СM97", dp,
             pd_cache, car);
  }
}
