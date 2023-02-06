#include <userver/utest/utest.hpp>

#include <clients/eats-place-subscriptions/client_gmock.hpp>
#include <components/event_types.hpp>

namespace testing {

namespace components = ::eats_restapp_communications::components::event_types;
namespace types = ::eats_restapp_communications::types;

struct ComponentFixture {
  std::shared_ptr<StrictMock<clients::eats_place_subscriptions::ClientGMock>>
      subscriptions_mock = std::make_shared<
          StrictMock<clients::eats_place_subscriptions::ClientGMock>>();

  const std::vector<int64_t> places{1, 2, 3, 4};
  const std::vector<int64_t> filtered_places{2, 4};

  components::ComponentImpl component;

  ComponentFixture() : component(*subscriptions_mock) {}

  static components::EventSettings MakeEventSettings() {
    components::EventSettings settings;
    decltype(settings.event_communication_types)::value_type events;
    events.push_back({"known-event-email", {"email"}});
    events.push_back({"unknown-event-email", {"email"}});
    events.push_back({"known-event-telegram", {"telegram"}});
    events.push_back({"unknown-event-telegram", {"telegram"}});
    events.push_back({"known-event-both", {"telegram", "email"}});
    events.push_back({"unknown-email-event-both", {"telegram", "email"}});
    events.push_back({"unknown-telegram-event-both", {"telegram", "email"}});
    events.push_back({"unknown-event-both", {"telegram", "email"}});
    events.push_back({"event-unknown-type", {"email", "abacaba", "telegram"}});
    settings.event_communication_types = std::move(events);
    return settings;
  }

  static components::EmailSettings MakeEmailSettings() {
    components::EmailSettings settings;
    settings.email_events.push_back({"known-event-email", {}, {}});
    settings.email_events.push_back({"known-event-both", {}, {}});
    settings.email_events.push_back({"unknown-telegram-event-both", {}, {}});
    return settings;
  }

  static components::TelegramSettings MakeTelegramSettings() {
    components::TelegramSettings settings;
    settings.telegram_events.push_back({"known-event-telegram", {}});
    settings.telegram_events.push_back({"known-event-both", {}});
    settings.telegram_events.push_back({"unknown-email-event-both", {}});
    return settings;
  }

  static components::SubscriptionCheckSettings MakeSubscriptionCheckSettings() {
    components::SubscriptionCheckSettings settings;
    settings.features.push_back({"unknown-feature", {"dummy"}});
    settings.features.push_back({"boss_bot", {"event"}});
    return settings;
  }
};

using GetCommunicationTypeParams =
    std::tuple<std::string, std::vector<types::CommunicationType>>;

struct GetCommunicationTypeTest
    : public ComponentFixture,
      public TestWithParam<GetCommunicationTypeParams> {};

INSTANTIATE_TEST_SUITE_P(
    EventTypesTest, GetCommunicationTypeTest,
    Values(GetCommunicationTypeParams{"unknown-event",
                                      types::kDefaultCommunicationTypes},
           GetCommunicationTypeParams{"known-event-email",
                                      {types::CommunicationType::kEmail}},
           GetCommunicationTypeParams{"known-event-telegram",
                                      {types::CommunicationType::kTelegram}},
           GetCommunicationTypeParams{"known-event-both",
                                      {types::CommunicationType::kTelegram,
                                       types::CommunicationType::kEmail}},
           GetCommunicationTypeParams{"event-unknown-type",
                                      {types::CommunicationType::kEmail,
                                       types::CommunicationType::kTelegram}}));

TEST_P(GetCommunicationTypeTest, should_return_communication_types) {
  const auto [event_type, expected] = GetParam();
  ASSERT_EQ(component.GetCommunicationTypes(event_type, MakeEventSettings()),
            expected);
}

using IsInConfigParams = std::tuple<std::string, bool>;

struct IsInConfigTest : public ComponentFixture,
                        public TestWithParam<IsInConfigParams> {};

INSTANTIATE_TEST_SUITE_P(
    EventTypesTest, IsInConfigTest,
    Values(IsInConfigParams{"unknown-event", false},
           IsInConfigParams{"known-event-email", true},
           IsInConfigParams{"unknown-event-email", false},
           IsInConfigParams{"known-event-telegram", true},
           IsInConfigParams{"unknown-event-telegram", false},
           IsInConfigParams{"known-event-both", true},
           IsInConfigParams{"unknown-email-event-both", false},
           IsInConfigParams{"unknown-telegram-event-both", false},
           IsInConfigParams{"unknown-event-both", false}));

TEST_P(IsInConfigTest, should_check_event_in_configs) {
  const auto [event_type, expected] = GetParam();
  ASSERT_EQ(component.IsInConfig(event_type, MakeEventSettings(),
                                 MakeEmailSettings(), MakeTelegramSettings()),
            expected);
}

struct EventTypesFilterEnabledPlacesTest : public ComponentFixture,
                                           public Test {};

TEST_F(EventTypesFilterEnabledPlacesTest,
       should_do_nothing_on_type_not_in_config) {
  const auto result = component.FilterEnabledPlaces(
      "unknown-event", places, MakeSubscriptionCheckSettings());
  ASSERT_EQ(result, places);
}

TEST_F(EventTypesFilterEnabledPlacesTest,
       should_do_nothing_on_unknown_feature) {
  const auto result = component.FilterEnabledPlaces(
      "dummy", places, MakeSubscriptionCheckSettings());
  ASSERT_EQ(result, places);
}

TEST_F(EventTypesFilterEnabledPlacesTest,
       should_filter_by_subscriptions_response) {
  {
    namespace subscriptions = clients::eats_place_subscriptions::
        internal_eats_place_subscriptions_v1_feature_enabled_for_places::post;
    subscriptions::Request request;
    request.body.feature =
        clients::eats_place_subscriptions::FeatureType::kBossBot;
    request.body.place_ids = places;
    subscriptions::Response200 response200;
    response200.places.with_enabled_feature = filtered_places;
    EXPECT_CALL(
        *subscriptions_mock,
        InternalEatsPlaceSubscriptionsV1FeatureEnabledForPlaces(request, _))
        .WillOnce(Return(response200));
  }
  const auto result = component.FilterEnabledPlaces(
      "event", places, MakeSubscriptionCheckSettings());
  ASSERT_EQ(result, filtered_places);
}

}  // namespace testing

namespace clients::eats_place_subscriptions {
namespace internal_eats_place_subscriptions_v1_feature_enabled_for_places {
namespace post {
inline bool operator==(const Request& lhs, const Request& rhs) {
  return std::tie(lhs.body.feature, lhs.body.place_ids) ==
         std::tie(rhs.body.feature, rhs.body.place_ids);
}
}  // namespace post
}  // namespace internal_eats_place_subscriptions_v1_feature_enabled_for_places
}  // namespace clients::eats_place_subscriptions
