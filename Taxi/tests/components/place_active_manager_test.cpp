#include <testing/taxi_config.hpp>
#include <userver/utest/utest.hpp>

#include <clients/eats-core/client_gmock.hpp>
#include <clients/sender/client_gmock.hpp>
#include <userver/crypto/base64.hpp>

#include "components/place_active_manager.hpp"

using SenderClient = ::clients::sender::Client;
using CoreClient = ::clients::eats_core::Client;
using namespace eats_restapp_places::components::place_active_manager;

namespace testing {

const std::string kSenderToken = "SENDER_TOKEN";

DisabledDetails MakeDisabledDetails() {
  DisabledDetails details;
  using Reason = taxi_config::eats_restapp_places_restaurant_disable_details::
      RestaurantDisableReason;
  details.disable_reasons.emplace_back(Reason{"DISABLE_REASON_MENU_UPDATE", 0});
  details.disable_reasons.emplace_back(Reason{"DISABLE_REASON_HOLIDAYS", 4});
  details.disable_reasons.emplace_back(Reason{"DISABLE_REASON_BACKFIRING", 13});
  details.disable_reasons.emplace_back(Reason{"DISABLE_REASON_RUSH_HOUR", 28});
  details.disable_reasons.emplace_back(
      Reason{"DISABLE_REASON_SELF_BY_VENDOR", 47});
  details.disable_reasons.emplace_back(
      Reason{"DISABLE_REASON_AUTO_STOP_ORDER_CANCEL", 90});
  details.disable_reasons.emplace_back(
      Reason{"DISABLE_REASON_AUTO_STOP_CAN_NOT_COOK", 91});
  details.disable_reasons.emplace_back(
      Reason{"DISABLE_REASON_AUTO_STOP_VACATION_EVENT_EMERGENCY", 92});
  details.disable_reasons.emplace_back(
      Reason{"DISABLE_REASON_NEW_MENU_AWAIT", 111});
  details.disable_reasons.emplace_back(Reason{"DISABLE_REASON_ON_REPAIR", 112});
  return details;
}

DisabledList MakeDisabledList() {
  DisabledList list;
  using List = taxi_config::eats_restapp_places_restaurant_disable_lists::
      RestaurantDisableList;
  list.disable_reasons_lists.emplace_back(List{
      "REASONS_SELF",  // list_name
      std::vector<std::string>{
          "DISABLE_REASON_RUSH_HOUR", "DISABLE_REASON_HOLIDAYS",
          "DISABLE_REASON_SELF_BY_VENDOR",
          "DISABLE_REASON_AUTO_STOP_ORDER_CANCEL"}  // values
  });
  list.disable_reasons_lists.emplace_back(List{
      "REASONS_REQUEST",  // list_name
      std::vector<std::string>{
          "DISABLE_REASON_MENU_UPDATE", "DISABLE_REASON_NEW_MENU_AWAIT",
          "DISABLE_REASON_DELIVERY_ZONE_CHANGE", "DISABLE_REASON_TABLET_ISSUES",
          "DISABLE_REASON_ON_REPAIR"}  // values
  });
  return list;
}

EnableEmailConfig MakeEnableEmailConfig() {
  using EmailType =
      taxi_config::eats_restapp_places_enable_email_settings::MapemailsA;
  using ReasonList =
      taxi_config::eats_restapp_places_enable_email_settings::ReasonslistsA;

  EnableEmailConfig config;
  config.sender_account = "yandex.food";
  config.sender_slug = "WC78FQ64-6IN";
  config.template_url =
      "https://admin.eda.yandex-team.ru/places/{place_id}/edit";
  config.map_emails.emplace_back(EmailType{
      "callcenter",                 // type
      "Колл Центр",                 // name
      "eda-content@yandex-team.ru"  // email
  });
  config.map_emails.emplace_back(EmailType{
      "content",                    // type
      "Контент",                    // name
      "eda-content@yandex-team.ru"  // email
  });
  config.map_emails.emplace_back(EmailType{
      "partners",                    // type
      "Партнеры",                    // name
      "eda-partners@yandex-team.ru"  // email
  });
  config.reasons_lists.emplace_back(ReasonList{
      "REASON_FOR_CONTENT_WITH_STATUS",  // name
      std::vector<std::string>{
          "DISABLE_REASON_ON_REPAIR",
          "DISABLE_REASON_RESTAURANT_NO_NEED_PARTNERSHIP",
          "DISABLE_REASON_OFFER_RECONSIDERATION"}  // reasonsß
  });
  config.reasons_lists.emplace_back(ReasonList{
      "REASON_FOR_CONTENT_WITHOUT_STATUS",  // name
      std::vector<std::string>{"DISABLE_REASON_NEW_MENU_AWAIT",
                               "DISABLE_REASON_DESCRIPTION_ISSUES",
                               "DISABLE_REASON_CHANGE_OF_TIN"}  // reasons
  });
  return config;
}

std::vector<handlers::Place> MakePlaces() {
  std::vector<handlers::Place> data;
  std::string json_places = R"(
{
  "places": [
    {
      "auto_stop_rules_list": [],
      "address": "addres",
      "is_switching_on_requested": false,
      "is_available": true,
      "is_plus_enabled": false,
      "brand": {
        "business_type": "business_type_1",
        "slug": "slug1"
      },
      "country_code": "country_code1",
      "region_slug": "PENZA",
      "currency": {
        "code": "code1",
        "decimal_places": 1,
        "sign": "sign1"
      },
      "id": 1,
      "integration_type": "native",
      "name": "name1",
      "show_shipping_time": true,
      "slug": "slug1",
      "subscription": {
        "is_trial": true,
        "need_alerting_about_finishing_trial": false,
        "tariff_type": "free",
        "valid_until_iso": "2022-07-27T00:00:00+00:00"
      }
    },
    {
      "address": "addres",
      "is_switching_on_requested": false,
      "is_available": true,
      "is_plus_enabled": false,
      "brand": {
        "business_type": "business_type_2",
        "slug": "slug2"
      },
      "country_code": "country_code2",
      "currency": {
        "code": "code2",
        "decimal_places": 2,
        "sign": "sign2"
      },
      "id": 2,
      "integration_type": "native",
      "name": "name2",
      "show_shipping_time": true,
      "slug": "slug2",
      "subscription": {
        "is_trial": false,
        "need_alerting_about_finishing_trial": true,
        "tariff_type": "business",
        "valid_until_iso": "2022-07-26T00:00:00+00:00"
      }
    },
    {
      "address": "addres",
      "is_switching_on_requested": false,
      "is_available": false,
      "is_plus_enabled": false,
      "brand": {
        "business_type": "business_type_3",
        "slug": "slug3"
      },
      "country_code": "country_code3",
      "currency": {
        "code": "code3",
        "decimal_places": 3,
        "sign": "sign3"
      },
      "disable_details": {
        "available_at": "2020-07-28T09:07:12+00:00",
        "disable_at": "2020-07-28T09:07:12+00:00",
        "reason": 47,
        "status": 1
      },
      "id": 3,
      "integration_type": "native",
      "name": "name3",
      "show_shipping_time": true,
      "slug": "slug3",
      "subscription": {
        "is_trial": true,
        "need_alerting_about_finishing_trial": true,
        "tariff_type": "business_plus",
        "valid_until_iso": "2022-07-25T00:00:00+00:00"
      }
    },
    {
      "address": "addres",
      "is_switching_on_requested": false,
      "is_available": false,
      "is_plus_enabled": false,
      "brand": {
        "business_type": "business_type_4",
        "slug": "slug4"
      },
      "country_code": "country_code4",
      "currency": {
        "code": "code4",
        "decimal_places": 4,
        "sign": "sign4"
      },
      "disable_details": {
        "available_at": "2020-07-28T09:07:12+00:00",
        "disable_at": "2020-07-28T09:07:12+00:00",
        "reason": 47,
        "status": 1
      },
      "id": 4,
      "integration_type": "native",
      "name": "name4",
      "show_shipping_time": true,
      "slug": "slug4",
      "subscription": {
        "is_trial": false,
        "need_alerting_about_finishing_trial": false,
        "tariff_type": "free",
        "valid_until_iso": "2022-07-24T00:00:00+00:00"
      }
    },
    {
      "address": "addres",
      "is_switching_on_requested": false,
      "is_available": false,
      "is_plus_enabled": false,
      "brand": {
        "business_type": "business_type_5",
        "slug": "slug5"
      },
      "country_code": "country_code4",
      "currency": {
        "code": "code4",
        "decimal_places": 4,
        "sign": "sign4"
      },
      "disable_details": {
        "available_at": "2020-07-28T09:07:12+00:00",
        "disable_at": "2020-07-28T09:07:12+00:00",
        "reason": 123,
        "status": 1
      },
      "id": 5,
      "integration_type": "native",
      "name": "name5",
      "show_shipping_time": true,
      "slug": "slug4",
      "subscription": {
        "is_trial": true,
        "need_alerting_about_finishing_trial": false,
        "tariff_type": "business",
        "valid_until_iso": "2022-07-23T00:00:00+00:00"
      }
    },
    {
      "address": "addres",
      "is_switching_on_requested": false,
      "is_available": false,
      "is_plus_enabled": false,
      "brand": {
        "business_type": "business_type_6",
        "slug": "slug6"
      },
      "country_code": "country_code6",
      "currency": {
        "code": "code6",
        "decimal_places": 4,
        "sign": "sign6"
      },
      "disable_details": {
        "available_at": "2020-07-28T09:07:12+00:00",
        "disable_at": "2020-07-28T09:07:12+00:00",
        "reason": 0,
        "status": 1
      },
      "id": 6,
      "integration_type": "native",
      "name": "name6",
      "show_shipping_time": true,
      "slug": "slug6",
      "subscription": {
        "is_trial": true,
        "need_alerting_about_finishing_trial": false,
        "tariff_type": "business_plus",
        "valid_until_iso": "2022-07-22T00:00:00+00:00"
      }
    },
    {
      "address": "addres",
      "is_switching_on_requested": false,
      "is_available": false,
      "is_plus_enabled": false,
      "brand": {
        "business_type": "business_type_7",
        "slug": "slug7"
      },
      "country_code": "country_code7",
      "currency": {
        "code": "code7",
        "decimal_places": 7,
        "sign": "sign7"
      },
      "disable_details": {
        "available_at": "2020-07-28T09:07:12+00:00",
        "disable_at": "2020-07-28T09:07:12+00:00",
        "reason": 111,
        "status": 1
      },
      "id": 7,
      "integration_type": "native",
      "name": "name7",
      "show_shipping_time": true,
      "slug": "slug4",
      "subscription": {
        "is_trial": true,
        "need_alerting_about_finishing_trial": true,
        "tariff_type": "free",
        "valid_until_iso": "2022-07-21T00:00:00+00:00"
      }
    },
    {
      "address": "addres",
      "is_switching_on_requested": false,
      "is_available": false,
      "is_plus_enabled": false,
      "brand": {
        "business_type": "business_type_8",
        "slug": "slug8"
      },
      "country_code": "country_code8",
      "currency": {
        "code": "code8",
        "decimal_places": 8,
        "sign": "sign8"
      },
      "disable_details": {
        "available_at": "2020-07-28T09:07:12+00:00",
        "disable_at": "2020-07-28T09:07:12+00:00",
        "reason": 111,
        "status": 0
      },
      "id": 8,
      "integration_type": "native",
      "name": "name8",
      "show_shipping_time": true,
      "slug": "slug8",
      "subscription": {
        "is_trial": false,
        "need_alerting_about_finishing_trial": false,
        "tariff_type": "business",
        "valid_until_iso": "2022-07-20T00:00:00+00:00"
      }
    },
    {
      "address": "addres",
      "is_switching_on_requested": false,
      "is_available": false,
      "is_plus_enabled": false,
      "brand": {
        "business_type": "business_type_9",
        "slug": "slug9"
      },
      "country_code": "country_code8",
      "currency": {
        "code": "code8",
        "decimal_places": 8,
        "sign": "sign9"
      },
      "disable_details": {
        "available_at": "2020-07-28T09:07:12+00:00",
        "disable_at": "2020-07-28T09:07:12+00:00",
        "reason": 112,
        "status": 1
      },
      "id": 9,
      "integration_type": "native",
      "name": "name9",
      "show_shipping_time": true,
      "slug": "slug9",
      "subscription": {
        "is_trial": false,
        "need_alerting_about_finishing_trial": false,
        "tariff_type": "business_plus",
        "valid_until_iso": "2022-07-19T00:00:00+00:00"
      }
    },
    {
      "address": "addres",
      "is_switching_on_requested": false,
      "is_available": false,
      "is_plus_enabled": false,
      "brand": {
        "business_type": "business_type_9",
        "slug": "slug10"
      },
      "country_code": "country_code8",
      "currency": {
        "code": "code8",
        "decimal_places": 8,
        "sign": "sign9"
      },
      "disable_details": {
        "available_at": "2020-07-28T09:07:12+00:00",
        "disable_at": "2020-07-28T09:07:12+00:00",
        "reason": 112,
        "status": 0
      },
      "id": 10,
      "integration_type": "native",
      "name": "name10",
      "show_shipping_time": true,
      "slug": "slug10",
      "subscription": {
        "is_trial": true,
        "need_alerting_about_finishing_trial": true,
        "tariff_type": "business",
        "valid_until_iso": "2022-07-18T00:00:00+00:00"
      }
    }
  ]
}
)";
  const auto json = formats::json::FromString(json_places);
  for (const auto& item : json["places"]) {
    data.emplace_back(item.As<handlers::Place>());
  }
  return data;
}

