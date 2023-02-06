#include "parser.hpp"

#include <string>

#include <userver/utils/datetime.hpp>

#include <gtest/gtest.h>

#include <clients/feeds/definitions.hpp>

namespace eats_communications::models {

namespace {

auto tie(const models::AdvertSettings& advert_settings) {
  return std::tie(advert_settings.yabs_banner_id);
}

}  // namespace

bool operator==(const models::AdvertSettings& lhs,
                const models::AdvertSettings& rhs) {
  return tie(lhs) == tie(rhs);
}

}  // namespace eats_communications::models

namespace eats_communications::banners {

namespace {

std::string GetName(const std::string& src) {
  auto dst = src;
  for (auto it = dst.begin(); it != dst.end(); it++) {
    switch (*it) {
      case ',':
      case '-':
      case ' ':
        *it = '_';
        break;
    }
  }
  return dst;
}

::clients::feeds::FeedData CreateFeedData(std::string&& raw_payload) {
  ::clients::feeds::FeedDataPayload payload{
      ::formats::json::FromString(std::move(raw_payload)),
  };
  return ::clients::feeds::FeedData{
      "test",                    // feed_id
      std::nullopt,              // parent_feed_id
      std::nullopt,              // package_id
      "test",                    // request_id
      std::nullopt,              // tags
      ::utils::datetime::Now(),  // created
      std::nullopt,              // expire
      std::nullopt,              // last_status
      std::move(payload),        // payload
      std::nullopt,              // meta
      std::nullopt,              // statistics
  };
}

struct ParseAdvertSettingsTestCase {
  std::string name{};
  ::clients::feeds::FeedData feed{};
  std::optional<models::AdvertSettings> expected{};
};

class ParseAdvertSettingsTest
    : public ::testing::TestWithParam<ParseAdvertSettingsTestCase> {};

std::vector<ParseAdvertSettingsTestCase> CreateParseAdvertSettingsTestCases() {
  return {
      {
          "no advert settings",  // name
          CreateFeedData(R"({
            "banner_id": 1,
            "priority": 0,
            "recipients": {"type": "info"}
          })"),                  // feed
          std::nullopt,          // expected
      },
      {
          "disabled advert settings means no adverts",  // name
          CreateFeedData(R"({
            "banner_id": 1,
            "priority": 0,
            "recipients": {"type": "info"},
            "advert_settings": {
              "enabled": false
            }
          })"),                                         // feed
          std::nullopt,                                 // expected
      },
      {
          "advert banner without yabs banner id",  // name
          CreateFeedData(R"({
            "banner_id": 1,
            "priority": 0,
            "recipients": {"type": "info"},
            "advert_settings": {
              "enabled": true
            }
          })"),                                    // feed
          models::AdvertSettings{
              std::nullopt,  // yabs_banner_id
          },                 // expected
      },
      {
          "advert banner with yabs banner id",  // name
          CreateFeedData(R"({
            "banner_id": 1,
            "priority": 0,
            "recipients": {"type": "info"},
            "advert_settings": {
              "enabled": true,
              "direct": {
                "campaign_id": "1234",
                "yandex_uid": "123456789",
                "banner_id": "111222333"
              }
            }
          })"),                                 // feed
          models::AdvertSettings{
              models::YabsBannerId{"111222333"},  // yabs_banner_id
          },                                      // expected
      },
  };
}

}  // namespace

TEST_P(ParseAdvertSettingsTest, Test) {
  const auto param = GetParam();

  models::EdaBanner actual;
  ASSERT_NO_THROW(actual = ParseEdaBanner(param.feed);) << param.name;

  ASSERT_EQ(param.expected, actual.advert_settings) << param.name;
}

INSTANTIATE_TEST_SUITE_P(
    ParseEdaBannerAdvertSettings, ParseAdvertSettingsTest,
    ::testing::ValuesIn(CreateParseAdvertSettingsTestCases()),
    [](const auto& test_case) { return GetName(test_case.param.name); });

}  // namespace eats_communications::banners
