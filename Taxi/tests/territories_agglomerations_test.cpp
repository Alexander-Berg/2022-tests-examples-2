#include <gtest/gtest.h>
#include <clients/territories.hpp>
#include <fstream>
#include <utils/datetime.hpp>

namespace {
const std::string kDirName = std::string(SOURCE_DIR) + "/tests/static/";

std::string ReadFile(const std::string& filename) {
  std::ifstream file(kDirName + filename);
  return std::string{std::istreambuf_iterator<char>(file),
                     std::istreambuf_iterator<char>()};
}

namespace tt = clients::taxi_territories;

}  // namespace

TEST(TerritoriesClient, GoodAgglomerations) {
  const auto rules = ReadFile("agglomerations/good_agglomerations.json");

  std::vector<tt::Agglomeration> agglomerations;
  ASSERT_NO_THROW(agglomerations = tt::ParseGetAgglomerationsResponse(rules));

  std::vector<tt::Agglomeration> expected_result = {
      {utils::datetime::Stringtime("2019-03-16T15:14:47+0000"),
       "moscow",
       {
           {"cao", tt::Agglomeration::Sibling::Type::Agglomeration},
           {"uao", tt::Agglomeration::Sibling::Type::Agglomeration},
           {"district_3", tt::Agglomeration::Sibling::Type::Agglomeration},
       }},
      {utils::datetime::Stringtime("2019-03-15T15:14:47+0000"),
       "cao",
       {
           {"district_1", tt::Agglomeration::Sibling::Type::Agglomeration},
       }},
      {utils::datetime::Stringtime("2019-03-14T15:14:47+0000"),
       "uao",
       {
           {"district_2", tt::Agglomeration::Sibling::Type::Agglomeration},
       }},
      {utils::datetime::Stringtime("2019-03-13T15:14:47+0000"),
       "district_1",
       {
           {"district_1_tariff_zone_1",
            tt::Agglomeration::Sibling::Type::TariffZone},
           {"district_1_tariff_zone_2",
            tt::Agglomeration::Sibling::Type::TariffZone},
           {"district_1_geoarea_1", tt::Agglomeration::Sibling::Type::Geoarea},
       }},
      {utils::datetime::Stringtime("2019-03-12T15:14:47+0000"),
       "district_2",
       {
           {"district_2_tariff_zone_1",
            tt::Agglomeration::Sibling::Type::TariffZone},
           {"district_2_tariff_zone_2",
            tt::Agglomeration::Sibling::Type::TariffZone},
           {"district_2_geoarea_1", tt::Agglomeration::Sibling::Type::Geoarea},
       }},
      {utils::datetime::Stringtime("2019-03-11T15:14:47+0000"),
       "district_3",
       {
           {"district_3_tariff_zone_1",
            tt::Agglomeration::Sibling::Type::TariffZone},
           {"district_3_tariff_zone_2",
            tt::Agglomeration::Sibling::Type::TariffZone},
           {"district_3_geoarea_1", tt::Agglomeration::Sibling::Type::Geoarea},
       }},
      {utils::datetime::Stringtime("2019-03-10T15:14:47+0000"),
       "district_4",
       {
           {"district_4_tariff_zone_1",
            tt::Agglomeration::Sibling::Type::TariffZone},
           {"district_4_tariff_zone_2",
            tt::Agglomeration::Sibling::Type::TariffZone},
           {"district_4_geoarea_1", tt::Agglomeration::Sibling::Type::Geoarea},
       }}};

  ASSERT_EQ(agglomerations, expected_result);
}

TEST(TerritoriesClient, BadAgglomerations) {
  const auto rules = ReadFile("agglomerations/bad_agglomerations.json");

  std::vector<tt::Agglomeration> agglomerations;
  ASSERT_NO_THROW(agglomerations = tt::ParseGetAgglomerationsResponse(rules));

  std::vector<tt::Agglomeration> expected_result = {
      {utils::datetime::Stringtime("2019-03-16T15:14:47+0000"),
       "moscow",
       {
           {"cao", tt::Agglomeration::Sibling::Type::Agglomeration},
           {"uao", tt::Agglomeration::Sibling::Type::Agglomeration},
           {"district_3", tt::Agglomeration::Sibling::Type::Agglomeration},
       }},
      {utils::datetime::Stringtime("2019-03-15T15:14:47+0000"),
       "cao",
       {
           {"district_1", tt::Agglomeration::Sibling::Type::Agglomeration},
       }},
      {utils::datetime::Stringtime("2019-03-14T15:14:47+0000"),
       "uao",
       {
           {"district_2", tt::Agglomeration::Sibling::Type::Agglomeration},
       }},
      {utils::datetime::Stringtime("2019-03-13T15:14:47+0000"),
       "district_1",
       {
           {"district_1_tariff_zone_1",
            tt::Agglomeration::Sibling::Type::TariffZone},
           {"district_1_tariff_zone_2",
            tt::Agglomeration::Sibling::Type::TariffZone},
           {"district_1_geoarea_1", tt::Agglomeration::Sibling::Type::Geoarea},
       }},
      {utils::datetime::Stringtime("2019-03-12T15:14:47+0000"),
       "district_2",
       {
           {"district_2_tariff_zone_1",
            tt::Agglomeration::Sibling::Type::TariffZone},
           {"district_2_tariff_zone_2",
            tt::Agglomeration::Sibling::Type::TariffZone},
           {"district_2_geoarea_1", tt::Agglomeration::Sibling::Type::Geoarea},
       }},
      {utils::datetime::Stringtime("2019-03-11T15:14:47+0000"),
       "district_3",
       {
           {"district_3_tariff_zone_1",
            tt::Agglomeration::Sibling::Type::TariffZone},
           {"district_3_tariff_zone_1",
            tt::Agglomeration::Sibling::Type::TariffZone},
           {"district_3_tariff_zone_1",
            tt::Agglomeration::Sibling::Type::TariffZone},
       }},
      {utils::datetime::Stringtime("2019-03-10T15:14:47+0000"),
       "district_4",
       {}}};

  ASSERT_EQ(agglomerations, expected_result);
}