struct PlaceActiveManagerComponentTest : public Test {
  ComponentImpl impl_;
  clients::sender::ClientGMock sender_gmock_;
  clients::eats_core::ClientGMock core_gmock_;
  PlaceActiveManagerComponentTest()
      : impl_(sender_gmock_, core_gmock_, kSenderToken, MakeDisabledDetails(),
              MakeDisabledList(), MakeEnableEmailConfig()) {}
};

TEST_F(PlaceActiveManagerComponentTest, FilterEmpty) {
  const auto filter = impl_.FilterDisabledPlaces({});
  ASSERT_TRUE(filter.list_enabled_request.empty());
  ASSERT_TRUE(filter.list_enabled_core.empty());
}

TEST_F(PlaceActiveManagerComponentTest, FilterDataWithoutLists) {
  impl_.UpdateConfig(DisabledDetails{}, DisabledList{}, EnableEmailConfig{});
  const auto filter = impl_.FilterDisabledPlaces({});
  ASSERT_TRUE(filter.list_enabled_request.empty());
  ASSERT_TRUE(filter.list_enabled_core.empty());
}

TEST_F(PlaceActiveManagerComponentTest, FilterData) {
  const auto places = MakePlaces();
  ASSERT_EQ(places.size(), 10);
  const auto filter = impl_.FilterDisabledPlaces(places);
  ASSERT_EQ(filter.list_enabled_request.size(), 5);
  ASSERT_EQ(filter.list_enabled_core.size(), 2);
}

