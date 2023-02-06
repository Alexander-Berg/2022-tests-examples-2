#include <gtest/gtest.h>
#include <cache/territories.hpp>
#include <handlers/context.hpp>
#include <httpclient/request.hpp>
#include <threads/async.hpp>

namespace {
namespace tt = clients::taxi_territories;

const clients::Graphite& graphite() {
  static const clients::Graphite client;
  return client;
}

const utils::http::Client& http_client() {
  static utils::Async async(2, "xx", false);
  static const utils::http::Client client(async, 1, "test_http_client", false);
  return client;
}

class MockConfigDataProvider : public utils::DataProvider<config::Config> {
 public:
  UnsafePtr GetUnsafe() const override { return nullptr; }
};

class AgglomerationsTest : private caches::Territories {
 public:
  AgglomerationsTest()
      : caches::Territories(
            tt::Client(http_client(), std::string(), std::string()), graphite(),
            MockConfigDataProvider()) {}

  static tt::AgglomerationsByNameMap PublicProceedAgglomerations(
      std::vector<tt::Agglomeration>& agglomerations) {
    return ProceedAgglomerations(agglomerations, LogExtra());
  }
};

}  // namespace

TEST(TerritoriesCache, GoodRules) {
  std::vector<tt::Agglomeration> parsed_agglomerations = {
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

  tt::AgglomerationsByNameMap expected_result = {
      {"moscow", parsed_agglomerations[0]},
      {"cao", parsed_agglomerations[1]},
      {"uao", parsed_agglomerations[2]},
      {"district_1", parsed_agglomerations[3]},
      {"district_2", parsed_agglomerations[4]},
      {"district_3", parsed_agglomerations[5]},
      {"district_4", parsed_agglomerations[6]}};

  auto result =
      AgglomerationsTest::PublicProceedAgglomerations(parsed_agglomerations);

  ASSERT_EQ(result, expected_result);
}

TEST(TerritoriesCache, BadRules) {
  std::vector<tt::Agglomeration> parsed_agglomerations = {
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
       }},
      {utils::datetime::Stringtime("2019-03-10T15:14:47+0000"),
       "",  // Skipped cause of empty name
       {
           {"district_4_tariff_zone_1",
            tt::Agglomeration::Sibling::Type::TariffZone},
           {"district_4_tariff_zone_2",
            tt::Agglomeration::Sibling::Type::TariffZone},
           {"district_4_geoarea_1", tt::Agglomeration::Sibling::Type::Geoarea},
       }},
      {utils::datetime::Stringtime("2019-03-10T15:14:47+0000"),
       "district_12",  // Skipped cause of empty contains
       {}}};

  tt::AgglomerationsByNameMap expected_result = {
      {"moscow", parsed_agglomerations[0]},
      {"cao", parsed_agglomerations[1]},
      {"uao", parsed_agglomerations[2]},
      {"district_1", parsed_agglomerations[3]},
      {"district_2", parsed_agglomerations[4]},
      {"district_3", parsed_agglomerations[5]},
      {"district_4", parsed_agglomerations[6]}};

  auto result =
      AgglomerationsTest::PublicProceedAgglomerations(parsed_agglomerations);

  ASSERT_EQ(result, expected_result);
}
