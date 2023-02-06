#include <gtest/gtest.h>
#include <userver/utest/utest.hpp>

#include "components/impl/direct_storage_impl.hpp"

#include <clients/direct-internal/client_gmock.hpp>
#include <clients/direct/client_gmock.hpp>

class CampaignId;

using namespace clients::direct;
using namespace clients::direct_internal;
using namespace eats_restapp_marketing::components::direct_storage::impl;
namespace models = eats_restapp_marketing::models;

namespace testing {

struct DirectStorageComponentTest : public Test {
  std::shared_ptr<StrictMock<clients::direct::ClientGMock>> direct_gmock_ =
      std::make_shared<StrictMock<clients::direct::ClientGMock>>();
  std::shared_ptr<StrictMock<clients::direct_internal::ClientGMock>>
      direct_internal_gmock_ =
          std::make_shared<StrictMock<clients::direct_internal::ClientGMock>>();

  Component impl_;

  DirectStorageComponentTest()
      : impl_(*direct_gmock_, *direct_internal_gmock_) {}

  static models::Token MakeToken() {
    return {
        models::TokenId{333},               // token_id
        models::OAuthToken{"TOKEN_TOKEN"},  // oauth_token
        models::PassportId{1234567}         // passport_id
    };
  }
  static models::AdvertMain MakeAdvert() {
    const auto updated_at = ::utils::datetime::Now();

    return {
        models::AdvertId{777},                        // advert_id
        std::nullopt,                                 // created_at
        storages::postgres::TimePointTz{updated_at},  // updated_at
        models::PlaceId{111},                         // place_id
        25000000,                                     // averagecpc
        models::CampaignId{123},                      // campaign_id;
        "5d534825-be18-4728-bd9b-55b17353431a",       // campaign_uuid
        234,                                          // group_id;
        345,                                          // ad_id;
        456,                                          // content_id;
        567,                                          // banner_id;
        true,                                         // is_active;
        std::nullopt,                                 // error;
        1234567,                                      // passport_id;
        2500000000,                                   // weekly_spend_limit;
        std::nullopt,                                 // advert_status;
        std::nullopt,                                 // advert_reason_status;
        std::nullopt,                                 // started_at;
        std::nullopt,                                 //  suspended_at;
        models::CampaignType::kCPM,                   // campaign_type{};
        models::StrategyType::kAverageCpc,            // strategy_type{};
        ""                                            // experiment
    };
  }

