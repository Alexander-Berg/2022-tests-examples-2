#include <gmock/gmock.h>

#include <defs/api/v2_rules_match.hpp>
#include <userver/utils/datetime.hpp>

#include "smart_rules/serializers/matching_query.hpp"

namespace {

namespace types = billing_subventions_x::types;
namespace serializers =
    billing_subventions_x::smart_rules::serializers::matching_query;

class QueryMapper : public ::testing::Test {
  void SetUp() override {
    request_.reference_time =
        ::utils::datetime::Stringtime("2020-07-01T00:00:00Z");
    request_.zone = "moscow";
    request_.tariff_class = "econom";
    request_.has_lightbox = true;
    request_.has_sticker = true;
    request_.tags = std::vector<std::string>({"this", "that"});
    request_.geoareas = std::vector<std::string>({"here", "there"});
  }

 protected:
  handlers::V2MatchRulesRequest request_;
};

TEST_F(QueryMapper, ConvertsReferenceTime) {
  auto query = serializers::FromSchema(request_);
  ASSERT_EQ(query.reference_time, request_.reference_time);
}

TEST_F(QueryMapper, ConvertsTariffZone) {
  auto query = serializers::FromSchema(request_);
  ASSERT_EQ(query.tariff_zone, types::TariffZone(request_.zone));
}

TEST_F(QueryMapper, ConvertsTariffClass) {
  auto query = serializers::FromSchema(request_);
  ASSERT_EQ(query.tariff_class, types::TariffClass(request_.tariff_class));
}

TEST_F(QueryMapper, ConvertsActitivityPoints) {
  request_.activity_points = 60;
  auto query = serializers::FromSchema(request_);
  ASSERT_EQ(query.activity_points, types::ActivityPoints(60));
}

TEST_F(QueryMapper, ConvertsGeoAreas) {
  auto query = serializers::FromSchema(request_);
  ASSERT_THAT(query.geoareas, ::testing::ElementsAre(types::GeoArea("here"),
                                                     types::GeoArea("there")));
}

TEST_F(QueryMapper, ConvertsStickerAndLightbox) {
  request_.has_sticker = true;
  request_.has_lightbox = true;
  auto query = serializers::FromSchema(request_);
  ASSERT_THAT(query.brandings,
              ::testing::ElementsAre(types::Branding::kSticker,
                                     types::Branding::kFullBranding));
}

TEST_F(QueryMapper, ConvertsStickerAndNoLightbox) {
  request_.has_sticker = true;
  request_.has_lightbox = false;
  auto query = serializers::FromSchema(request_);
  ASSERT_THAT(query.brandings,
              ::testing::ElementsAre(types::Branding::kNoFullBranding,
                                     types::Branding::kSticker));
}

TEST_F(QueryMapper, ConvertsNoStickerAndLightbox) {
  request_.has_sticker = false;
  request_.has_lightbox = true;
  auto query = serializers::FromSchema(request_);
  ASSERT_THAT(query.brandings,
              ::testing::ElementsAre(types::Branding::kNoSticker,
                                     types::Branding::kNoFullBranding));
}

TEST_F(QueryMapper, ConvertsNoStickerAndNoLightbox) {
  request_.has_sticker = false;
  request_.has_lightbox = false;
  auto query = serializers::FromSchema(request_);
  ASSERT_THAT(query.brandings,
              ::testing::ElementsAre(types::Branding::kNoSticker,
                                     types::Branding::kNoFullBranding));
}

TEST_F(QueryMapper, ConvertsTags) {
  auto query = serializers::FromSchema(request_);
  ASSERT_THAT(query.tags,
              ::testing::ElementsAre(types::Tag("this"), types::Tag("that")));
}

TEST_F(QueryMapper, ConvertsAbsentRuleTypes) {
  auto query = serializers::FromSchema(request_);
  ASSERT_THAT(query.rule_types,
              ::testing::ElementsAre(types::RuleType::kSingleRide,
                                     types::RuleType::kGoal,
                                     types::RuleType::kSingleOnTop));
}

TEST_F(QueryMapper, ConvertsRuleTypes) {
  request_.rule_types = std::vector<handlers::SmartRuleType>{
      handlers::SmartRuleType::kSingleRide};
  auto query = serializers::FromSchema(request_);
  ASSERT_THAT(query.rule_types,
              ::testing::ElementsAre(types::RuleType::kSingleRide));
}

TEST_F(QueryMapper, ConvertTimeZone) {
  request_.timezone = "Europe/Moscow";
  auto query = serializers::FromSchema(request_);
  ASSERT_THAT(query.timezone, ::testing::Eq(request_.timezone));
}

TEST_F(QueryMapper, ConvertGeoNode) {
  request_.geonode = "br_moscow";
  auto query = serializers::FromSchema(request_);
  ASSERT_THAT(query.geonode, ::testing::Eq(types::TariffZone("br_moscow")));
}

TEST_F(QueryMapper, ConvertAbsentUDID) {
  auto query = serializers::FromSchema(request_);
  ASSERT_THAT(query.unique_driver_id, ::testing::Eq(std::nullopt));
}

TEST_F(QueryMapper, ConvertUDID) {
  request_.unique_driver_id = "cd74d504-f2e0-43bd-9553-3f07cb01fa93";
  auto query = serializers::FromSchema(request_);
  ASSERT_THAT(query.unique_driver_id.value_or(""),
              ::testing::Eq(request_.unique_driver_id));
}

}  // namespace
