#include <gtest/gtest.h>
#include <iostream>
#include <string>

#include <defs/api/advert.hpp>
#include <models/advert_status.hpp>
#include <models/advert_types.hpp>
#include <models/banner_status.hpp>
#include <views/4.0/restapp-front/marketing/v1/ad/campaigns/get/response_builder.hpp>
namespace eats_restapp_marketing::campaigns::response_builder {
constexpr std::int64_t kCurrentPassportId = 123456;
constexpr std::int64_t kAnotherPassportId = 12345;
const models::MediaId media_id_1{"media_id_1"}, media_id_2{"media_id_2"};
const models::UrlId media_url_1{"media_url_1"}, media_url_2{"media_url_2"};
const std::string banner_text("text");
models::AdvertMain BuildCpc(int num, models::PlaceId&& place_id,
                            models::AdvertStatus&& status,
                            std::optional<std::int64_t>&& passport_id) {
  return {models::AdvertId(num),
          {},
          storages::postgres::TimePointTz(std::chrono::system_clock::now()),
          place_id,
          100,
          models::CampaignId(1),
          {"campaign_" + std::to_string(num) + "_uuid"},
          num,
          {},
          num,
          num,
          true,
          {},
          passport_id,
          1000,
          status,
          {},
          {},
          {},
          models::CampaignType::kCpmBannerCampaign,
          models::StrategyType::kAverageCpc,
          ""};
}

models::AdvertCpm BuildCpmCampaign(models::InnerCampaignId&& id,
                                   models::CampaignStatus&& status,
                                   models::PassportId&& passport_id) {
  return {std::move(id),
          "client_info",
          {},
          std::move(passport_id),
          {},
          {},
          {},
          std::move(status),
          {},
          {}};
}

models::CpmBanner BuildCpmBanner(
    int num, const models::InnerCampaignId& id, models::PlaceId&& place_id,
    std::optional<models::MediaId>&& image,
    std::optional<models::MediaId>&& original_image,
    const std::optional<std::string>& text, models::BannerStatus&& status) {
  return {models::CpmBannerId{num}, place_id, id, {},     {}, {}, {}, image,
          original_image,           text,     {}, status, {}};
}

const models::AdvertMain cpc_campaign_with_stats =
    BuildCpc(1, models::PlaceId(111111), models::AdvertStatus::kStarted,
             kCurrentPassportId);

const models::AdvertMain cpc_campaign_with_no_stats =
    BuildCpc(2, models::PlaceId(222222), models::AdvertStatus::kStarted,
             kCurrentPassportId);

const models::AdvertMain cpc_campaign_processed =
    BuildCpc(3, models::PlaceId(333333), models::AdvertStatus::kPaused,
             kCurrentPassportId);

const models::AdvertMain cpc_campaign_archived =
    BuildCpc(3, models::PlaceId(222333), models::AdvertStatus::kArchived,
             kCurrentPassportId);

const models::AdvertMain cpc_campaign_another_passport_id =
    BuildCpc(3, models::PlaceId(333333), models::AdvertStatus::kPaused,
             kAnotherPassportId);

const models::AdvertCpm cpm_campaign_1 = BuildCpmCampaign(
    models::InnerCampaignId("1"), models::CampaignStatus::kActive,
    models::PassportId(kCurrentPassportId));

const models::AdvertCpm cpm_campaign_archived = BuildCpmCampaign(
    models::InnerCampaignId("1"), models::CampaignStatus::kArchived,
    models::PassportId(kCurrentPassportId));

const models::AdvertCpm cpm_campaign_updating = BuildCpmCampaign(
    models::InnerCampaignId("1"), models::CampaignStatus::kUpdating,
    models::PassportId(kCurrentPassportId));

const models::AdvertCpm cpm_campaign_2 = BuildCpmCampaign(
    models::InnerCampaignId("2"), models::CampaignStatus::kActive,
    models::PassportId(kCurrentPassportId));

const models::CpmBanner cpm_banner_1_1 = BuildCpmBanner(
    1, cpm_campaign_1.inner_campaign_id, models::PlaceId(111111), media_id_1,
    media_id_2, {banner_text}, models::BannerStatus::kActive);
const models::CpmBanner cpm_banner_1_2 = BuildCpmBanner(
    2, cpm_campaign_1.inner_campaign_id, models::PlaceId(222222), media_id_1,
    media_id_2, {banner_text}, models::BannerStatus::kActive);
const models::CpmBanner cpm_banner_2_1 = BuildCpmBanner(
    3, cpm_campaign_2.inner_campaign_id, models::PlaceId(333333), media_id_1,
    media_id_2, {banner_text}, models::BannerStatus::kActive);

namespace testing {
struct ResponseBuilderTest : ::testing::Test {
  static std::unordered_map<models::PassportId, handlers::PassportData>
  BuildPassports() {
    std::unordered_map<models::PassportId, handlers::PassportData> passports;
    passports.try_emplace(
        models::PassportId(cpc_campaign_with_stats.passport_id.value()),
        handlers::PassportData{1, ::handlers::PassportDataStatus::kOk, "name1",
                               "login1", "avatar1"});
    return passports;
  }