  static eats_restapp_marketing::types::place_info::PlaceInfo MakePlaceInfo() {
    return {
        "place name",                // name;
        "place_slug",                // slug;
        std::vector<std::string>{},  // categories;
        "RU"                         // country_code
    };
  }
};

TEST_F(DirectStorageComponentTest, MakeContent_true) {
  std::string_view place_slug = "custom_slug";
  const auto token = MakeToken();
  const auto prefix = "prefix_";

  json_v5_promotedcontent::post::Request request;
  request.body.method = PromotedContentRequestMethod::kAdd;
  PromotedContentAddItem item;
  item.type = PromotedContentAddItemType::kEda;
  item.url = std::string{prefix} + std::string{place_slug};
  request.body.params.promotedcontent.push_back(item);
  request.authorization = token.ToString();

  json_v5_promotedcontent::post::Response200 response{};
  IdResult result;
  result.id = 654321;
  response.result = ::clients::direct::ResponseResult{};
  response.result->addresults =
      ::std::vector<clients::direct::IdResult>{result};

  EXPECT_CALL(*direct_gmock_, JsonV5Promotedcontent(request, _))
      .Times(1)
      .WillOnce(Return(response));

  const auto content_id = impl_.MakeContent(place_slug, token, prefix);
  ASSERT_EQ(content_id, 654321);
}

TEST_F(DirectStorageComponentTest, MakeContent_throw) {
  std::string_view place_slug = "custom_slug";
  const auto token = MakeToken();
  const auto prefix = "prefix_";

  json_v5_promotedcontent::post::Request request;
  request.body.method = PromotedContentRequestMethod::kAdd;
  PromotedContentAddItem item;
  item.type = PromotedContentAddItemType::kEda;
  item.url = std::string{prefix} + std::string{place_slug};
  request.body.params.promotedcontent.push_back(item);
  request.authorization = token.ToString();

  json_v5_promotedcontent::post::Response200 response{};

  EXPECT_CALL(*direct_gmock_, JsonV5Promotedcontent(request, _))
      .Times(1)
      .WillOnce(Return(response));

  EXPECT_THROW(impl_.MakeContent(place_slug, token, prefix),
               std::runtime_error);
}

TEST_F(DirectStorageComponentTest, SetLanguage_true) {
  models::CampaignId campaign_id{777};
  const auto lang = "KZ";
  using namespace clients::direct_internal::campaigns_language::post;
  Request request;
  request.campaignid = campaign_id.GetUnderlying();
  request.language = Language::kKz;
  Response200 response200;
  EXPECT_CALL(*direct_internal_gmock_, CampaignsLanguage(_, _))
      .Times(1)
      .WillOnce(Return(response200));
  impl_.SetLanguage(campaign_id, lang);
}

TEST_F(DirectStorageComponentTest, SetLanguage_throw_parse) {
  models::CampaignId campaign_id{777};
  const auto lang = "kz";
  EXPECT_CALL(*direct_internal_gmock_, CampaignsLanguage(_, _)).Times(0);
  EXPECT_THROW(impl_.SetLanguage(campaign_id, lang), std::runtime_error);
}

TEST_F(DirectStorageComponentTest, UpdateAdvert_true) {
  const auto token = MakeToken();
  const auto advert = MakeAdvert();

  ContentPromotionCampaign content_promotion_campaign;
  content_promotion_campaign.biddingstrategy.search.biddingstrategytype =
      ContentPromotionCampaignSearchStrategyAddBiddingstrategytype::kAverageCpc;
  auto averagecpc_update = AverageCpcUpdate();

  averagecpc_update.averagecpc = advert.averagecpc;
  averagecpc_update.weeklyspendlimit = advert.weekly_spend_limit;
  content_promotion_campaign.biddingstrategy.search.averagecpc =
      averagecpc_update;

  content_promotion_campaign.biddingstrategy.search.averagecpc =
      averagecpc_update;
  content_promotion_campaign.biddingstrategy.network.biddingstrategytype =
      ContentPromotionCampaignNetworkStrategyAddBiddingstrategytype::
          kServingOff;
  CampaignAddItem item;
  item.contentpromotioncampaign = std::move(content_promotion_campaign);
  item.id = advert.campaign_id.value().GetUnderlying();

  json_v5_campaignsext::post::Request request;
  request.body.method = CampaignRequestMethod::kUpdate;
  request.body.params.campaigns = {item};
  request.authorization = token.ToString();

  json_v5_campaignsext::post::Response200 response200;

  EXPECT_CALL(*direct_gmock_, JsonV5Campaignsext(request, _))
      .Times(1)
      .WillOnce(Return(response200));

  impl_.UpdateAdvert(advert, token);
}

TEST_F(DirectStorageComponentTest, UpdateAdvert_throw) {
  const auto token = MakeToken();
  const auto advert = MakeAdvert();

  ContentPromotionCampaign content_promotion_campaign;
  content_promotion_campaign.biddingstrategy.search.biddingstrategytype =
      ContentPromotionCampaignSearchStrategyAddBiddingstrategytype::kAverageCpc;
  auto averagecpc_update = AverageCpcUpdate();

  averagecpc_update.averagecpc = advert.averagecpc;
  averagecpc_update.weeklyspendlimit = advert.weekly_spend_limit;
  content_promotion_campaign.biddingstrategy.search.averagecpc =
      averagecpc_update;

  content_promotion_campaign.biddingstrategy.search.averagecpc =
      averagecpc_update;
  content_promotion_campaign.biddingstrategy.network.biddingstrategytype =
      ContentPromotionCampaignNetworkStrategyAddBiddingstrategytype::
          kServingOff;
  CampaignAddItem item;
  item.contentpromotioncampaign = std::move(content_promotion_campaign);
  item.id = advert.campaign_id.value().GetUnderlying();

  json_v5_campaignsext::post::Request request;
  request.body.method = CampaignRequestMethod::kUpdate;
  request.body.params.campaigns = {item};
  request.authorization = token.ToString();

  json_v5_campaignsext::post::Response200 response200;
  response200.error = ::clients::direct::ResponseError{};

  EXPECT_CALL(*direct_gmock_, JsonV5Campaignsext(request, _))
      .Times(1)
      .WillOnce(Return(response200));

  EXPECT_THROW(impl_.UpdateAdvert(advert, token), std::runtime_error);
}

TEST_F(DirectStorageComponentTest, GetBalance_true) {
  const auto token = MakeToken();

  live_v4_json::post::Request request;
  request.body.token = token.RawString();

  live_v4_json::post::Response200 response;
  response.data = ::clients::direct::BalanceResponseData{};

  ::std::vector<clients::direct::BalanceResponseDataAccountsA> acs;
  acs.emplace_back(clients::direct::BalanceResponseDataAccountsA{
      "500.5",  // amount
      "RUB",    // currency
      {}        // extra
  });
  response.data->accounts = acs;

  eats_restapp_marketing::types::balance::Balance balance{
      "500.5",  // balance
      "RUB"     // currency
  };

  EXPECT_CALL(*direct_gmock_, LiveV4Json(request, _))
      .Times(1)
      .WillOnce(Return(response));
  ASSERT_EQ(impl_.GetBalance(token, false), balance);
}

TEST_F(DirectStorageComponentTest, GetBalance_throw) {
  const auto token = MakeToken();

  live_v4_json::post::Request request;
  request.body.token = token.RawString();

  live_v4_json::post::Response200 response;

  EXPECT_CALL(*direct_gmock_, LiveV4Json(request, _))
      .Times(1)
      .WillOnce(Return(response));
  EXPECT_THROW(impl_.GetBalance(token, false), std::runtime_error);
}

TEST_F(DirectStorageComponentTest, RunOperation_true) {
  const auto token = MakeToken();
  const auto advert = MakeAdvert();
  const auto operation_suspend = "suspend";
  const auto operation_resume = "resume";

  json_v5_campaignsext::post::Request request;
  request.authorization = token.ToString();
  request.body.params.selectioncriteria = {
      {advert.campaign_id.value().GetUnderlying()}};

  {
    request.body.method = clients::direct::CampaignRequestMethod::kSuspend;
    json_v5_campaignsext::post::Response200 response;

    EXPECT_CALL(*direct_gmock_, JsonV5Campaignsext(request, _))
        .Times(1)
        .WillOnce(Return(response));
    ASSERT_TRUE(impl_.RunOperation(advert, token, operation_suspend));
  }
  {
    request.body.method = clients::direct::CampaignRequestMethod::kResume;
    json_v5_campaignsext::post::Response200 response;

    EXPECT_CALL(*direct_gmock_, JsonV5Campaignsext(request, _))
        .Times(1)
        .WillOnce(Return(response));
    ASSERT_TRUE(impl_.RunOperation(advert, token, operation_resume));
  }
}

TEST_F(DirectStorageComponentTest, RunOperation_false) {
  const auto token = MakeToken();
  const auto advert = MakeAdvert();
  const auto operation_bad = "bad";

  EXPECT_CALL(*direct_gmock_, JsonV5Campaignsext(_, _)).Times(0);
  ASSERT_FALSE(impl_.RunOperation(advert, token, operation_bad));
}

TEST_F(DirectStorageComponentTest, MakeAd_true) {
  const auto place_info = MakePlaceInfo();
  const auto token = MakeToken();
  const auto advert = MakeAdvert();

  json_v5_ads::post::Request request;

  request.body.method = AdsRequestMethod::kAdd;
  AdAddItem item;
  item.adgroupid = advert.group_id.value();
  AdAddItemContentpromotionedaad item_info;
  item_info.title = place_info.name;
  item_info.promotedcontentid = advert.content_id.value();
  item.contentpromotionedaad = item_info;

  auto& ads = request.body.params.ads.emplace();
  ads.push_back(item);

  request.authorization = token.ToString();

  json_v5_ads::post::Response200 response;
  response.result = ::clients::direct::ResponseResult{};
  response.result->addresults = std::vector{clients::direct::IdResult{123}};

  EXPECT_CALL(*direct_gmock_, JsonV5Ads(request, _))
      .Times(1)
      .WillOnce(Return(response));

  ASSERT_EQ(impl_.MakeAd(place_info, models::GroupId(advert.group_id.value()),
                         models::ContentId(advert.content_id.value()), token),
            123);
}

TEST_F(DirectStorageComponentTest, MakeAd_throw) {
  const auto place_info = MakePlaceInfo();
  const auto token = MakeToken();
  const auto advert = MakeAdvert();

  json_v5_ads::post::Request request;

  request.body.method = AdsRequestMethod::kAdd;
  AdAddItem item;
  item.adgroupid = advert.group_id.value();
  AdAddItemContentpromotionedaad item_info;
  item_info.title = place_info.name;
  item_info.promotedcontentid = advert.content_id.value();
  item.contentpromotionedaad = item_info;

  auto& ads = request.body.params.ads.emplace();
  ads.push_back(item);

  request.authorization = token.ToString();

  json_v5_ads::post::Response200 response;

  EXPECT_CALL(*direct_gmock_, JsonV5Ads(request, _))
      .Times(1)
      .WillOnce(Return(response));

  EXPECT_THROW(
      impl_.MakeAd(place_info, models::GroupId(advert.group_id.value()),
                   models::ContentId(advert.content_id.value()), token),
      std::runtime_error);
}

TEST_F(DirectStorageComponentTest, MakeGroup_true) {
  const auto token = MakeToken();
  const auto advert = MakeAdvert();

  json_v5_adgroups::post::Request request;

  request.body.method = AdGroupsRequestMethod::kAdd;

  AdGroupAddItem item;
  item.campaignid = advert.campaign_id.value().GetUnderlying();
  item.name = "EDA";
  item.regionids.push_back(0);
  item.contentpromotionadgroup = ContentPromotionAdGroupAdd();
  item.contentpromotionadgroup->promotedcontenttype =
      ContentPromotionAdGroupAddPromotedcontenttype::kEda;

  request.body.params.adgroups.push_back(item);
  request.authorization = token.ToString();

  json_v5_adgroups::post::Response200 response;
  response.result = ::clients::direct::ResponseResult{};
  response.result->addresults = std::vector{clients::direct::IdResult{123}};

  EXPECT_CALL(*direct_gmock_, JsonV5Adgroups(request, _))
      .Times(1)
      .WillOnce(Return(response));

  ASSERT_EQ(impl_.MakeGroup(advert.campaign_id.value(), token), 123);
}

TEST_F(DirectStorageComponentTest, MakeGroup_throw) {
  const auto token = MakeToken();
  const auto advert = MakeAdvert();

  json_v5_adgroups::post::Request request;

  request.body.method = AdGroupsRequestMethod::kAdd;

  AdGroupAddItem item;
  item.campaignid = advert.campaign_id.value().GetUnderlying();
  item.name = "EDA";
  item.regionids.push_back(0);
  item.contentpromotionadgroup = ContentPromotionAdGroupAdd();
  item.contentpromotionadgroup->promotedcontenttype =
      ContentPromotionAdGroupAddPromotedcontenttype::kEda;

  request.body.params.adgroups.push_back(item);
  request.authorization = token.ToString();

  json_v5_adgroups::post::Response200 response;

  EXPECT_CALL(*direct_gmock_, JsonV5Adgroups(request, _))
      .Times(1)
      .WillOnce(Return(response));

  EXPECT_THROW(impl_.MakeGroup(advert.campaign_id.value(), token),
               std::runtime_error);
}

TEST_F(DirectStorageComponentTest, MakeCampaign_true) {
  const auto info = MakePlaceInfo();
  const auto token = MakeToken();
  const auto advert = MakeAdvert();

  json_v5_campaignsext::post::Request request;

  request.body.method = CampaignRequestMethod::kAdd;

  CampaignAddItem item;
  item.name = "EDA_111";
  item.contentpromotioncampaign = ContentPromotionCampaign();
  item.contentpromotioncampaign->biddingstrategy.search.biddingstrategytype =
      ContentPromotionCampaignSearchStrategyAddBiddingstrategytype::kAverageCpc;
  auto averagecpc = AverageCpcAdd();
  averagecpc.averagecpc = advert.averagecpc;
  if (advert.weekly_spend_limit.has_value()) {
    averagecpc.weeklyspendlimit = advert.weekly_spend_limit.value();
  }
  item.contentpromotioncampaign->biddingstrategy.search.averagecpc = averagecpc;
  item.contentpromotioncampaign->biddingstrategy.network.biddingstrategytype =
      ContentPromotionCampaignNetworkStrategyAddBiddingstrategytype::
          kServingOff;
  item.clientinfo = info.name;

  request.body.params.campaigns = {item};
  request.authorization = token.ToString();

  json_v5_campaignsext::post::Response200 response;
  response.result = ::clients::direct::ResponseResult{};
  response.result->addresults = std::vector{clients::direct::IdResult{123}};

  EXPECT_CALL(*direct_gmock_, JsonV5Campaignsext(request, _))
      .Times(1)
      .WillOnce(Return(response));

  ASSERT_EQ(impl_.MakeCampaign(advert, token, info), 123);
}

TEST_F(DirectStorageComponentTest, MakeCampaign_throw) {
  const auto info = MakePlaceInfo();
  const auto token = MakeToken();
  const auto advert = MakeAdvert();

  json_v5_campaignsext::post::Request request;

  request.body.method = CampaignRequestMethod::kAdd;

  CampaignAddItem item;
  item.name = "EDA_111";
  item.contentpromotioncampaign = ContentPromotionCampaign();
  item.contentpromotioncampaign->biddingstrategy.search.biddingstrategytype =
      ContentPromotionCampaignSearchStrategyAddBiddingstrategytype::kAverageCpc;
  auto averagecpc = AverageCpcAdd();
  averagecpc.averagecpc = advert.averagecpc;
  if (advert.weekly_spend_limit.has_value()) {
    averagecpc.weeklyspendlimit = advert.weekly_spend_limit.value();
  }
  item.contentpromotioncampaign->biddingstrategy.search.averagecpc = averagecpc;
  item.contentpromotioncampaign->biddingstrategy.network.biddingstrategytype =
      ContentPromotionCampaignNetworkStrategyAddBiddingstrategytype::
          kServingOff;
  item.clientinfo = info.name;

  request.body.params.campaigns = {item};
  request.authorization = token.ToString();

  json_v5_campaignsext::post::Response200 response;

  EXPECT_CALL(*direct_gmock_, JsonV5Campaignsext(request, _))
      .Times(1)
      .WillOnce(Return(response));

  ASSERT_THROW(impl_.MakeCampaign(advert, token, info), std::runtime_error);
}

TEST_F(DirectStorageComponentTest, ResumeCampaign_true) {
  const auto token = MakeToken();
  const auto advert = MakeAdvert();

  json_v5_campaignsext::post::Request request;
  request.authorization = token.ToString();
  request.body.params.selectioncriteria = {
      {advert.campaign_id.value().GetUnderlying()}};

  request.body.method = clients::direct::CampaignRequestMethod::kResume;
  json_v5_campaignsext::post::Response200 response;

  EXPECT_CALL(*direct_gmock_, JsonV5Campaignsext(request, _))
      .Times(1)
      .WillOnce(Return(response));
  impl_.ResumeCampaign(advert, token);
}

TEST_F(DirectStorageComponentTest, CreateKeywords_true) {
  const auto token = MakeToken();

  json_v5_keywords::post::Request request;
  request.authorization = token.ToString();
  request.body.method = KeywordsRequestMethod::kAdd;
  clients::direct::Keywords keywords;
  keywords.keywords.reserve(2);
  ::clients::direct::KeywordAddItem k1;
  k1.adgroupid = 123;
  k1.keyword = "cat_one";
  ::clients::direct::KeywordAddItem k2;
  k2.adgroupid = 123;
  k2.keyword = "еда";

  keywords.keywords.emplace_back(k1);
  keywords.keywords.emplace_back(k2);

  request.body.params = std::move(keywords);

  json_v5_keywords::post::Response200 response;
  response.result = ::clients::direct::ResponseKeywordsResult{};
  response.result->addresults = std::vector{clients::direct::IdResult{123},
                                            clients::direct::IdResult{321},
                                            clients::direct::IdResult{123}};

  EXPECT_CALL(*direct_gmock_, JsonV5Keywords(request, _))
      .Times(1)
      .WillOnce(Return(response));

  ASSERT_THAT(impl_.CreateKeywords(token, models::GroupId(123),
                                   std::vector{std::string{"cat_one"}}),
              UnorderedElementsAre(123, 321));
}

TEST_F(DirectStorageComponentTest, CreateKeywords_throw) {
  const auto token = MakeToken();

  json_v5_keywords::post::Request request;
  request.authorization = token.ToString();
  request.body.method = KeywordsRequestMethod::kAdd;
  clients::direct::Keywords keywords;
  keywords.keywords.reserve(2);

  ::clients::direct::KeywordAddItem k1;
  k1.adgroupid = 123;
  k1.keyword = "cat_one";
  ::clients::direct::KeywordAddItem k2;
  k2.adgroupid = 123;
  k2.keyword = "еда";

  keywords.keywords.emplace_back(k1);
  keywords.keywords.emplace_back(k2);

  request.body.params = std::move(keywords);

  json_v5_keywords::post::Response200 response;

  EXPECT_CALL(*direct_gmock_, JsonV5Keywords(request, _))
      .Times(1)
      .WillOnce(Return(response));

  EXPECT_THROW(impl_.CreateKeywords(token, models::GroupId(123),
                                    std::vector{std::string{"cat_one"}}),
               std::runtime_error);
}

TEST_F(DirectStorageComponentTest, RegisterClient_true) {
  using namespace eats_restapp_marketing::types::direct_internal;
  const eats_restapp_marketing::types::direct_internal::
      RegisterClientRequestParams params = {
          Uid{"1234567890"}, Fio{"Vasiliy Pupkin"},
          CountryCode{CountryCode::kRussia},
          Currency{clients::direct_internal::Currency::kRub}, WithApi{true}};

  clients_addorget::post::Request request;
  request.body.uid =
      ::utils::FromString<std::int64_t>(params.uid.GetUnderlying());
  request.body.fio = params.fio.GetUnderlying();
  request.body.country = 225;
  request.body.currency = params.currency;
  request.body.with_api = params.with_api.GetUnderlying();

  clients_addorget::post::Response200 response;
  response.success = true;

  EXPECT_CALL(*direct_internal_gmock_, ClientsAddorget(request, _))
      .Times(1)
      .WillOnce(Return(response));

  ASSERT_EQ(impl_.RegisterClient(params).success, response.success);
}

TEST_F(DirectStorageComponentTest, CheckClientState_true) {
  using namespace eats_restapp_marketing::types::direct_internal;
  const CheckClientStateRequestParams params = {Uid{"1234567890"}, {}};

  clients_checkclientstate::post::Request request;
  request.body.uid =
      ::utils::FromString<std::int64_t>(params.uid.GetUnderlying());

  clients_checkclientstate::post::Response200 response;
  response.success = true;

  EXPECT_CALL(*direct_internal_gmock_, ClientsCheckclientstate(request, _))
      .Times(1)
      .WillOnce(Return(response));

  ASSERT_EQ(impl_.CheckClientState(params), response);
}

}  // namespace testing

