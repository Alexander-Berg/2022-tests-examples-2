#include <gmock/gmock-spec-builders.h>
#include <gtest/gtest.h>
#include <string_view>
#include <userver/utest/utest.hpp>

#include <clients/direct-internal/client_gmock.hpp>
#include <clients/direct/client_gmock.hpp>

#include <clients/direct/requests.hpp>
#include <clients/direct/responses.hpp>
#include <components/impl/direct_storage_impl.hpp>
#include <models/advert_types.hpp>

namespace testing {
using ::clients::direct::json_v5_campaignsext::post::Request;
using ::clients::direct::json_v5_campaignsext::post::Response200;
using ::eats_restapp_marketing::components::direct_storage::impl::Component;
using ::eats_restapp_marketing::models::CampaignId;
using ::eats_restapp_marketing::models::OAuthToken;
using ::eats_restapp_marketing::models::PassportId;
using ::eats_restapp_marketing::models::Token;
using ::eats_restapp_marketing::models::TokenId;

const Token token = {TokenId(1), OAuthToken("token"), PassportId(1)};
const std::vector<CampaignId> campaigns = {CampaignId(1), CampaignId(2),
                                           CampaignId(3)};
const ::clients::direct::GetResultCampaignsAStatus any_status =
    ::clients::direct::GetResultCampaignsAStatus::kAccepted;
const ::clients::direct::GetResultCampaignsAState any_state =
    ::clients::direct::GetResultCampaignsAState::kArchived;

Request BuildRequest(const std::vector<CampaignId>& ids, const Token& t) {
  Request direct_request;
  std::vector<std::int64_t> campaign_ids;
  campaign_ids.reserve(ids.size());
  std::for_each(ids.begin(), ids.end(), [&campaign_ids](const auto& id) {
    campaign_ids.emplace_back(id.GetUnderlying());
  });
  direct_request.authorization = t.ToString();
  direct_request.body.method = clients::direct::CampaignRequestMethod::kGet;
  direct_request.body.params.selectioncriteria = {campaign_ids};
  direct_request.body.params.fieldnames = {
      clients::direct::CampaignFieldNames::kId,
      clients::direct::CampaignFieldNames::kState,
      clients::direct::CampaignFieldNames::kStatus};
  return direct_request;
}

clients::direct::GetResultCampaignsA BuildCampaignResponse(
    const std::optional<std::int64_t> id,
    const std::optional<::clients::direct::GetResultCampaignsAStatus>& status,
    const std::optional<::clients::direct::GetResultCampaignsAState>& state) {
  return {id, status, state};
}

Response200 GetResult(const std::vector<CampaignId>& contained_campaigns) {
  std::vector<clients::direct::GetResultCampaignsA> res_campaigns;
  for (const auto& id : contained_campaigns) {
    res_campaigns.emplace_back(
        BuildCampaignResponse(id.GetUnderlying(), any_status, any_state));
  }
  clients::direct::ResponseResult result;
  result.getresults = clients::direct::GetResult{res_campaigns};
  Response200 res;
  res.result = result;
  return res;
}

struct ComponentTest : public Test {
  std::shared_ptr<StrictMock<clients::direct::ClientGMock>> direct_mock =
      std::make_shared<StrictMock<clients::direct::ClientGMock>>();
  std::shared_ptr<StrictMock<clients::direct_internal::ClientGMock>>
      direct_internal_mock =
          std::make_shared<StrictMock<clients::direct_internal::ClientGMock>>();

  Component component;
  ComponentTest() : component(*direct_mock, *direct_internal_mock) {}
};
TEST_F(ComponentTest, getAllCampaigns) {
  EXPECT_CALL(*direct_mock,
              JsonV5Campaignsext(BuildRequest(campaigns, token), _))
      .WillOnce(Return(GetResult(campaigns)));
  auto result = component.GetDirectStatuses(campaigns, token);
  ASSERT_EQ(result.size(), campaigns.size());
}
TEST_F(ComponentTest, getNotAllCampaigns) {
  auto direct_result = {campaigns[0], campaigns[1]};
  EXPECT_CALL(*direct_mock,
              JsonV5Campaignsext(BuildRequest(campaigns, token), _))
      .WillOnce(Return(GetResult(direct_result)));
  auto result = component.GetDirectStatuses(campaigns, token);
  ASSERT_EQ(result.size(), direct_result.size());
}
TEST_F(ComponentTest, getEmptyResult) {
  EXPECT_CALL(*direct_mock,
              JsonV5Campaignsext(BuildRequest(campaigns, token), _))
      .Times(0);
  auto result = component.GetDirectStatuses({}, token);
  ASSERT_TRUE(result.empty());
}
TEST_F(ComponentTest, getNoCampaigns) {
  EXPECT_CALL(*direct_mock,
              JsonV5Campaignsext(BuildRequest(campaigns, token), _))
      .WillOnce(Return(GetResult({})));
  EXPECT_ANY_THROW(component.GetDirectStatuses(campaigns, token));
}
}  // namespace testing

namespace clients::direct::json_v5_campaignsext::post {
inline bool operator==(const Request& lhs, const Request& rhs) {
  return std::tie(lhs.authorization, lhs.body.method) ==
         std::tie(rhs.authorization, rhs.body.method);
}
}  // namespace clients::direct::json_v5_campaignsext::post