  static std::unordered_map<models::MediaId, models::UrlId> BuildBanners() {
    std::unordered_map<models::MediaId, models::UrlId> banners_info_by_id;
    banners_info_by_id.try_emplace(media_id_1, media_url_1);
    banners_info_by_id.try_emplace(media_id_2, media_url_2);
    return banners_info_by_id;
  }

  static std::unordered_map<models::PlaceId, types::campaign::Stats>
  BuildCpcStats() {
    std::unordered_map<models::PlaceId, types::campaign::Stats>
        cpc_stats_by_place_id;
    types::campaign::Stats stats_1{
        std::chrono::system_clock::now(), {25}, {20}, {10}};
    cpc_stats_by_place_id.try_emplace(cpc_campaign_with_stats.place_id,
                                      stats_1);
    return cpc_stats_by_place_id;
  }

  static std::unordered_map<std::int64_t, bool> BuildRatingInfo() {
    std::unordered_map<std::int64_t, bool> rating_result;
    rating_result.try_emplace(cpc_campaign_with_stats.place_id.GetUnderlying(),
                              true);
    rating_result.try_emplace(
        cpc_campaign_with_no_stats.place_id.GetUnderlying(), true);
    rating_result.try_emplace(cpc_campaign_processed.place_id.GetUnderlying(),
                              true);
    return rating_result;
  }

  static std::vector<types::campaign::DataForCreate> BuildProcessedCpc() {
    std::vector<types::campaign::DataForCreate> processed_cpc_campaigns;
    processed_cpc_campaigns.push_back(
        {cpc_campaign_processed.id, cpc_campaign_processed.averagecpc, {}, {}});
    return processed_cpc_campaigns;
  }