namespace clients::direct {

bool operator==(const IdResult& lhs, const IdResult& rhs) {
  return lhs.id == rhs.id;
}

namespace json_v5_promotedcontent::post {

bool operator==(const Request& lhs, const Request& rhs) {
  return std::tie(lhs.body, lhs.authorization) ==
         std::tie(rhs.body, rhs.authorization);
}

}  // namespace json_v5_promotedcontent::post

namespace json_v5_campaignsext::post {

bool operator==(const Request& lhs, const Request& rhs) {
  return std::tie(lhs.body, lhs.authorization) ==
         std::tie(rhs.body, rhs.authorization);
}

}  // namespace json_v5_campaignsext::post

namespace live_v4_json::post {

bool operator==(const Request& lhs, const Request& rhs) {
  return std::tie(lhs.body, lhs.authorization) ==
         std::tie(rhs.body, rhs.authorization);
}

}  // namespace live_v4_json::post
namespace json_v5_ads::post {

bool operator==(const Request& lhs, const Request& rhs) {
  return std::tie(lhs.body, lhs.authorization) ==
         std::tie(rhs.body, rhs.authorization);
}

}  // namespace json_v5_ads::post
namespace json_v5_adgroups::post {

bool operator==(const Request& lhs, const Request& rhs) {
  return std::tie(lhs.body, lhs.authorization) ==
         std::tie(rhs.body, rhs.authorization);
}

}  // namespace json_v5_adgroups::post
namespace json_v5_keywords::post {

bool operator==(const Request& lhs, const Request& rhs) {
  return std::tie(lhs.body, lhs.authorization) ==
         std::tie(rhs.body, rhs.authorization);
}

}  // namespace json_v5_keywords::post

bool operator==(const CampaignAddItem& lhs, const CampaignAddItem& rhs) {
  return std::tie(lhs.name, lhs.contentpromotioncampaign, lhs.clientinfo) ==
         std::tie(rhs.name, rhs.contentpromotioncampaign, rhs.clientinfo);
}

}  // namespace clients::direct

namespace clients::direct_internal {

namespace clients_addorget::post {
bool operator==(const Request& lhs, const Request& rhs) {
  return std::tie(lhs.body.uid, lhs.body.fio, lhs.body.currency,
                  lhs.body.country, lhs.body.login, lhs.body.with_api) ==
         std::tie(rhs.body.uid, rhs.body.fio, rhs.body.currency,
                  rhs.body.country, rhs.body.login, rhs.body.with_api);
}
}  // namespace clients_addorget::post

namespace clients_checkclientstate::post {
bool operator==(const Request& lhs, const Request& rhs) {
  return std::tie(lhs.body.login, lhs.body.uid) ==
         std::tie(rhs.body.login, rhs.body.uid);
}
}  // namespace clients_checkclientstate::post
}  // namespace clients::direct_internal
