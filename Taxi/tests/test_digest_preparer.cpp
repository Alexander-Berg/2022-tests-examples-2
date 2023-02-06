#include <gtest/gtest.h>

#include <fstream>
#include <list>
#include <streambuf>

#include <boost/algorithm/string.hpp>

#include <userver/formats/json/inline.hpp>
#include <userver/formats/serialize/common_containers.hpp>
#include <userver/utils/mock_now.hpp>

#include "tools/services.hpp"
#include "tools/testutils.hpp"

#include <clients/sticker/sticker_highlevel_client.hpp>
#include <models/link.hpp>
#include <radio/detail/digests/db_host_digest_constructor.hpp>
#include <radio/detail/digests/digest_preparer_tools.hpp>
#include <radio/detail/digests/incident_filters.hpp>
#include <radio/detail/digests/incident_list_digest_constructor.hpp>
#include <radio/detail/digests/service_incidents_duration_digest_constructor.hpp>
#include <utils/container_operations.hpp>

namespace hejmdal::radio {

TEST(TestDigestPreparer, ParseIncidents) {
  auto now = time::Now();

  models::Incident inc1, inc2, inc3;
  inc1.description = "test description";
  inc1.alert_status = radio::blocks::State::kWarn;
  inc1.circuit_id = "host::sensor";
  inc1.out_point_id = "out_point";
  inc1.start_time = now - time::Minutes(5);
  inc1.end_time = now - time::Minutes(2);
  inc1.incident_status = "closed";
  inc1.meta_data = formats::json::MakeObject("test_service_index", 1);

  inc2.description = "test description 2";
  inc2.alert_status = radio::blocks::State::kCritical;
  inc2.circuit_id = "host::sensor";
  inc2.out_point_id = "out_point";
  inc2.start_time = now - time::Minutes(3);
  inc2.end_time = now - time::Minutes(2);
  inc2.incident_status = "open";
  inc2.meta_data = formats::json::MakeObject("test_service_index", 1);

  inc3.description = "test description 3";
  inc3.alert_status = radio::blocks::State::kNoData;
  inc3.circuit_id = "host2::sensor";
  inc3.out_point_id = "out_point";
  inc3.start_time = now - time::Minutes(10);
  inc3.end_time = now - time::Minutes(2);
  inc3.incident_status = "open";
  inc3.meta_data = kMetaData;
  {  // Test few incidents
    auto result = detail::digests::IncidentsToString({&inc1, &inc2, &inc3},
                                                     time::Minutes(0));
    std::string body(
        "  * Начало: " +
        time::datetime::Timestring(now - time::Minutes(5), "Europe/Moscow",
                                   "%Y-%m-%d %H:%M") +
        " MSK, длительность: 3m\n     test description\n"
        "  * Начало: " +
        time::datetime::Timestring(now - time::Minutes(3), "Europe/Moscow",
                                   "%Y-%m-%d %H:%M") +
        " MSK, длительность: 1m\n     test description 2\n" + "  * Начало: " +
        time::datetime::Timestring(now - time::Minutes(10), "Europe/Moscow",
                                   "%Y-%m-%d %H:%M") +
        " MSK, длительность: 8m\n     test description 3\n"
        "     Ссылки:\n"
        "       * link text -- link address\n"
        "       * link text 2 -- link address 2?from=" +
        std::to_string(
            time::To<time::Milliseconds>(inc3.start_time - time::Hours{1})) +
        "&to=" +
        std::to_string(
            time::To<time::Milliseconds>(inc3.end_time + time::Hours{1})) +
        "\n");
    EXPECT_EQ(result, body);
  }
  {  // Test skip by duration
    auto result = detail::digests::IncidentsToString({&inc1, &inc2, &inc3},
                                                     time::Minutes(4));
    std::string body(
        "  * Начало: " +
        time::datetime::Timestring(now - time::Minutes(10), "Europe/Moscow",
                                   "%Y-%m-%d %H:%M") +
        " MSK, длительность: 8m\n     test description 3\n"
        "     Ссылки:\n"
        "       * link text -- link address\n"
        "       * link text 2 -- link address 2?from=" +
        std::to_string(
            time::To<time::Milliseconds>(inc3.start_time - time::Hours{1})) +
        "&to=" +
        std::to_string(
            time::To<time::Milliseconds>(inc3.end_time + time::Hours{1})) +
        "\n  + 2 "
        "инцидентов с длительностью меньше чем 4 мин\n");
    EXPECT_EQ(result, body);
  }
}

TEST(TestDigestPreparer, IncidentListDigest) {
  auto now = time::Now();

  models::Incident inc1, inc2, inc3;
  inc1.description = "test description";
  inc1.alert_status = radio::blocks::State::kWarn;
  inc1.circuit_id = "host::sensor";
  inc1.out_point_id = "out_point";
  inc1.start_time = now - time::Minutes(5);
  inc1.end_time = now - time::Minutes(2);
  inc1.incident_status = "closed";
  inc1.meta_data = formats::json::MakeObject("test_service_index", 1);

  inc2.description = "test description 2";
  inc2.alert_status = radio::blocks::State::kCritical;
  inc2.circuit_id = "host::sensor";
  inc2.out_point_id = "out_point";
  inc2.start_time = now - time::Minutes(3);
  inc2.end_time = now - time::Minutes(2);
  inc2.incident_status = "open";
  inc2.meta_data = formats::json::MakeObject("test_service_index", 1);

  inc3.description = "test description 3";
  inc3.alert_status = radio::blocks::State::kNoData;
  inc3.circuit_id = "host2::sensor";
  inc3.out_point_id = "out_point";
  inc3.start_time = now - time::Minutes(10);
  inc3.end_time = now - time::Minutes(2);
  inc3.incident_status = "open";

  auto buffer = std::make_shared<Buffer>();
  auto hl_client = clients::StickerHighLevelClient(buffer, "Source <s@s.s>");

  models::postgres::Digest digest{
      1,  "test digest", "a@a.a", now - time::Hours(1), 1, "incident_list", "",
      {}, std::nullopt,  {}};

  {  // Test full digest
    detail::digests::IncidentListDigestConstructor ctor(digest,
                                                        time::Minutes(0));
    auto sticker_digests = ctor.Construct({inc1, inc2, inc3}).sticker_digests;
    ASSERT_EQ(sticker_digests.size(), 1u);
    auto& sticker_digest = sticker_digests[0];
    hl_client.Send(sticker_digest);
    EXPECT_EQ(buffer->email_.from, "Source <s@s.s>");
    EXPECT_EQ(buffer->email_.subject, "Digest: test digest");
    std::string body(
        "\n - Id выхода серкита: host2::sensor::out_point\n - Инциденты:\n    "
        "   * Начало: " +
        time::datetime::Timestring(now - time::Minutes(10), "Europe/Moscow",
                                   "%Y-%m-%d %H:%M") +
        " MSK, длительность: 8m\n          test description 3\n"
        "-----------------------------------------------\n"
        " - Id выхода серкита: host::sensor::out_point\n - Инциденты:\n       "
        "* Начало: " +
        time::datetime::Timestring(now - time::Minutes(5), "Europe/Moscow",
                                   "%Y-%m-%d %H:%M") +
        " MSK, длительность: 3m\n          test description\n  "
        "     * Начало: " +
        time::datetime::Timestring(now - time::Minutes(3), "Europe/Moscow",
                                   "%Y-%m-%d %H:%M") +
        " MSK, длительность: 1m\n          test description "
        "2\n-----------------------------------------------\n\n________________"
        "___\nStay OK,\nHejmdal\n");
    EXPECT_EQ(buffer->email_.body, body);
  }
  {  // Test skip by duration
    detail::digests::IncidentListDigestConstructor ctor(digest,
                                                        time::Minutes(2));
    auto sticker_digests = ctor.Construct({inc1, inc2, inc3}).sticker_digests;
    ASSERT_EQ(sticker_digests.size(), 1u);
    auto& sticker_digest = sticker_digests[0];
    hl_client.Send(sticker_digest);
    EXPECT_EQ(buffer->email_.from, "Source <s@s.s>");
    EXPECT_EQ(buffer->email_.subject, "Digest: test digest");
    std::string body(
        "\n - Id выхода серкита: host2::sensor::out_point\n - Инциденты:\n    "
        "   * Начало: " +
        time::datetime::Timestring(now - time::Minutes(10), "Europe/Moscow",
                                   "%Y-%m-%d %H:%M") +
        " MSK, длительность: 8m\n          test description "
        "3\n-----------------------------------------------\n - Id выхода "
        "серкита: host::sensor::out_point\n - Инциденты:\n       * Начало: " +
        time::datetime::Timestring(now - time::Minutes(5), "Europe/Moscow",
                                   "%Y-%m-%d %H:%M") +
        " MSK, длительность: 3m\n          test description\n  "
        "     + 1 инцидентов с длительностью меньше чем 2 мин"
        "\n-----------------------------------------------\n\n______________"
        "_____\nStay OK,\nHejmdal\n");
    EXPECT_EQ(buffer->email_.body, body);
  }
}

TEST(TestDigestPreparer, IncidentsDurationByServiceDigest) {
  auto now = time::Now();

  models::Incident inc1, inc2, inc3, inc4;
  inc1.description = "test description";
  inc1.alert_status = radio::blocks::State::kWarn;
  inc1.circuit_id = "host1::sensor";
  inc1.out_point_id = "out_point";
  inc1.start_time = now - time::Minutes(5);
  inc1.end_time = now - time::Minutes(2);
  inc1.incident_status = "closed";
  inc1.meta_data = formats::json::MakeObject("test_service_index", 0);

  inc2.description = "test description 2";
  inc2.alert_status = radio::blocks::State::kCritical;
  inc2.circuit_id = "host2::sensor";
  inc2.out_point_id = "out_point";
  inc2.start_time = now - time::Minutes(3);
  inc2.end_time = now - time::Minutes(2);
  inc2.incident_status = "open";
  inc2.meta_data = formats::json::MakeObject("test_service_index", 0);

  inc3.description = "test description 3";
  inc3.alert_status = radio::blocks::State::kNoData;
  inc3.circuit_id = "host3::sensor";
  inc3.out_point_id = "out_point";
  inc3.start_time = now - time::Minutes(10);
  inc3.end_time = now - time::Minutes(2);
  inc3.incident_status = "open";
  inc3.meta_data = formats::json::MakeObject("test_service_index", 1);

  inc4.description = "test description 4";
  inc4.alert_status = radio::blocks::State::kWarn;
  inc4.circuit_id = "host1::sensor";
  inc4.out_point_id = "out_point";
  inc4.start_time = now - time::Minutes(120);
  inc4.end_time = now - time::Minutes(58);
  inc4.incident_status = "closed";
  inc4.meta_data = formats::json::MakeObject("test_service_index", 0);

  std::list<models::Incident> incs = {inc1, inc2, inc3, inc4};

  auto buffer = std::make_shared<Buffer>();
  auto hl_client = clients::StickerHighLevelClient(buffer, "Source <s@s.s>");

  models::postgres::Digest digest{
      1,  "test digest", "a@a.a", now - time::Hours(1), 1, "incident_list", "",
      {}, std::nullopt,  {}};

  {
    detail::digests::ServiceIncidentsDurationDigestConstructor ctor(
        digest, &GetService, 10);
    auto sticker_digests = ctor.Construct(incs).sticker_digests;
    ASSERT_EQ(sticker_digests.size(), 1u);
    auto& sticker_digest = sticker_digests[0];
    hl_client.Send(sticker_digest);
    EXPECT_EQ(buffer->email_.from, "Source <s@s.s>");
    EXPECT_EQ(buffer->email_.subject, "Digest: test digest");
    std::string body(
        "\n - Проект: project\n"
        " - Сервис:\n     service2\n       * Системный дашборд -- "
        "https://yasm.yandex-team.ru/panel/"
        "robot-taxi-clown.nanny_service2_branch_direct_link?from=" +
        std::to_string(time::To<time::Milliseconds>(digest.last_broadcast)) +
        "&to=" +
        std::to_string(time::To<time::Milliseconds>(
            digest.last_broadcast + time::Hours{digest.period_hours})) +
        "\n - Сколько "
        "времени не ОК: ~ 13%\n"
        " - Не ОК минут / всего минут: 8/60\n - Несколько самых длительных "
        "инцидентов:\n"
        "       * Начало: " +
        time::datetime::Timestring(now - time::Minutes(10), "Europe/Moscow",
                                   "%Y-%m-%d %H:%M") +
        " MSK, длительность: 8m\n          test description 3\n"
        "-----------------------------------------------\n"
        " - Проект: project\n"
        " - Сервис: service1\n - Сколько времени не ОК: ~ 8%\n"
        " - Не ОК минут / всего минут: 5/60\n - Несколько самых длительных "
        "инцидентов:\n       * Начало: " +
        time::datetime::Timestring(now - time::Minutes(5), "Europe/Moscow",
                                   "%Y-%m-%d %H:%M") +
        " MSK, длительность: 3m\n          test description\n"
        "       * Начало: " +
        time::datetime::Timestring(now - time::Minutes(3), "Europe/Moscow",
                                   "%Y-%m-%d %H:%M") +
        " MSK, длительность: 1m\n          test description 2\n"
        "       * Начало: " +
        time::datetime::Timestring(now - time::Minutes(120), "Europe/Moscow",
                                   "%Y-%m-%d %H:%M") +
        " MSK, длительность: 1h 2m\n"
        "          test description 4\n"
        "-----------------------------------------------\n\n"
        "___________________\nStay OK,\nHejmdal\n");
    auto email_body = buffer->email_.body;
    EXPECT_EQ(email_body, body);
  }
  {  // Test longest incidents
    detail::digests::ServiceIncidentsDurationDigestConstructor ctor(
        digest, &GetService, 1);
    auto sticker_digests = ctor.Construct(incs).sticker_digests;
    ASSERT_EQ(sticker_digests.size(), 1u);
    auto& sticker_digest = sticker_digests[0];
    hl_client.Send(sticker_digest);
    EXPECT_EQ(buffer->email_.from, "Source <s@s.s>");
    EXPECT_EQ(buffer->email_.subject, "Digest: test digest");
    std::string body(
        "\n - Проект: project\n"
        " - Сервис:\n     service2\n       * Системный дашборд -- "
        "https://yasm.yandex-team.ru/panel/"
        "robot-taxi-clown.nanny_service2_branch_direct_link?from=" +
        std::to_string(time::To<time::Milliseconds>(digest.last_broadcast)) +
        "&to=" +
        std::to_string(time::To<time::Milliseconds>(
            digest.last_broadcast + time::Hours{digest.period_hours})) +
        "\n - Сколько "
        "времени не ОК: ~ 13%\n"
        " - Не ОК минут / всего минут: 8/60\n - Самый длительный инцидент:\n"
        "       * Начало: " +
        time::datetime::Timestring(now - time::Minutes(10), "Europe/Moscow",
                                   "%Y-%m-%d %H:%M") +
        " MSK, длительность: 8m\n          test description 3\n"
        "-----------------------------------------------\n"
        " - Проект: project\n"
        " - Сервис: service1\n - Сколько времени не ОК: ~ 8%\n"
        " - Не ОК минут / всего минут: 5/60\n - Самый длительный инцидент:\n"
        "       * Начало: " +
        time::datetime::Timestring(now - time::Minutes(120), "Europe/Moscow",
                                   "%Y-%m-%d %H:%M") +
        " MSK, длительность: 1h 2m\n          test description 4\n"
        "-----------------------------------------------\n\n"
        "___________________\nStay OK,\nHejmdal\n");
    auto email_body = buffer->email_.body;
    EXPECT_EQ(email_body, body);
  }
}

std::string LoadTextFile(const std::string& file_name_in_static) {
  const std::string& digest_text_file_name =
      testutils::kStasticDir + file_name_in_static;
  std::ifstream ifstr(digest_text_file_name);
  std::string body((std::istreambuf_iterator<char>(ifstr)),
                   std::istreambuf_iterator<char>());
  return body;
}

TEST(TestDigestPreparer, DbByHost) {
  // monday june 8 15:09:01 UTC 2020
  auto now = time::From<time::Milliseconds>(1591628941045);
  ::utils::datetime::MockNowSet(now);

  models::Incident inc1, inc2, inc3, inc_ignore1, inc4, inc_ignore2;
  inc1.description = "test description";
  inc1.alert_status = radio::blocks::State::kWarn;
  inc1.circuit_id = "host1::sensor";
  inc1.out_point_id = "out_point";
  inc1.start_time = now - time::Minutes(5);
  inc1.end_time = now - time::Minutes(2);
  inc1.incident_status = "closed";
  inc1.meta_data = formats::json::MakeObject(
      "host_name", "host1.taxi.yandex.net", "test_service_index", 0);

  inc2.description = "test description 2";
  inc2.alert_status = radio::blocks::State::kCritical;
  inc2.circuit_id = "host2::sensor";
  inc2.out_point_id = "out_point";
  inc2.start_time = now - time::Minutes(3);
  inc2.end_time = now - time::Minutes(2);
  inc2.incident_status = "open";
  inc2.meta_data = formats::json::MakeObject(
      "host_name", "host2.taxi.yandex.net", "test_service_index", 0);

  inc3.description = "test description 3";
  inc3.alert_status = radio::blocks::State::kNoData;
  inc3.circuit_id = "host3::sensor";
  inc3.out_point_id = "out_point";
  inc3.start_time = now - time::Minutes(10);
  inc3.end_time = now - time::Minutes(2);
  inc3.incident_status = "open";
  inc3.meta_data = formats::json::MakeObject(
      "host_name", "host3.taxi.yandex.net", "test_service_index", 1);

  inc4.description = "test description 4";
  inc4.alert_status = radio::blocks::State::kWarn;
  inc4.circuit_id = "host1::sensor";
  inc4.out_point_id = "out_point";
  inc4.start_time = now - time::Minutes(120);
  inc4.end_time = now - time::Minutes(58);
  inc4.incident_status = "closed";
  inc4.meta_data = formats::json::MakeObject(
      "host_name", "host1.taxi.yandex.net", "test_service_index", 0);

  // service of this incident should not appear in the digest at all
  inc_ignore2.description = "test description ignore 2";
  inc_ignore2.alert_status = radio::blocks::State::kWarn;
  inc_ignore2.circuit_id = "host4::sensor";
  inc_ignore2.out_point_id = "out_point";
  inc_ignore2.start_time = now - time::Minutes(10);
  inc_ignore2.end_time = now - time::Minutes(2);
  inc_ignore2.incident_status = "closed";
  inc_ignore2.meta_data = formats::json::MakeObject(
      "host_name", "host4.taxi.yandex.net", "test_service_index", 2);

  std::list<models::Incident> incs = {inc1, inc2, inc3, inc4, inc_ignore2};

  auto buffer = std::make_shared<Buffer>();
  auto hl_client = clients::StickerHighLevelClient(buffer, "Source <s@s.s>");

  models::postgres::Digest digest{
      1,
      "test digest",
      "a@a.a",
      now - time::Hours(1),
      1,
      "db_by_host",
      "",
      {},
      std::nullopt,
      formats::json::MakeObject("ignored_service_suffixes",
                                formats::json::MakeArray("ignore"))};

  {  // Test longest incidents
    detail::digests::DbHostDigestConstructor ctor(digest, &GetService,
                                                  time::Minutes{0});
    auto sticker_digests = ctor.Construct(incs).sticker_digests;
    ASSERT_EQ(sticker_digests.size(), 1u);
    auto& sticker_digest = sticker_digests[0];
    hl_client.Send(sticker_digest);
    EXPECT_EQ(buffer->email_.from, "Source <s@s.s>");
    EXPECT_EQ(buffer->email_.subject, "Digest: test digest");

    auto expected_body = LoadTextFile("/digest_texts/test_db_by_host.txt");

    auto email_body = buffer->email_.body;
    EXPECT_EQ(expected_body, email_body);
  }
}

TEST(TestDigestPreparer, DbByShard) {
  // monday june 8 15:09:01 UTC 2020
  auto now = time::From<time::Milliseconds>(1591628941045);
  ::utils::datetime::MockNowSet(now);

  models::Incident inc1;
  inc1.description = "test description";
  inc1.alert_status = radio::blocks::State::kWarn;
  inc1.circuit_id = "host1::sensor";
  inc1.out_point_id = "out_point";
  inc1.start_time = now - time::Minutes(5);
  inc1.end_time = now - time::Minutes(2);
  inc1.incident_status = "closed";
  inc1.meta_data = formats::json::MakeObject("branch_name", "some_shard",
                                             "branch_direct_link", "cluster_id",
                                             "test_service_index", 0);

  auto buffer = std::make_shared<Buffer>();
  auto hl_client = clients::StickerHighLevelClient(buffer, "Source <s@s.s>");

  models::postgres::Digest digest{
      1,
      "test digest",
      "a@a.a",
      now - time::Hours(1),
      1,
      "db_by_host",
      "",
      {},
      std::nullopt,
      formats::json::MakeObject("incident_grouping", "by_branch")};

  {
    detail::digests::DbHostDigestConstructor ctor(digest, &GetService,
                                                  time::Minutes{0});
    auto sticker_digests = ctor.Construct({inc1}).sticker_digests;
    ASSERT_EQ(sticker_digests.size(), 1u);
    auto& sticker_digest = sticker_digests[0];
    hl_client.Send(sticker_digest);
    EXPECT_EQ(buffer->email_.from, "Source <s@s.s>");
    EXPECT_EQ(buffer->email_.subject, "Digest: test digest");

    auto expected_body = LoadTextFile("/digest_texts/test_db_by_shard.txt");

    auto email_body = buffer->email_.body;
    EXPECT_EQ(expected_body, email_body);
  }
}

TEST(TestDigestPreparer, TestIncidentFiltersEnv) {
  auto now = time::Now();

  models::Incident inc1, inc2, inc3;
  inc1.description = "test description";
  inc1.alert_status = radio::blocks::State::kWarn;
  inc1.circuit_id = "host::sensor";
  inc1.out_point_id = "out_point";
  inc1.start_time = now - time::Minutes(5);
  inc1.end_time = now - time::Minutes(2);
  inc1.incident_status = "closed";
  inc1.meta_data = formats::json::MakeObject("env", "prestable");

  inc2.description = "test description 2";
  inc2.alert_status = radio::blocks::State::kCritical;
  inc2.circuit_id = "host::sensor";
  inc2.out_point_id = "out_point";
  inc2.start_time = now - time::Minutes(3);
  inc2.end_time = now - time::Minutes(2);
  inc2.incident_status = "open";
  inc2.meta_data = formats::json::MakeObject("env", "stable");

  inc3.description = "test description 3";
  inc3.alert_status = radio::blocks::State::kNoData;
  inc3.circuit_id = "host2::sensor";
  inc3.out_point_id = "out_point";
  inc3.start_time = now - time::Minutes(10);
  inc3.end_time = now - time::Minutes(2);
  inc3.incident_status = "open";
  inc3.meta_data = formats::json::MakeObject("env", "testing");

  {
    formats::json::ValueBuilder builder;
    builder["env"] = std::vector<std::string>{"stable", "prestable"};
    auto filters = builder.ExtractValue();
    std::list<models::Incident> incs = {inc1, inc2, inc3};
    detail::digests::FilterIncidents(incs, filters);

    ASSERT_EQ(incs.size(), 2u);
    EXPECT_EQ(incs.front(), inc1);
    EXPECT_EQ(incs.back(), inc2);
  }
  {
    formats::json::ValueBuilder builder;
    builder["env"] = std::vector<std::string>{"testing"};
    auto filters = builder.ExtractValue();
    std::list<models::Incident> incs = {inc1, inc2, inc3};
    detail::digests::FilterIncidents(incs, filters);

    ASSERT_EQ(incs.size(), 1u);
    EXPECT_EQ(incs.front(), inc3);
  }
  {
    formats::json::ValueBuilder builder;
    builder["env"] = std::vector<std::string>{"unstable"};
    auto filters = builder.ExtractValue();
    std::list<models::Incident> incs = {inc1, inc2, inc3};
    detail::digests::FilterIncidents(incs, filters);

    ASSERT_EQ(incs.size(), 0u);
  }
  {
    formats::json::ValueBuilder builder;
    auto filters = builder.ExtractValue();
    std::list<models::Incident> incs = {inc1, inc2, inc3};
    detail::digests::FilterIncidents(incs, filters);

    ASSERT_EQ(incs.size(), 3u);
  }
}

}  // namespace hejmdal::radio