  ResponseBuilderTest(
      std::optional<models::PassportId> current_passport_id = {})
      : response_builder(BuildPassports(), BuildBanners(), BuildCpcStats(),
                         BuildRatingInfo(),
                         current_passport_id.has_value()
                             ? current_passport_id.value()
                             : models::PassportId(kCurrentPassportId),
                         BuildProcessedCpc()) {}
  ResponseBuilder response_builder;
};

TEST_F(ResponseBuilderTest, cpc_response_stats) {
  response_builder.AddCampaigns({cpc_campaign_with_stats});
  auto result = response_builder.GetCampaigns();
  ASSERT_TRUE(result.size() == 1);
  ASSERT_EQ(result.begin()->campaign_id,
            cpc_campaign_with_stats.campaign_id->GetUnderlying());
  ASSERT_EQ(result.begin()->status, handlers::CampaignStatus::kActive);
  ASSERT_TRUE(result.begin()->stats.has_value());
}
TEST_F(ResponseBuilderTest, cpc_response_no_stats) {
  response_builder.AddCampaigns({cpc_campaign_with_no_stats});
  auto result = response_builder.GetCampaigns();
  ASSERT_TRUE(result.size() == 1);
  ASSERT_EQ(result.begin()->campaign_id,
            cpc_campaign_with_no_stats.campaign_id->GetUnderlying());
  ASSERT_EQ(result.begin()->status, handlers::CampaignStatus::kActive);
  ASSERT_FALSE(result.begin()->stats.has_value());
}
TEST_F(ResponseBuilderTest, cpc_response_archived) {
  response_builder.AddCampaigns({cpc_campaign_archived});
  auto result = response_builder.GetCampaigns();
  ASSERT_TRUE(result.size() == 1);
  ASSERT_EQ(result.begin()->campaign_id,
            cpc_campaign_archived.campaign_id->GetUnderlying());
  ASSERT_EQ(result.begin()->status, handlers::CampaignStatus::kArchived);
  ASSERT_FALSE(result.begin()->stats.has_value());
}
TEST_F(ResponseBuilderTest, cpc_response_processed) {
  response_builder.AddCampaigns({cpc_campaign_processed});
  auto result = response_builder.GetCampaigns();
  ASSERT_TRUE(result.size() == 1);
  ASSERT_EQ(result.begin()->campaign_id,
            cpc_campaign_processed.campaign_id->GetUnderlying());
  ASSERT_EQ(result.begin()->status, handlers::CampaignStatus::kProcess);
  ASSERT_FALSE(result.begin()->stats.has_value());
}
TEST_F(ResponseBuilderTest, cpc_response_many_campaigns) {
  response_builder.AddCampaigns({cpc_campaign_with_stats,
                                 cpc_campaign_with_no_stats,
                                 cpc_campaign_processed});
  auto result = response_builder.GetCampaigns();
  ASSERT_TRUE(result.size() == 3);
}
TEST_F(ResponseBuilderTest, cpm_response_find_image) {
  response_builder.AddCampaigns({cpm_campaign_1}, {cpm_banner_1_1});
  auto result = response_builder.GetCampaigns();
  ASSERT_TRUE(result.size() == 1);
  ASSERT_EQ(result.begin()->cpm_advert_id,
            cpm_campaign_1.inner_campaign_id.GetUnderlying());
  ASSERT_EQ(result.begin()->image, media_url_1.GetUnderlying());
  ASSERT_EQ(result.begin()->source_image, media_url_2.GetUnderlying());
}
TEST_F(ResponseBuilderTest, cpm_response_archived) {
  response_builder.AddCampaigns({cpm_campaign_archived}, {cpm_banner_1_1});
  auto result = response_builder.GetCampaigns();
  ASSERT_TRUE(result.size() == 1);
  ASSERT_EQ(result.begin()->cpm_advert_id,
            cpm_campaign_archived.inner_campaign_id.GetUnderlying());
  ASSERT_EQ(result.begin()->status, handlers::CampaignStatus::kArchived);
}
TEST_F(ResponseBuilderTest, cpm_response_updating) {
  response_builder.AddCampaigns({cpm_campaign_updating}, {cpm_banner_1_1});
  auto result = response_builder.GetCampaigns();
  ASSERT_TRUE(result.size() == 1);
  ASSERT_EQ(result.begin()->cpm_advert_id,
            cpm_campaign_updating.inner_campaign_id.GetUnderlying());
  ASSERT_EQ(result.begin()->status, handlers::CampaignStatus::kUpdating);
}

TEST_F(ResponseBuilderTest, cpm_response_two_places_one_campaign) {
  response_builder.AddCampaigns({cpm_campaign_1},
                                {cpm_banner_1_1, cpm_banner_1_2});
  auto result = response_builder.GetCampaigns();
  ASSERT_TRUE(result.size() == 2);
}

TEST_F(ResponseBuilderTest, cpm_response_two_campaigns) {
  response_builder.AddCampaigns(
      {cpm_campaign_1, cpm_campaign_2},
      {cpm_banner_1_1, cpm_banner_1_2, cpm_banner_2_1});
  auto result = response_builder.GetCampaigns();
  ASSERT_TRUE(result.size() == 3);
}
TEST_F(ResponseBuilderTest, both_response) {
  response_builder.AddCampaigns({cpc_campaign_processed,
                                 cpc_campaign_with_no_stats,
                                 cpc_campaign_with_stats});
  response_builder.AddCampaigns(
      {cpm_campaign_1, cpm_campaign_2},
      {cpm_banner_1_1, cpm_banner_1_2, cpm_banner_2_1});
  auto result = response_builder.GetCampaigns();
  ASSERT_TRUE(result.size() == 6);
  int cpc_num = 0, cpm_num = 0;
  for (const auto& item : result) {
    if (item.campaign_type == handlers::CampaignType::kCpc) {
      cpc_num++;
    }
    if (item.campaign_type == handlers::CampaignType::kCpm) {
      cpm_num++;
    }
    ASSERT_TRUE(item.has_access);
  }
  ASSERT_TRUE(cpc_num == 3);
  ASSERT_TRUE(cpm_num == 3);
}

TEST_F(ResponseBuilderTest, access_false) {
  response_builder.AddCampaigns({cpc_campaign_another_passport_id});
  auto result = response_builder.GetCampaigns();
  ASSERT_TRUE(result.size() == 1);
  ASSERT_FALSE(result.front().has_access);
}

TEST_F(ResponseBuilderTest, access_true) {
  response_builder.AddCampaigns({cpc_campaign_processed});
  auto result = response_builder.GetCampaigns();
  ASSERT_TRUE(result.size() == 1);
  ASSERT_TRUE(result.front().has_access);
}
}  // namespace testing
}  // namespace eats_restapp_marketing::campaigns::response_builder
