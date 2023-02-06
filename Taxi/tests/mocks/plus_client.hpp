#pragma once

#include <clients/plus/client_mock_base.hpp>

#include <functional>

namespace sweet_home::mocks {

namespace {

auto default_v_1_subscriptions_settings_put_handler =
    [](const clients::plus::v1_subscriptions_settings::put::Request& request) {
      clients::plus::v1_subscriptions_settings::put::Response200 response;
      response.version = std::to_string(std::stoi(request.body.version) + 1);
      response.settings.renew_subscription_by_plus =
          request.body.settings.renew_subscription_by_plus;
      return response;
    };

auto default_v_1_subscriptions_settings_get_handler =
    [](const clients::plus::v1_subscriptions_settings::get::
           Request& /*request*/) {
      clients::plus::v1_subscriptions_settings::get::Response200 response;
      response.version = "1";
      response.settings.renew_subscription_by_plus = true;
      return response;
    };

}  // namespace

using V1SubscriptionsSettingsPutHandler =
    std::function<clients::plus::v1_subscriptions_settings::put::Response200(
        const clients::plus::v1_subscriptions_settings::put::Request&)>;

using V1SubscriptionsSettingsGetHandler =
    std::function<clients::plus::v1_subscriptions_settings::get::Response200(
        const clients::plus::v1_subscriptions_settings::get::Request&)>;

class PlusClientMock : public clients::plus::ClientMockBase {
 private:
  V1SubscriptionsSettingsPutHandler v_1_subscriptions_settings_put_handler_;
  V1SubscriptionsSettingsGetHandler v_1_subscriptions_settings_get_handler_;

 public:
  PlusClientMock(const V1SubscriptionsSettingsPutHandler&
                     v_1_subscriptions_settings_put_handler = nullptr,
                 const V1SubscriptionsSettingsGetHandler&
                     v_1_subscriptions_settings_get_handler = nullptr)
      : v_1_subscriptions_settings_put_handler_(
            v_1_subscriptions_settings_put_handler),
        v_1_subscriptions_settings_get_handler_(
            v_1_subscriptions_settings_get_handler){};

  clients::plus::v1_subscriptions_settings::put::Response200
  V1SubscriptionsSettingsPut(
      const clients::plus::v1_subscriptions_settings::put::Request& request,
      const ::clients::codegen::CommandControl& /*command_control*/ = {})
      const override {
    if (!v_1_subscriptions_settings_put_handler_) {
      return default_v_1_subscriptions_settings_put_handler(request);
    }
    return v_1_subscriptions_settings_put_handler_(request);
  }

  clients::plus::ns_4_0_plus_v1_subscriptions_upgrade::post::Response
  upgradeSubscription(
      const clients::plus::ns_4_0_plus_v1_subscriptions_upgrade::post::
          Request& /*request*/,
      const ::clients::codegen::CommandControl& /*command_control*/ = {})
      const override {
    return clients::plus::ns_4_0_plus_v1_subscriptions_upgrade::post::
        Response200();
  };

  clients::plus::v1_subscriptions_settings::get::Response
  V1SubscriptionsSettingsGet(
      const clients::plus::v1_subscriptions_settings::get::Request& request,
      const ::clients::codegen::CommandControl& /*command_control*/ = {})
      const override {
    if (!v_1_subscriptions_settings_get_handler_) {
      return default_v_1_subscriptions_settings_get_handler(request);
    }
    return v_1_subscriptions_settings_get_handler_(request);
  };

  clients::plus::ns_4_0_plus_v1_subscriptions_purchase::post::Response purchase(
      const clients::plus::ns_4_0_plus_v1_subscriptions_purchase::post::
          Request& /*request*/,
      const ::clients::codegen::CommandControl& /*command_control*/ = {})
      const override {
    return clients::plus::ns_4_0_plus_v1_subscriptions_purchase::post::
        Response200();
  };

  clients::plus::ns_4_0_plus_v1_subscriptions_purchase::get::Response
  purchase_info(const clients::plus::ns_4_0_plus_v1_subscriptions_purchase::
                    get::Request& /*request*/,
                const ::clients::codegen::CommandControl& /*command_control*/ =
                    {}) const override {
    return clients::plus::ns_4_0_plus_v1_subscriptions_purchase::get::
        Response200();
  };
};

}  // namespace sweet_home::mocks