TEST_F(PlaceActiveManagerComponentTest, SendInCore) {
  const auto places = MakePlaces();
  const auto filter = impl_.FilterDisabledPlaces(places);
  ASSERT_EQ(filter.list_enabled_core.size(), 2);
  clients::eats_core::v1_places_enable::post::Request request;

  for (const auto& item : filter.list_enabled_core) {
    request.body.place_ids.emplace_back(item.id);
  }

  EXPECT_CALL(core_gmock_, V1PlacesEnable(request, _))
      .WillOnce(
          Return(clients::eats_core::v1_places_enable::post::Response200{}));

  impl_.SendEnabledInCore(filter.list_enabled_core);
}

TEST_F(PlaceActiveManagerComponentTest, GetDisableReasonByNumber) {
  ASSERT_TRUE(impl_.GetDisableReasonByNumber(12000).empty());
  ASSERT_EQ(impl_.GetDisableReasonByNumber(112), "DISABLE_REASON_ON_REPAIR");
  ASSERT_EQ(impl_.GetDisableReasonByNumber(90),
            "DISABLE_REASON_AUTO_STOP_ORDER_CANCEL");
  ASSERT_EQ(impl_.GetDisableReasonByNumber(0), "DISABLE_REASON_MENU_UPDATE");
}

TEST_F(PlaceActiveManagerComponentTest, IsReasonInList) {
  ASSERT_TRUE(impl_.IsReasonInList("REASON_FOR_CONTENT_WITH_STATUS",
                                   "DISABLE_REASON_ON_REPAIR"));
  ASSERT_TRUE(
      impl_.IsReasonInList("REASON_FOR_CONTENT_WITH_STATUS",
                           "DISABLE_REASON_RESTAURANT_NO_NEED_PARTNERSHIP"));
  ASSERT_TRUE(impl_.IsReasonInList("REASON_FOR_CONTENT_WITH_STATUS",
                                   "DISABLE_REASON_OFFER_RECONSIDERATION"));
  ASSERT_TRUE(impl_.IsReasonInList("REASON_FOR_CONTENT_WITHOUT_STATUS",
                                   "DISABLE_REASON_NEW_MENU_AWAIT"));
  ASSERT_TRUE(impl_.IsReasonInList("REASON_FOR_CONTENT_WITHOUT_STATUS",
                                   "DISABLE_REASON_DESCRIPTION_ISSUES"));
  ASSERT_TRUE(impl_.IsReasonInList("REASON_FOR_CONTENT_WITHOUT_STATUS",
                                   "DISABLE_REASON_CHANGE_OF_TIN"));
  ASSERT_FALSE(impl_.IsReasonInList("REASON_FOR_CONTENT_WITHOUT_STATUS",
                                    "DISABLE_REASON_ON_REPAIR"));
  ASSERT_FALSE(
      impl_.IsReasonInList("REASON_FOR_CONTENT_WITHOUT_STATUS",
                           "DISABLE_REASON_RESTAURANT_NO_NEED_PARTNERSHIP"));
  ASSERT_FALSE(impl_.IsReasonInList("REASON_FOR_CONTENT_WITHOUT_STATUS",
                                    "DISABLE_REASON_OFFER_RECONSIDERATION"));
  ASSERT_FALSE(impl_.IsReasonInList("REASON_FOR_CONTENT_WITH_STATUS",
                                    "DISABLE_REASON_NEW_MENU_AWAIT"));
  ASSERT_FALSE(impl_.IsReasonInList("REASON_FOR_CONTENT_WITH_STATUS",
                                    "DISABLE_REASON_DESCRIPTION_ISSUES"));
  ASSERT_FALSE(impl_.IsReasonInList("REASON_FOR_CONTENT_WITH_STATUS",
                                    "DISABLE_REASON_CHANGE_OF_TIN"));
  ASSERT_FALSE(impl_.IsReasonInList("", ""));
  ASSERT_FALSE(impl_.IsReasonInList("abc", ""));
  ASSERT_FALSE(impl_.IsReasonInList("", "abc"));
  ASSERT_FALSE(impl_.IsReasonInList("abc", "abc"));
  ASSERT_FALSE(impl_.IsReasonInList("REASON_FOR_CONTENT_WITHOUT_STATUS", ""));
  ASSERT_FALSE(impl_.IsReasonInList("REASON_FOR_CONTENT_WITH_STATUS", ""));
}

