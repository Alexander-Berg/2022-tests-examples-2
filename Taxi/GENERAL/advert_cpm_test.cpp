#include "advert_cpm.hpp"

#include <string>
#include <vector>

#include <userver/crypto/base64.hpp>

#include <fmt/format.h>
#include <gtest/gtest.h>

namespace eats_restapp_marketing::models {

namespace {

std::string GetName(std::string name) {
  for (auto& c : name) {
    switch (c) {
      case ' ':
        c = '_';
    }
  }

  return name;
}

struct CpmFilterIsSaneTestCase {
  std::string name;
  CpmAdvertFilter target;
  bool expected;
};

std::vector<CpmFilterIsSaneTestCase> CreateCpmFilterIsSaneTestCases() {
  return {
      {
          "no inner campaign ids and statuses",  // name
          CpmAdvertFilter{},                     // target
          false,                                 // expected
      },
      {
          "has campaigns",  // name
          CpmAdvertFilter{
              {InnerCampaignId("1")},  // inner_campaign_ids
              {},                      // banner_statuses
              {},                      // media_id
              {},                      // id
              {},                      // place_ids
          },                           // target
          true,                        // expected
      },
      {
          "has statuses",  // name
          CpmAdvertFilter{
              {},                               // inner_campaign_ids
              {models::BannerStatus::kActive},  // banner_statuses
              {},                               // media_id
              {},                               // id
              {},                               // place_ids
          },                                    // target
          true,                                 // expected
      },
      {
          "has media id",  // name
          CpmAdvertFilter{
              {},                    // inner_campaign_ids
              {},                    // banner_statuses
              {models::MediaId{1}},  // media_id
              {},                    // id
              {},                    // place_ids
          },                         // target
          true,                      // expected
      },
      {
          "has banner id",  // name
          CpmAdvertFilter{
              {},                        // inner_campaign_ids
              {},                        // banner_statuses
              {},                        // media_id
              {models::CpmBannerId{1}},  // id
              {},                        // place_ids
          },                             // target
          true,                          // expected
      },
      {
          "has place id",  // name
          CpmAdvertFilter{
              {},                    // inner_campaign_ids
              {},                    // banner_statuses
              {},                    // media_id
              {},                    // id
              {models::PlaceId{1}},  // place_ids
          },                         // target
          true,                      // expected
      },
  };
};

class CpmFilterTest : public testing::TestWithParam<CpmFilterIsSaneTestCase> {};

}  // namespace

TEST_P(CpmFilterTest, IsSane) {
  const auto param = GetParam();
  const auto actual = param.target.IsSane();
  ASSERT_EQ(param.expected, actual);
}

INSTANTIATE_TEST_SUITE_P(CpmFilterTest, CpmFilterTest,
                         testing::ValuesIn(CreateCpmFilterIsSaneTestCases()),
                         [](const auto& test_case) {
                           return GetName(test_case.param.name);
                         });

TEST(FromDataUrl, EmptyDataUrl) {
  EXPECT_THROW(FromDataUrl(""), std::invalid_argument);
}

TEST(FromDataUrl, NoDataPrefix) {
  EXPECT_THROW(FromDataUrl("malformed_url"), std::invalid_argument);
}

TEST(FromDataUrl, NotBase64Encoded) {
  EXPECT_THROW(FromDataUrl("data:malformed_url"), std::invalid_argument);
}

TEST(FromDataUrl, NotData) {
  EXPECT_THROW(FromDataUrl("data:malformed_url;base64"), std::invalid_argument);
}

TEST(FromDataUrl, EmptyData) {
  EXPECT_THROW(FromDataUrl("data:malformed_url;base64,"),
               std::invalid_argument);
}

TEST(FromDataUrl, BadEncoding) {
  EXPECT_THROW(FromDataUrl("data:malformed_url;base64,a"),
               std::invalid_argument);
}

TEST(FromDataUrl, Ok) {
  const auto media_type = "image/jpeg";
  const auto blob = "hello world";

  const auto url = fmt::format("data:{};base64,{}", media_type,
                               crypto::base64::Base64Encode(blob));
  const auto actual = FromDataUrl(url);
  ASSERT_EQ(actual.media_type, media_type);
  ASSERT_EQ(actual.blob, blob);
}

}  // namespace eats_restapp_marketing::models
