#include <clients/eats-partners/client_gmock.hpp>
#include <components/partners_adaptor.hpp>
#include <userver/utest/utest.hpp>

#include <models/chat.hpp>
#include <models/partner.hpp>

namespace testing {

using ::eats_restapp_support_chat::components::AdaptorSettings;
using ::eats_restapp_support_chat::components::PartnersAdaptorImpl;

namespace models = eats_restapp_support_chat::models;
namespace client_info = clients::eats_partners::internal_partners_v1_info::get;
namespace client_search =
    clients::eats_partners::internal_partners_v1_search::post;

struct PartnersAdaptorComponentTest : public Test {
  static constexpr int64_t kLimitFifty = 50;
  static constexpr int64_t kLimitOne = 1;

  std::shared_ptr<StrictMock<clients::eats_partners::ClientGMock>>
      partners_mock =
          std::make_shared<StrictMock<clients::eats_partners::ClientGMock>>();

  PartnersAdaptorImpl component_with_limit_50;
  PartnersAdaptorImpl component_with_limit_1;

  PartnersAdaptorComponentTest()
      : component_with_limit_50(*partners_mock, AdaptorSettings(kLimitFifty)),
        component_with_limit_1(*partners_mock, AdaptorSettings(kLimitOne)) {}

  client_info::Request MakeInfoRequest(int64_t partner_id) {
    client_info::Request request_info;
    request_info.partner_id = partner_id;
    request_info.with_blocked = true;
    return request_info;
  }

  client_info::Response200 MakeInfoResponse(int64_t place_id,
                                            int64_t partner_id) {
    client_info::Response200 response200_info;
    response200_info.payload.is_blocked = false;
    response200_info.payload.places = {place_id};
    response200_info.payload.email = "vhdev@yandex.ru";
    response200_info.payload.partner_id = partner_id;
    response200_info.payload.roles = {{2, "ROLE_MANAGER"}};
    return response200_info;
  }

  client_search::Request MakeSearchRequest(int64_t place_id, int64_t cursor = 0,
                                           int64_t limit = kLimitFifty) {
    client_search::Request request_search;
    request_search.body.places = {place_id};
    request_search.limit = limit;
    request_search.offset = 0;
    request_search.cursor = cursor;
    return request_search;
  }

