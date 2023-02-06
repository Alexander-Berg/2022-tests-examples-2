#include "yql_queries.hpp"

#include <userver/utils/datetime.hpp>

#include <gtest/gtest.h>

namespace eats_restapp_marketing::utils {

namespace {

using ::taxi_config::eats_restapp_marketing_advert_clients_upload::
    Advertclientperiodic;
using ::taxi_config::eats_restapp_marketing_advert_settings::Bannerperiodic;

const Bannerperiodic default_config = {
    "hahn",                                            // cluster
    ::std::optional<::std::string>{},                  // yt_pool
    "//tmp/restapp/banner_ids",                        // ids_table
    "//home/yabs-cs/export/Banners",                   // direct_data
    120,                                               // check_period
    10,                                                // number_of_checks
    3600,                                              // task_period
    "//home/eda/restapp/testing/",                     // tmp_directory
    false,                                             // use_caesar
    "hahn",                                            // caesar_cluster
    "//home/bs/logs/AdsCaesarBannersFullDump/latest",  // caesar_table
};

const Advertclientperiodic advert_client_periodic_config = {
    "hahn",                                       // cluster
    "//home/eda/restapp/testing/advert_clients",  // table_directory
    std::chrono::seconds{3600},                   // task_period
    "//home/eda/restapp/tmp/",                    // tmp_directory
};

}  // namespace

TEST(MakeYabsExportYqlQuery, no_throw) {
  ASSERT_NO_THROW(MakeYabsExportYqlQuery(default_config, {}));
}

TEST(MakeYabsExportYqlQuery, ok) {
  const std::string expected =
      R"-(PRAGMA AnsiInForEmptyOrNullableItemsCollections;PRAGMA yt.TmpFolder="//home/eda/restapp/testing/";INSERT INTO hahn.`//tmp/restapp/banner_ids` WITH TRUNCATE SELECT   `BannerID`,   `ExportID` FROM hahn.`//home/yabs-cs/export/Banners` WHERE `ExportID` IN(1,2,3))-";

  const std::vector<models::AdvertId> advert_ids = {
      models::AdvertId{1},
      models::AdvertId{2},
      models::AdvertId{3},
  };
  const auto actual = MakeYabsExportYqlQuery(default_config, advert_ids);

  ASSERT_EQ(expected, actual);
}

TEST(MakeCaesarYqlQuery, no_throw) {
  ASSERT_NO_THROW(MakeCaesarYqlQuery(default_config, {}));
}

TEST(MakeCaesarYqlQuery, ok) {
  const std::string expected = R"-(
PRAGMA File('bigb.so', 'https://proxy.sandbox.yandex-team.ru/last/BIGB_UDF');
PRAGMA udf('bigb.so');
PRAGMA AnsiInForEmptyOrNullableItemsCollections;
PRAGMA yt.TmpFolder="//home/eda/restapp/testing/";

INSERT INTO hahn.`//tmp/restapp/banner_ids`
WITH TRUNCATE
SELECT
  CAST(BannerID AS int64) AS BannerID,
  CAST(ExportID AS int64) AS ExportID
FROM (
  SELECT
    BannerID,
    Bigb::ParseBannerProfile(TableRow()).Resources.EssDirectBannerExportID.Value AS ExportID
  FROM hahn.`//home/bs/logs/AdsCaesarBannersFullDump/latest`
)
WHERE ExportID IN (1,2,3);
  )-";

  const std::vector<models::AdvertId> advert_ids = {
      models::AdvertId{1},
      models::AdvertId{2},
      models::AdvertId{3},
  };
  const auto actual = MakeCaesarYqlQuery(default_config, advert_ids);

  ASSERT_EQ(expected, actual);
}

TEST(MakeCaesarYqlQuery, ow_with_pool) {
  auto config = default_config;
  config.yt_pool = "pool_name";
  const std::string expected = R"-(
PRAGMA yt.Pool = 'pool_name';

PRAGMA File('bigb.so', 'https://proxy.sandbox.yandex-team.ru/last/BIGB_UDF');
PRAGMA udf('bigb.so');
PRAGMA AnsiInForEmptyOrNullableItemsCollections;
PRAGMA yt.TmpFolder="//home/eda/restapp/testing/";

INSERT INTO hahn.`//tmp/restapp/banner_ids`
WITH TRUNCATE
SELECT
  CAST(BannerID AS int64) AS BannerID,
  CAST(ExportID AS int64) AS ExportID
FROM (
  SELECT
    BannerID,
    Bigb::ParseBannerProfile(TableRow()).Resources.EssDirectBannerExportID.Value AS ExportID
  FROM hahn.`//home/bs/logs/AdsCaesarBannersFullDump/latest`
)
WHERE ExportID IN (1,2,3);
  )-";

  const std::vector<models::AdvertId> advert_ids = {
      models::AdvertId{1},
      models::AdvertId{2},
      models::AdvertId{3},
  };
  const auto actual = MakeCaesarYqlQuery(config, advert_ids);

  ASSERT_EQ(expected, actual);
}

TEST(MakeAdvertClientsYqlQuery, no_throw) {
  ASSERT_NO_THROW(MakeAdvertClientsYqlQuery(advert_client_periodic_config, {}));
}

TEST(MakeAdvertClientsYqlQuery, ok) {
  const std::string expected = R"-(
PRAGMA AnsiInForEmptyOrNullableItemsCollections;
PRAGMA yt.TmpFolder="//home/eda/restapp/tmp/";

INSERT INTO hahn.`//home/eda/restapp/testing/advert_clients`
WITH TRUNCATE
  (`id`, `client_id`, `passport_id`, `created_at`, `updated_at`)
VALUES (CAST(1 as int64),CAST(93359492 as int64),CAST(569165633 as String),DateTime::MakeTimestamp(DateTime::ParseIso8601("2021-04-27T13:51:39.148563+0000")),DateTime::MakeTimestamp(DateTime::ParseIso8601("2021-04-27T13:51:39.148563+0000")))
,(CAST(2 as int64),CAST(93360419 as int64),CAST(644098790 as String),DateTime::MakeTimestamp(DateTime::ParseIso8601("2021-04-27T15:00:45.264351+0000")),DateTime::MakeTimestamp(DateTime::ParseIso8601("2021-04-27T15:00:45.264351+0000")))
;
  )-";

  const std::vector<models::AdvertClient> advert_clients = {
      models::AdvertClient{
          1, 93359492, "569165633",
          storages::postgres::TimePointTz{
              ::utils::datetime::Stringtime("2021-04-27T13:51:39.148563+0000")},
          storages::postgres::TimePointTz{::utils::datetime::Stringtime(
              "2021-04-27T13:51:39.148563+0000")}},
      models::AdvertClient{
          2, 93360419, "644098790",
          storages::postgres::TimePointTz{
              ::utils::datetime::Stringtime("2021-04-27T15:00:45.264351+0000")},
          storages::postgres::TimePointTz{::utils::datetime::Stringtime(
              "2021-04-27T15:00:45.264351+0000")}},
  };

  const auto actual =
      MakeAdvertClientsYqlQuery(advert_client_periodic_config, advert_clients);

  ASSERT_EQ(expected, actual);
}

}  // namespace eats_restapp_marketing::utils