TEST_F(PlaceActiveManagerComponentTest, GetEmailFromReason) {
  Place place;
  place.is_available = false;
  place.disable_details = ::handlers::PlaceDisabledetails{};
  place.disable_details->reason = 111;
  place.disable_details->status = 1;
  auto email_data = impl_.GetEmailFromReason(place);
  ASSERT_EQ(email_data.name, "Партнеры");
  ASSERT_EQ(email_data.email, "eda-partners@yandex-team.ru");
  place.disable_details->reason = 111;
  place.disable_details->status = 0;
  email_data = impl_.GetEmailFromReason(place);
  ASSERT_EQ(email_data.name, "Контент");
  ASSERT_EQ(email_data.email, "eda-content@yandex-team.ru");
  place.disable_details->reason = 101;
  place.disable_details->status = 0;
  email_data = impl_.GetEmailFromReason(place);
  ASSERT_EQ(email_data.name, "Колл Центр");
  ASSERT_EQ(email_data.email, "eda-content@yandex-team.ru");
  place.disable_details->reason = 112;
  place.disable_details->status = 1;
  email_data = impl_.GetEmailFromReason(place);
  ASSERT_EQ(email_data.name, "Контент");
  ASSERT_EQ(email_data.email, "eda-content@yandex-team.ru");
}

