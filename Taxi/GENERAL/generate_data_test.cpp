#include "generate_data.hpp"
#include <gmock/gmock.h>
#include <boost/lexical_cast.hpp>
#include <userver/formats/json.hpp>
#include <userver/utest/utest.hpp>

using namespace eats_restapp_support_chat;

TEST(GenerateData, GenerateJsonString) {
  auto time = ::utils::datetime::FromRfc3339StringSaturating(
      "2020-01-01T01:00:00+00:00");
  auto nonce =
      models::AppliedKey{boost::lexical_cast<boost::uuids::uuid>(
                             "2ff02a49-69ef-40cd-9a67-a4548ea0adb6"),  // nonce
                         storages::postgres::TimePointTz{time},
                         storages::postgres::TimePointTz{time}};
  auto json_string =
      eats_restapp_support_chat::utils::GenerateJsonStringKeyData(nonce, 1, 2);
  ASSERT_EQ(json_string,
            "{\"nonce\":\"2ff02a49-69ef-40cd-9a67-a4548ea0adb6\",\"expire_at\":"
            "\"2020-01-01T01:00:00+00:00\",\"partner_id\":1,\"place_id\":2}");
}

TEST(GenerateData, GenerateJsonStringWithoutPlaceId) {
  auto time = ::utils::datetime::FromRfc3339StringSaturating(
      "2020-01-01T01:00:00+00:00");
  auto nonce =
      models::AppliedKey{boost::lexical_cast<boost::uuids::uuid>(
                             "2ff02a49-69ef-40cd-9a67-a4548ea0adb6"),  // nonce
                         storages::postgres::TimePointTz{time},
                         storages::postgres::TimePointTz{time}};
  auto json_string =
      eats_restapp_support_chat::utils::GenerateJsonStringKeyData(nonce, 1,
                                                                  std::nullopt);
  ASSERT_EQ(json_string,
            "{\"nonce\":\"2ff02a49-69ef-40cd-9a67-a4548ea0adb6\",\"expire_at\":"
            "\"2020-01-01T01:00:00+00:00\",\"partner_id\":1}");
}

TEST(GenerateData, GenerateJson) {
  auto time = ::utils::datetime::FromRfc3339StringSaturating(
      "2020-01-01T01:00:00+00:00");
  auto nonce =
      models::AppliedKey{boost::lexical_cast<boost::uuids::uuid>(
                             "2ff02a49-69ef-40cd-9a67-a4548ea0adb6"),  // nonce
                         storages::postgres::TimePointTz{time},
                         storages::postgres::TimePointTz{time}};
  auto json_string =
      eats_restapp_support_chat::utils::GenerateJsonStringKeyData(nonce, 1, 2);

  // Проверка, что json валидный и данные не потеряли целостности
  formats::json::Value json = formats::json::FromString(json_string);
  ASSERT_EQ(json["nonce"].As<std::string>(), to_string(nonce.nonce));
  ASSERT_EQ(json["expire_at"].As<storages::postgres::TimePointTz>(),
            nonce.expire_at);
  ASSERT_EQ(json["partner_id"].As<int64_t>(), 1);
  ASSERT_EQ(json["place_id"].As<int64_t>(), 2);
}

TEST(GenerateData, GenerateParseFlow) {
  auto time = ::utils::datetime::FromRfc3339StringSaturating(
      "2020-01-01T01:00:00+00:00");
  auto uuid = boost::lexical_cast<boost::uuids::uuid>(
      "2ff02a49-69ef-40cd-9a67-a4548ea0adb6");
  auto nonce = models::AppliedKey{uuid,  // nonce
                                  storages::postgres::TimePointTz{time},
                                  storages::postgres::TimePointTz{time}};
  auto json_string =
      eats_restapp_support_chat::utils::GenerateJsonStringKeyData(nonce, 1, 2);

  const auto& [key, partner, place] =
      eats_restapp_support_chat::utils::ParseAppliedKeyFromJsonString(
          json_string);
  ASSERT_EQ(key.nonce, uuid);
  ASSERT_EQ(key.expire_at, storages::postgres::TimePointTz{time});
  ASSERT_EQ(partner, 1);
  ASSERT_EQ(place, 2);
}

TEST(GenerateData, ParseData) {
  auto time = ::utils::datetime::FromRfc3339StringSaturating(
      "2020-01-01T01:00:00+00:00");
  auto uuid = boost::lexical_cast<boost::uuids::uuid>(
      "2ff02a49-69ef-40cd-9a67-a4548ea0adb6");
  auto json_string = R"(
{
    "nonce":"2ff02a49-69ef-40cd-9a67-a4548ea0adb6",
    "expire_at": "2020-01-01T01:00:00+00:00",
    "partner_id": 1,
    "place_id": 100
}
)";

  const auto& [key, partner, place] =
      eats_restapp_support_chat::utils::ParseAppliedKeyFromJsonString(
          json_string);
  ASSERT_EQ(key.nonce, uuid);
  ASSERT_EQ(key.expire_at, storages::postgres::TimePointTz{time});
  ASSERT_EQ(partner, 1);
  ASSERT_EQ(place.value(), 100);
}

TEST(GenerateData, ParseDataWithoutPlaceId) {
  auto time = ::utils::datetime::FromRfc3339StringSaturating(
      "2020-01-01T01:00:00+00:00");
  auto uuid = boost::lexical_cast<boost::uuids::uuid>(
      "2ff02a49-69ef-40cd-9a67-a4548ea0adb6");
  auto json_string = R"(
{
    "nonce":"2ff02a49-69ef-40cd-9a67-a4548ea0adb6",
    "expire_at": "2020-01-01T01:00:00+00:00",
    "partner_id": 1
}
)";

  const auto& [key, partner, place] =
      eats_restapp_support_chat::utils::ParseAppliedKeyFromJsonString(
          json_string);
  ASSERT_EQ(key.nonce, uuid);
  ASSERT_EQ(key.expire_at, storages::postgres::TimePointTz{time});
  ASSERT_EQ(partner, 1);
  ASSERT_EQ(place, std::nullopt);
}

TEST(GenerateData, ParseDataInvalidJson) {
  // нарушена целостность JSON
  auto json_string = R"(
{
    "nonce":"2ff02a49-69ef-40cd-9a67-a4548ea0adb6",
    "expire_at": "2020-01-01T01:00:00+00:00",
    "partner_id": 1
)";

  ASSERT_ANY_THROW(
      eats_restapp_support_chat::utils::ParseAppliedKeyFromJsonString(
          json_string));

  // неправильно поле называется uuid -> nonce
  json_string = R"(
{
    "uuid":"2ff02a49-69ef-40cd-9a67-a4548ea0adb6",
    "expire_at": "2020-01-01T01:00:00+00:00",
    "partner_id": 1
}
)";
  ASSERT_ANY_THROW(
      eats_restapp_support_chat::utils::ParseAppliedKeyFromJsonString(
          json_string));

  // неверный uuid
  json_string = R"(
{
    "nonce":"2ff02a49-69ef-40cd-9a67-a4548ea0ad",
    "expire_at": "2020-01-01T01:00:00+00:00",
    "partner_id": 1
}
)";

  ASSERT_ANY_THROW(
      eats_restapp_support_chat::utils::ParseAppliedKeyFromJsonString(
          json_string));
}