  client_search::Response200 MakeSearchResponse(
      int64_t place_id, int64_t partner_id, int64_t cursor = 1,
      int64_t can_fetch_next = false) {
    client_search::Response200 response200_search;
    response200_search.payload = {
        MakeInfoResponse(place_id, partner_id).payload};
    response200_search.meta.can_fetch_next = can_fetch_next;
    response200_search.meta.cursor = cursor;
    return response200_search;
  }
};

TEST_F(PartnersAdaptorComponentTest, partners_search_once) {
  int64_t partner_id = 2;
  int64_t place_id = 2;

  {
    auto request_search = MakeSearchRequest(place_id);

    auto response200_search = MakeSearchResponse(place_id, partner_id);

    EXPECT_CALL(*partners_mock, InternalPartnersV1Search(request_search, _))
        .WillOnce(Return(response200_search));
  }

  component_with_limit_50.GetPartnersByPlace(
      models::PlaceId(std::to_string(place_id)));
}

TEST_F(PartnersAdaptorComponentTest, get_partner_once) {
  int64_t partner_id = 2;
  int64_t place_id = 2;

  {
    auto request_info = MakeInfoRequest(partner_id);
    auto response200 = MakeInfoResponse(place_id, partner_id);
    ;

    EXPECT_CALL(*partners_mock, InternalPartnersV1Info(request_info, _))
        .WillOnce(Return(response200));
  }

  component_with_limit_50.GetPartner(
      models::PartnerId(std::to_string(partner_id)));
}

TEST_F(PartnersAdaptorComponentTest, get_related_logins_once) {
  int64_t partner_id = 2;
  int64_t place_id = 2;

  {
    auto request_info = MakeInfoRequest(partner_id);
    auto response200_info = MakeInfoResponse(place_id, partner_id);

    EXPECT_CALL(*partners_mock, InternalPartnersV1Info(request_info, _))
        .WillOnce(Return(response200_info));

    auto request_search = MakeSearchRequest(place_id);
    auto response200_search = MakeSearchResponse(place_id, partner_id);

    EXPECT_CALL(*partners_mock, InternalPartnersV1Search(request_search, _))
        .WillOnce(Return(response200_search));
  }

  const std::unordered_set<models::PlaceId> places = {
      models::PlaceId(std::to_string(place_id))};

  auto logins = component_with_limit_50.GetRelatedLoginsById(
      models::PartnerId(std::to_string(partner_id)), places);
  ASSERT_EQ(logins.size(), 1);
  ASSERT_EQ(logins.begin()->second.GetUnderlying(), "vhdev@yandex.ru");
}

TEST_F(PartnersAdaptorComponentTest, get_related_partners_once_by_partner_id) {
  int64_t partner_id = 2;
  int64_t place_id = 2;

  {
    auto request_info = MakeInfoRequest(partner_id);
    auto response200_info = MakeInfoResponse(place_id, partner_id);

    EXPECT_CALL(*partners_mock, InternalPartnersV1Info(request_info, _))
        .WillOnce(Return(response200_info));
  }

  models::ChatOwnerId owner_id{models::PartnerId(std::to_string(partner_id))};
  models::PartnerRole role = models::PartnerRole::kRoleManager;

  component_with_limit_50.GetRelatedPartnerIds(owner_id, role);
}

TEST_F(PartnersAdaptorComponentTest, get_related_partners_once_by_place_id) {
  int64_t partner_id = 2;
  int64_t place_id = 2;

  {
    auto request_search = MakeSearchRequest(place_id);
    auto response200_search = MakeSearchResponse(place_id, partner_id);

    EXPECT_CALL(*partners_mock, InternalPartnersV1Search(request_search, _))
        .WillOnce(Return(response200_search));
  }

  models::ChatOwnerId owner_id{models::PlaceId(std::to_string(partner_id))};
  models::PartnerRole role = models::PartnerRole::kRoleManager;

  component_with_limit_50.GetRelatedPartnerIds(owner_id, role);
}

TEST_F(PartnersAdaptorComponentTest, partners_search_twice) {
  int64_t partner_id = 2;
  int64_t place_id = 2;

  {
    auto request_search = MakeSearchRequest(place_id, 0, kLimitOne);

    auto response200_search = MakeSearchResponse(place_id, partner_id, 1, true);

    EXPECT_CALL(*partners_mock, InternalPartnersV1Search(request_search, _))
        .WillOnce(Return(response200_search));

    auto request_search2 = MakeSearchRequest(place_id, 1, kLimitOne);
    auto response200_search2 =
        MakeSearchResponse(place_id, partner_id, 2, false);

    EXPECT_CALL(*partners_mock, InternalPartnersV1Search(request_search2, _))
        .WillOnce(Return(response200_search2));
  }

  component_with_limit_1.GetPartnersByPlace(
      models::PlaceId(std::to_string(place_id)));
}

}  // namespace testing

namespace clients::eats_partners {

namespace internal_partners_v1_search::post {

inline bool operator==(const Request& lhs, const Request& rhs) {
  return std::tie(lhs.body) == std::tie(rhs.body) && lhs.cursor == rhs.cursor;
}

}  // namespace internal_partners_v1_search::post

namespace internal_partners_v1_info::get {

inline bool operator==(const Request& lhs, const Request& rhs) {
  return std::tie(lhs.partner_id) == std::tie(rhs.partner_id);
}

}  // namespace internal_partners_v1_info::get

}  // namespace clients::eats_partners