TEST_F(PlaceActiveManagerComponentTest, SendEmailRequestEnable) {
  Place place;
  place.is_available = false;
  place.id = 777;
  place.name = "Лев";
  place.disable_details = ::handlers::PlaceDisabledetails{};
  place.disable_details->reason = 111;
  place.disable_details->status = 1;
  auto email_data = impl_.GetEmailFromReason(place);
  ASSERT_EQ(email_data.name, "Партнеры");
  ASSERT_EQ(email_data.email, "eda-partners@yandex-team.ru");

  clients::sender::api_0_account_slug_transactional_campaign_slug_send::post::
      Request request;
  request.authorization =
      "Basic " + ::crypto::base64::Base64Encode(kSenderToken + ":");
  request.x_sender_i_am_sender = true;
  request.account_slug = "yandex.food";
  request.campaign_slug = "WC78FQ64-6IN";
  request.body.to = std::vector<::clients::sender::Recipient>{
      {email_data.email, email_data.name}};
  // Create args
  ::formats::json::ValueBuilder build_args;
  build_args["place_id"] = place.id;
  build_args["place_name"] = place.name;
  build_args["disable_reason"] = 111;
  build_args["place_url"] = "https://admin.eda.yandex-team.ru/places/777/edit";

  request.body.args =
      ::clients::sender::SenderRequestArgs{build_args.ExtractValue()};

  EXPECT_CALL(sender_gmock_,
              Api0AccountSlugTransactionalCampaignSlugSend(request, _))
      .WillOnce(Return(
          clients::sender::api_0_account_slug_transactional_campaign_slug_send::
              post::Response200{}));

  impl_.SendEmailRequestEnable(place);
}

TEST_F(PlaceActiveManagerComponentTest, AllFlowEnablePlacesComponent) {
  const auto places = MakePlaces();
  const auto filter = impl_.FilterDisabledPlaces(places);
  ASSERT_EQ(filter.list_enabled_core.size(), 2);
  if (!filter.list_enabled_core.empty()) {
    EXPECT_CALL(core_gmock_, V1PlacesEnable(_, _))
        .Times(1)
        .WillOnce(
            Return(clients::eats_core::v1_places_enable::post::Response200{}));

    impl_.SendEnabledInCore(filter.list_enabled_core);
  }
  ASSERT_EQ(filter.list_enabled_request.size(), 5);
  if (!filter.list_enabled_request.empty()) {
    EXPECT_CALL(sender_gmock_,
                Api0AccountSlugTransactionalCampaignSlugSend(_, _))
        .Times(filter.list_enabled_request.size())
        .WillRepeatedly(
            Return(clients::sender::
                       api_0_account_slug_transactional_campaign_slug_send::
                           post::Response200{}));

    for (const auto& place : filter.list_enabled_request) {
      impl_.SendEmailRequestEnable(place);
    }
  }
}

}  // namespace testing

namespace clients::eats_core::v1_places_enable::post {
inline bool operator==(const Request& lhs, const Request& rhs) {
  return std::tie(lhs.body.place_ids) == std::tie(rhs.body.place_ids);
}
}  // namespace clients::eats_core::v1_places_enable::post

namespace clients::sender::api_0_account_slug_transactional_campaign_slug_send::
    post {
inline bool operator==(const Request& lhs, const Request& rhs) {
  return std::tie(lhs.authorization, lhs.x_sender_i_am_sender, lhs.account_slug,
                  lhs.campaign_slug, lhs.body.to[0].email,
                  lhs.body.to[0].name) ==
         std::tie(rhs.authorization, rhs.x_sender_i_am_sender, rhs.account_slug,
                  rhs.campaign_slug, rhs.body.to[0].email, rhs.body.to[0].name);
}
// clang-format off
}  // namespace clients::sender::api_0_account_slug_transactional_campaign_slug_send::post
// clang-format on
