#include <clients/antifraud/client_mock_base.hpp>
#include <clients/cardstorage/client_mock_base.hpp>
#include <clients/eats-coupons/client_mock_base.hpp>
#include <clients/eats-eaters/client_mock_base.hpp>
#include <clients/eats-promocodes/client_mock_base.hpp>
#include <clients/eda-promocodes/client_mock_base.hpp>
#include <clients/experiments3-proxy/client_mock_base.hpp>
#include <clients/grocery-communications/client_mock_base.hpp>
#include <clients/grocery-marketing/client_mock_base.hpp>
#include <clients/grocery-wms/client_mock_base.hpp>
#include <clients/maas/client_mock_base.hpp>
#include <clients/order-core/client_mock_base.hpp>
#include <clients/personal/client_mock_base.hpp>
#include <clients/statistics/client_mock_base.hpp>
#include <clients/sticker/client_mock_base.hpp>
#include <clients/stq-agent/client_mock_base.hpp>
#include <clients/taxi-exp-uservices/client_mock_base.hpp>
#include <clients/taxi-shared-payments/client_mock_base.hpp>
#include <clients/taxi-tariffs/client_mock_base.hpp>
#include <clients/territories/client_mock_base.hpp>
#include <clients/uantifraud/client_mock_base.hpp>
#include <clients/ucommunications/client_mock_base.hpp>
#include <clients/user-api/client_mock_base.hpp>
#include <clients/user-statistics/client_mock_base.hpp>
#include <clients/yql/client_mock_base.hpp>
#include <config/service_params.hpp>
#include <couponcheck/checks/check_error.hpp>
#include <couponcheck/checks/checks.hpp>
#include <couponcheck/models/context.hpp>
#include <couponcheck/models/coupon.hpp>
#include <testing/taxi_config.hpp>
#include <userver/concurrent/background_task_storage.hpp>
#include <userver/dynamic_config/storage_mock.hpp>
#include <userver/storages/secdist/secdist.hpp>

#include <gtest/gtest.h>

#include "couponcheck/models/usages_stats.hpp"
#include "grocery-coupons-mock.hpp"

namespace coupons::check {
namespace {

// dynamic_config::StorageMock patch_storage() {
//   return dynamic_config::MakeDefaultStorage(
//     {{taxi_config::COUPONS_EXTERNAL_VALIDATION_SERVICES, {"grocery"}}}
//   );
// }

}  // namespace

namespace grocery_coupons = ::clients::grocery_coupons;

void CheckUsageLimits(const Coupon& coupon,
                      const taxi_config::TaxiConfig& taxi_config,
                      const CouponUsagesStats& usages_stats);

struct Clients {
  clients::antifraud::ClientMockBase antifraud_client;
  clients::cardstorage::ClientMockBase cardstorage_client;
  clients::eats_coupons::ClientMockBase eats_coupons_client;
  clients::eats_eaters::ClientMockBase eats_eaters_client;
  clients::eats_promocodes::ClientMockBase eats_promocodes_client;
  clients::eda_promocodes::ClientMockBase eda_promocodes_client;
  clients::experiments3_proxy::ClientMockBase experiments3_proxy_client;
  grocery_coupons::MyGroceryCouponsClient grocery_coupons_client;
  clients::grocery_communications::ClientMockBase grocery_communications_client;
  clients::grocery_marketing::ClientMockBase grocery_marketing_client;
  clients::grocery_wms::ClientMockBase grocery_wms_client;
  clients::maas::ClientMockBase maas_client;
  clients::order_core::ClientMockBase order_core_client;
  clients::personal::ClientMockBase personal_client;
  clients::statistics::ClientMockBase statistics_client;
  clients::sticker::ClientMockBase sticker_client;
  clients::stq_agent::ClientMockBase stq_agent_client;
  clients::taxi_exp_uservices::ClientMockBase taxi_exp_client;
  clients::taxi_shared_payments::ClientMockBase taxi_shared_payments_client;
  clients::taxi_tariffs::ClientMockBase taxi_tariffs_client;
  clients::territories::ClientMockBase territories_client;
  clients::uantifraud::ClientMockBase uantifraud_client;
  clients::ucommunications::ClientMockBase ucommunications_client;
  clients::user_api::ClientMockBase user_api_client;
  clients::user_statistics::ClientMockBase user_statistics_client;
  clients::yql::ClientMockBase yql_client;
};

handlers::Dependencies MockCheckRequestContextDeps(
    const dynamic_config::Snapshot& config, Clients& clients,
    concurrent::BackgroundTaskStorage& bts,
    const storages::secdist::SecdistConfig& secdist,
    const configs::ServiceParams& service_params) {
  return {
      handlers::CampaignsCacheData(nullptr),        // campaigns
      handlers::ConsumerConfigsCacheData(nullptr),  // consumer_configs
      nullptr,                                      // countries
      handlers::CreatorConfigsCacheData(nullptr),   // creator_configs
      handlers::PromocodeSeriesCacheData(nullptr),  // promocode_series
      nullptr,                                      // tariff_settings
      caches::TranslationsData(nullptr),            // translations
      config,
      nullptr,  // metrics
      bts,

      {
          nullptr,         // VisibilityHelper
          secdist,         // SecdistConfig
          service_params,  // ServiceParams
          bts,             // Bts
      },                   // Extra

      nullptr,  // mongo_collections
      nullptr,  // pg_user_referrals

      clients.antifraud_client,
      clients.cardstorage_client,
      clients.eats_coupons_client,
      clients.eats_eaters_client,
      clients.eats_promocodes_client,
      clients.eda_promocodes_client,

      nullptr,  // experiments3
      clients.experiments3_proxy_client,
      clients.grocery_communications_client,
      clients.grocery_coupons_client,
      clients.grocery_marketing_client,
      clients.grocery_wms_client,
      clients.maas_client,
      clients.order_core_client,
      clients.personal_client,
      clients.statistics_client,
      clients.sticker_client,

      nullptr,  // stq

      clients.stq_agent_client,
      clients.taxi_exp_client,
      clients.taxi_shared_payments_client,
      clients.taxi_tariffs_client,

      clients.territories_client,
      clients.uantifraud_client,
      clients.ucommunications_client,
      clients.user_api_client,
      clients.user_statistics_client,
      clients.yql_client,

  };
}

coupons::check::Phone MockPhone() {
  const std::optional<std::string> phone_id = "6fff5faf15870bd76635d5e2";
  const std::optional<std::string> personal_phone_id = "123456789";
  const CouponFlow coupon_flow = coupons::check::CouponFlow::kTaxi;
  return coupons::check::Phone{phone_id, personal_phone_id, coupon_flow};
}

class ContextLifetimeWrapper {
  dynamic_config::Snapshot config_;
  Clients clients_;
  handlers::Dependencies deps_;
  concurrent::BackgroundTaskStorage bts_;
  storages::secdist::SecdistConfig secdist_;
  configs::ServiceParams service_params_;

 public:
  CheckRequestContext context_;

  ContextLifetimeWrapper(const dynamic_config::Snapshot config =
                             dynamic_config::GetDefaultSnapshot())
      : config_(config),
        deps_(MockCheckRequestContextDeps(config_, clients_, bts_, secdist_,
                                          service_params_)),
        context_({
            MockPhone(),
            {},                 // yandex_uid
            {},                 // zone_name
            {},                 // locale
            {},                 // country
            {},                 // time_zone
            {},                 // payment_options
            {},                 // zone_classes
            {},                 // apns_token
            {},                 // gcm_token
            {},                 // device_id
            {},                 // selected_class
            SourceApi::kCheck,  // source_api
            {},                 // payment_info
            {},                 // application
            {},                 // user_agent
            {},                 // user_ip
            {},                 // service_type
            {},                 // user_rides_provider
            {},                 // user_cards
            {},                 // glue
            {},                 // brand
            {},                 // order_id
            {},                 // service
            {},                 // bound_uids
            deps_.config.Get<taxi_config::ReferralConfig>(),
            deps_.config.Get<taxi_config::ApplicationConfig>(),
            config_,
            deps_,
            false,
            {},  // options
            {},  // payload
            {},  // handler
            {}   // eater_id
        }) {}

  void SetGroceryCouponsBehaviour(grocery_coupons::ClientBehaviour _behaviour) {
    clients_.grocery_coupons_client.behaviour = _behaviour;
  }
};

MultiUserCoupon MockMultiUserCoupon() {
  models::PromocodeSeries series;
  std::string code = "promocode";
  return MultiUserCoupon{series, code};
}

SingleUserCoupon MockSingleUserCoupon() {
  models::PromocodeSeries series;
  Promocode promocode;
  std::string code = "promocode";
  return SingleUserCoupon{promocode, series, code};
}

CheckExceptionCode RunCheck(CheckFunc check_func, Coupon& coupon,
                            const CheckRequestContext& context) {
  try {
    auto finalizer = check_func(coupon, context);
    if (finalizer) {
      finalizer(coupon);
    }
  } catch (CheckException& ex) {
    return ex.reason_code;
  }
  return CheckExceptionCode::ERROR_UNKNOWN;
}

CheckExceptionCode RunLimitsCheck(Coupon& coupon,
                                  const CheckRequestContext& context,
                                  const CouponUsagesStats& stats) {
  try {
    CheckUsageLimits(coupon, context.config, stats);
  } catch (CheckException& ex) {
    return ex.reason_code;
  }
  return CheckExceptionCode::ERROR_UNKNOWN;
}

CheckExceptionCode RunFirstLimitsCheck(Coupon& coupon,
                                       const CheckRequestContext& context) {
  try {
    CheckUsageLimitsFirstLimit(coupon, context);
  } catch (CheckException& ex) {
    return ex.reason_code;
  }
  return CheckExceptionCode::ERROR_UNKNOWN;
}

UTEST(CheckUsagesLimit, Percent) {
  auto coupon = MockMultiUserCoupon();
  coupon.series.user_limit = 1;
  coupon.series.percent = 10;
  coupon.series.value = 500;

  ContextLifetimeWrapper context_wrapper;
  auto context = context_wrapper.context_;

  CouponUsagesStats usages_stats;
  usages_stats.uses_by_coupon.cost_usage = 600;

  auto error = RunLimitsCheck(coupon, context, usages_stats);
  EXPECT_EQ(error, CheckExceptionCode::ERROR_PERCENTAGE_LIMIT_EXCEEDED);
}

UTEST(CheckUsagesLimit, PercentMultiorder) {
  auto coupon = MockMultiUserCoupon();
  coupon.series.user_limit = 3;
  coupon.series.percent = 10;
  coupon.series.value = 500;

  ContextLifetimeWrapper context_wrapper;
  auto context = context_wrapper.context_;

  CouponUsagesStats usages_stats;
  usages_stats.uses_by_coupon.uncommited_reserve_by_other_order = true;

  auto error = RunLimitsCheck(coupon, context, usages_stats);
  EXPECT_EQ(error, CheckExceptionCode::ERROR_MANUAL_ACTIVATION_IS_REQUIRED);
}

UTEST(CheckUsagesLimit, FirstLimitExceeded) {
  auto coupon = MockMultiUserCoupon();
  coupon.series.user_limit = 1;
  coupon.series.first_limit = 5;

  ContextLifetimeWrapper context_wrapper;
  auto context = context_wrapper.context_;

  context.gcm_token = "push_token";

  {
    UserRides stats;
    stats.user_rides = 5;
    context.user_rides_provider = stats;

    EXPECT_EQ(RunFirstLimitsCheck(coupon, context),
              CheckExceptionCode::ERROR_FIRST_LIMIT_EXCEEDED);
  }
}

UTEST(CheckUsagesLimit, UserLimitExceeded) {
  auto coupon = MockMultiUserCoupon();
  coupon.series.user_limit = 3;

  ContextLifetimeWrapper context_wrapper;
  auto context = context_wrapper.context_;

  CouponUsagesStats usages_stats;
  usages_stats.uses_by_user.all_uses = 3;

  auto error = RunLimitsCheck(coupon, context, usages_stats);
  EXPECT_EQ(error, CheckExceptionCode::ERROR_USER_LIMIT_EXCEEDED);
}

UTEST(CheckUsagesLimit, CountExceeded) {
  auto coupon = MockMultiUserCoupon();
  coupon.series.count = 3;

  ContextLifetimeWrapper context_wrapper;
  auto context = context_wrapper.context_;

  CouponUsagesStats usages_stats;
  usages_stats.uses_total = 3;

  auto error = RunLimitsCheck(coupon, context, usages_stats);
  EXPECT_EQ(error, CheckExceptionCode::ERROR_COUNT_EXCEEDED);
}

UTEST(CheckPrerequisites, DeviceId) {
  auto coupon = MockMultiUserCoupon();
  coupon.series.first_limit = 1;

  ContextLifetimeWrapper context_wrapper;
  auto context = context_wrapper.context_;

  context.application.type = "iphone";
  context.application.version = ua_parser::ApplicationVersion(5, 0, 0);
  context.application.platform_version = ua_parser::PlatformVersion(11, 0, 0);

  context.allow_empty_device_id = false;
  auto error_code = RunCheck(CheckPrerequisites, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_INVALID_CODE);

  context.allow_empty_device_id = true;
  error_code = RunCheck(CheckPrerequisites, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_UNKNOWN);
}

UTEST(CheckPrerequisites, MinPlatformVersion) {
  auto coupon = MockMultiUserCoupon();
  coupon.series.first_limit = 1;

  ContextLifetimeWrapper context_wrapper;
  auto context = context_wrapper.context_;

  context.application.type = "iphone";
  context.application.version = ua_parser::ApplicationVersion(5, 0, 0);
  context.application.platform_version = ua_parser::PlatformVersion(6, 0, 0);

  auto error_code = RunCheck(CheckPrerequisites, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_INVALID_PLATFORM_VERSION);
}

UTEST(CheckPrerequisites, MinAppVersion) {
  auto coupon = MockMultiUserCoupon();
  coupon.series.first_limit = 1;

  ContextLifetimeWrapper context_wrapper;
  auto context = context_wrapper.context_;

  context.application.type = "iphone";
  context.application.version = ua_parser::ApplicationVersion(2, 0, 0);
  context.application.platform_version = ua_parser::PlatformVersion(11, 1, 0);

  auto error_code = RunCheck(CheckPrerequisites, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_INVALID_APP_VERSION);
}

UTEST(CheckPrerequisites, MinVersion) {
  auto coupon = MockMultiUserCoupon();
  coupon.series.first_limit = 0;

  ContextLifetimeWrapper context_wrapper;
  auto context = context_wrapper.context_;

  auto error_code = RunCheck(CheckPrerequisites, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_UNKNOWN);

  coupon.series.first_limit = 1;
  error_code = RunCheck(CheckPrerequisites, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_INVALID_APPLICATION);
}

UTEST(CheckApplication, One) {
  auto coupon = MockMultiUserCoupon();

  ContextLifetimeWrapper context_wrapper;
  auto context = context_wrapper.context_;

  auto error_code = RunCheck(CheckApplication, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_UNKNOWN);

  context.application.type = "uber_iphone";

  coupon.series.applications = std::nullopt;
  error_code = RunCheck(CheckApplication, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_INVALID_APPLICATION);

  coupon.series.applications = std::unordered_set<std::string>{};
  error_code = RunCheck(CheckApplication, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_INVALID_APPLICATION);

  coupon.series.applications = std::unordered_set<std::string>{"android"};
  error_code = RunCheck(CheckApplication, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_INVALID_APPLICATION);
}

UTEST(CheckDates, Finish) {
  auto coupon = MockMultiUserCoupon();
  coupon.series.finish =
      std::chrono::system_clock::now() - std::chrono::hours(100000);

  ContextLifetimeWrapper context_wrapper;
  auto context = context_wrapper.context_;
  context.time_zone = "Europe/Moscow";

  auto error_code = RunCheck(CheckDates, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_TOO_LATE);
}

UTEST(CheckDates, Start) {
  auto coupon = MockMultiUserCoupon();
  coupon.series.start =
      std::chrono::system_clock::now() + std::chrono::hours(100000);

  ContextLifetimeWrapper context_wrapper;
  auto context = context_wrapper.context_;
  context.time_zone = "Europe/Moscow";

  auto error_code = RunCheck(CheckDates, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_TOO_EARLY);
}

UTEST(CheckCity, Country) {
  auto coupon = MockMultiUserCoupon();

  ContextLifetimeWrapper context_wrapper;
  auto context = context_wrapper.context_;

  context.payment_options = ::utils::helpers::PaymentOptions{
      std::vector<std::string>{"coupon"}, "zone"};
  context.country = "rus";
  coupon.series.country = "usa";

  auto error_code = RunCheck(CheckCity, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_INVALID_COUNTRY);
}

UTEST(CheckCity, Payment) {
  auto coupon = MockMultiUserCoupon();

  ContextLifetimeWrapper context_wrapper;
  auto context = context_wrapper.context_;

  context.payment_options = ::utils::helpers::PaymentOptions{
      std::vector<std::string>{"cash"}, "zone"};
  auto error_code = RunCheck(CheckCity, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_INVALID_CITY);
}

UTEST(CheckCity, Zones) {
  auto coupon = MockMultiUserCoupon();

  ContextLifetimeWrapper context_wrapper;
  auto context = context_wrapper.context_;

  context.zone_name = "moscow";
  coupon.series.zones = std::unordered_set<std::string>{"spb"};
  auto error_code = RunCheck(CheckCity, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_INVALID_CITY);
}

UTEST(CheckClass, One) {
  auto coupon = MockMultiUserCoupon();

  ContextLifetimeWrapper context_wrapper;
  auto context = context_wrapper.context_;

  auto error_code = RunCheck(CheckClass, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_UNKNOWN);

  coupon.series.classes = std::unordered_set<std::string>{"econom"};
  context.zone_classes = {"business"};
  error_code = RunCheck(CheckClass, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_UNSUPPORTED_ZONE_CLASSES);
}

UTEST(CheckPaymentMethod, CreditCard) {
  auto coupon = MockMultiUserCoupon();

  ContextLifetimeWrapper context_wrapper;
  auto context = context_wrapper.context_;

  CheckExceptionCode error_code;

  coupon.series.payment_methods = std::unordered_set<std::string>{"card"};
  context.payment_info.type = "cash";
  error_code = RunCheck(CheckPaymentMethod, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_CREDITCARD_ONLY);

  coupon.series.payment_methods = std::unordered_set<std::string>{};
  context.payment_info.type = "business_account";
  error_code = RunCheck(CheckPaymentMethod, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_UNKNOWN);

  coupon.series.payment_methods = std::unordered_set<std::string>{"card"};
  context.payment_info.type = "card";
  error_code = RunCheck(CheckPaymentMethod, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_UNKNOWN);

  coupon.series.payment_methods = std::unordered_set<std::string>{
      "family_account", "business_account", "corp"};
  context.payment_info.type = "coop_account";
  context.payment_info.method_id = "business-123";
  error_code = RunCheck(CheckPaymentMethod, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_UNKNOWN);
}

UTEST(CheckBincode, One) {
  auto coupon = MockMultiUserCoupon();

  ContextLifetimeWrapper context_wrapper;
  auto context = context_wrapper.context_;

  context.payment_info.type = "card";
  context.payment_info.method_id = "method_id";
  auto error_code = RunCheck(CheckBincode, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_UNKNOWN);

  coupon.series.bin_ranges =
      std::vector<std::vector<std::string>>{{"400000", "500000"}};
  error_code = RunCheck(CheckBincode, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_INVALID_BINCODE);

  CheckRequestContext::Card card;
  card.number = "450000 00000";
  card.card_id = "method_id";
  context.user_cards.cards.push_back(card);
  error_code = RunCheck(CheckBincode, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_UNKNOWN);
}

UTEST(CheckPaymentMethod, Corp) {
  auto coupon = MockMultiUserCoupon();

  ContextLifetimeWrapper context_wrapper;
  auto context = context_wrapper.context_;

  context.payment_info.type = "cash";
  auto error_code = RunCheck(CheckPaymentMethod, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_UNKNOWN);

  context.payment_info.type = "corp";
  error_code = RunCheck(CheckPaymentMethod, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_CORP_NOT_ALLOWED);
}

UTEST(CheckSelfRef, One) {
  auto coupon = MockMultiUserCoupon();

  ContextLifetimeWrapper context_wrapper;
  auto context = context_wrapper.context_;

  coupon.series.type = models::PromocodeSeriesType::SingleUser;
  auto error_code = RunCheck(CheckSelfRef, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_UNKNOWN);

  coupon.series.type = models::PromocodeSeriesType::Referral;
  coupon.series.referral_creator = {
      "yandex_uid",
      std::optional(formats::bson::Oid(context.phone.GetPhoneValue()))};
  error_code = RunCheck(CheckSelfRef, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_SELF_NOT_ALLOWED);
}

UTEST(CheckSingleUser, Revoked) {
  auto coupon = MockSingleUserCoupon();

  ContextLifetimeWrapper context_wrapper;
  auto context = context_wrapper.context_;

  CheckRequestContext::Card card;
  card.valid = true;
  card.possible_moneyless = false;
  card.persistent_id = "id";
  context.user_cards.cards.emplace_back(card);

  auto error_code = RunCheck(CheckSingleUser, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_UNKNOWN);

  coupon.promocode.revoked =
      Revoked{"login", "ticket", std::chrono::system_clock::now()};
  error_code = RunCheck(CheckSingleUser, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_REVOKED);
}

UTEST(CheckSingleUser, PhoneId) {
  auto coupon = MockSingleUserCoupon();

  ContextLifetimeWrapper context_wrapper;
  auto context = context_wrapper.context_;

  CheckRequestContext::Card card;
  card.valid = true;
  card.possible_moneyless = false;
  card.persistent_id = "id";
  context.user_cards.cards.emplace_back(card);

  auto error_code = RunCheck(CheckSingleUser, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_UNKNOWN);

  coupon.promocode.phone_id = formats::bson::Oid("5bbb5faf15870bd76635d5e2");
  error_code = RunCheck(CheckSingleUser, coupon, context);
  EXPECT_EQ(error_code,
            CheckExceptionCode::ERROR_MANUAL_ACTIVATION_IS_REQUIRED);
}

UTEST(CheckSingleUser, CardFailure) {
  auto coupon = MockSingleUserCoupon();

  ContextLifetimeWrapper context_wrapper;
  auto context = context_wrapper.context_;

  CheckRequestContext::Card card;
  card.valid = true;
  card.possible_moneyless = true;
  card.persistent_id = "id";
  context.user_cards.cards.emplace_back(card);

  auto error_code = RunCheck(CheckSingleUser, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_CREDITCARD_MONEYLESS);
}

UTEST(CheckSingleUser, CardIsNotCheckedForSupportPromocodes) {
  auto storage = dynamic_config::MakeDefaultStorage(
      {{taxi_config::COUPONS_EATS_COUPONS_PARAMS,
        {{"skip_phone_check_for_support", {"eats"}}}}});

  const ContextLifetimeWrapper context_wrapper(storage.GetSnapshot());
  auto context = context_wrapper.context_;

  CheckRequestContext::Card card;
  card.valid = true;
  card.possible_moneyless = true;
  card.persistent_id = "id";
  context.user_cards.cards.emplace_back(card);

  auto coupon_should_be_skipped = MockSingleUserCoupon();
  coupon_should_be_skipped.series.services = {"eats"};
  coupon_should_be_skipped.series.for_support = true;

  auto coupon_should_not_be_skipped = MockSingleUserCoupon();
  coupon_should_not_be_skipped.series.services = {"eats", "taxi"};

  auto error_code =
      RunCheck(CheckSingleUser, coupon_should_not_be_skipped, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_CREDITCARD_MONEYLESS);

  error_code = RunCheck(CheckSingleUser, coupon_should_be_skipped, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_UNKNOWN);
}

UTEST(CheckManualActivationIsRequired, One) {
  auto coupon = MockMultiUserCoupon();

  ContextLifetimeWrapper context_wrapper;
  auto context = context_wrapper.context_;

  auto error_code = RunCheck(CheckManualActivationIsRequired, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_UNKNOWN);

  coupon.series.requires_activation_after =
      std::chrono::system_clock::now() - std::chrono::hours(1000);
  error_code = RunCheck(CheckManualActivationIsRequired, coupon, context);
  EXPECT_EQ(error_code,
            CheckExceptionCode::ERROR_MANUAL_ACTIVATION_IS_REQUIRED);
}

UTEST(CheckCardIsOk, One) {
  auto coupon = MockMultiUserCoupon();

  ContextLifetimeWrapper context_wrapper;
  auto context = context_wrapper.context_;

  CheckRequestContext::Card card;
  card.valid = true;
  card.possible_moneyless = false;
  card.persistent_id = "id";
  context.user_cards.cards.emplace_back(card);

  auto error_code = RunCheck(CheckCardIsOK, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_UNKNOWN);
  card.possible_moneyless = true;
  context.user_cards.cards.front() = card;

  error_code = RunCheck(CheckCardIsOK, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_CREDITCARD_MONEYLESS);
}

using Services = std::unordered_set<std::string>;

UTEST(CheckServiceConformity, OkDefaultOrTaxi) {
  auto coupon = MockSingleUserCoupon();

  ContextLifetimeWrapper context_wrapper;
  auto context = context_wrapper.context_;

  const std::vector<std::optional<std::string>> taxiLikeServices{kTaxiService,
                                                                 std::nullopt};
  const std::vector<std::optional<Services>> taxiLikeServiceSets{
      Services{kTaxiService}, std::nullopt};

  for (const auto& service : taxiLikeServices) {
    for (const auto& services : taxiLikeServiceSets) {
      coupon.series.services = services;
      context.service = service;

      auto error_code = RunCheck(CheckServiceConformity, coupon, context);
      EXPECT_EQ(error_code, CheckExceptionCode::ERROR_UNKNOWN);
    }
  }
}

const std::string kLavkaService = "grocery";

UTEST(CheckServiceConformity, OkNotTaxi) {
  auto coupon = MockSingleUserCoupon();

  ContextLifetimeWrapper context_wrapper;
  auto context = context_wrapper.context_;

  coupon.series.services = std::optional<Services>{Services{kLavkaService}};
  context.service = kLavkaService;

  auto error_code = RunCheck(CheckServiceConformity, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_UNKNOWN);
}

UTEST(CheckServiceConformity, ErrNotConforming) {
  auto coupon = MockSingleUserCoupon();

  ContextLifetimeWrapper context_wrapper;
  auto context = context_wrapper.context_;

  const std::vector<std::string> taxiLikeServices{kLavkaService,
                                                  "someOtherService"};
  const std::vector<std::optional<Services>> taxiLikeServiceSets{
      Services{kTaxiService}, std::nullopt};

  for (const auto& service : taxiLikeServices) {
    for (const auto& services : taxiLikeServiceSets) {
      coupon.series.services = services;
      context.service = service;

      auto error_code = RunCheck(CheckServiceConformity, coupon, context);
      EXPECT_EQ(error_code, CheckExceptionCode::ERROR_INVALID_SERVICE);
    }
  }
}

UTEST(CheckExternal, OkTaxi) {
  auto storage = dynamic_config::MakeDefaultStorage(
      {{taxi_config::COUPONS_EXTERNAL_VALIDATION_SERVICES, {"grocery"}}});
  auto coupon = MockSingleUserCoupon();

  ContextLifetimeWrapper context_wrapper(storage.GetSnapshot());
  auto context = context_wrapper.context_;

  context_wrapper.SetGroceryCouponsBehaviour(
      grocery_coupons::ClientBehaviour::kNotCalled);
  coupon.series.services = coupon.series.GetServicesOrDefault();
  context.service = coupons::check::kTaxiService;

  auto error_code = RunCheck(CheckExternalService, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_UNKNOWN);
}

UTEST(CheckExternal, OkLavka) {
  auto storage = dynamic_config::MakeDefaultStorage(
      {{taxi_config::COUPONS_EXTERNAL_VALIDATION_SERVICES, {"grocery"}}});
  auto coupon = MockSingleUserCoupon();

  ContextLifetimeWrapper context_wrapper(storage.GetSnapshot());

  auto context = context_wrapper.context_;

  context_wrapper.SetGroceryCouponsBehaviour(
      grocery_coupons::ClientBehaviour::kOk);
  coupon.series.services = std::optional<Services>{Services{kLavkaService}};
  context.service = coupons::check::kLavkaService;

  auto error_code = RunCheck(CheckExternalService, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_UNKNOWN);
}

UTEST(CheckExternal, InvalidLavka) {
  auto storage = dynamic_config::MakeDefaultStorage(
      {{taxi_config::COUPONS_EXTERNAL_VALIDATION_SERVICES, {"grocery"}}});
  auto coupon = MockSingleUserCoupon();

  ContextLifetimeWrapper context_wrapper(storage.GetSnapshot());

  auto context = context_wrapper.context_;

  context_wrapper.SetGroceryCouponsBehaviour(
      grocery_coupons::ClientBehaviour::kInvalid);
  coupon.series.services = std::optional<Services>{Services{kLavkaService}};
  context.service = coupons::check::kLavkaService;

  auto error_code = RunCheck(CheckExternalService, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_EXTERNAL_VALIDATION_FAILED);
}

UTEST(CheckExternal, TaxiNotInLavka) {
  auto storage = dynamic_config::MakeDefaultStorage(
      {{taxi_config::COUPONS_EXTERNAL_VALIDATION_SERVICES, {"grocery"}}});
  auto coupon = MockSingleUserCoupon();

  ContextLifetimeWrapper context_wrapper(storage.GetSnapshot());

  auto context = context_wrapper.context_;

  context_wrapper.SetGroceryCouponsBehaviour(
      grocery_coupons::ClientBehaviour::kNotCalled);
  coupon.series.services = std::optional<Services>{Services{kLavkaService}};
  context.service = coupons::check::kTaxiService;

  auto error_code = RunCheck(CheckExternalService, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_INVALID_SERVICE);
}

UTEST(CheckExternal, TaxiInEmpty) {
  auto storage = dynamic_config::MakeDefaultStorage(
      {{taxi_config::COUPONS_EXTERNAL_VALIDATION_SERVICES, {"grocery"}}});
  auto coupon = MockSingleUserCoupon();

  ContextLifetimeWrapper context_wrapper(storage.GetSnapshot());

  auto context = context_wrapper.context_;

  context_wrapper.SetGroceryCouponsBehaviour(
      grocery_coupons::ClientBehaviour::kNotCalled);
  coupon.series.services = std::nullopt;
  context.service = coupons::check::kTaxiService;

  auto error_code = RunCheck(CheckExternalService, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_UNKNOWN);
}

UTEST(CheckExternal, LavkaNotInDefault) {
  auto storage = dynamic_config::MakeDefaultStorage(
      {{taxi_config::COUPONS_EXTERNAL_VALIDATION_SERVICES, {"grocery"}}});
  auto coupon = MockSingleUserCoupon();

  ContextLifetimeWrapper context_wrapper(storage.GetSnapshot());

  auto context = context_wrapper.context_;

  context_wrapper.SetGroceryCouponsBehaviour(
      grocery_coupons::ClientBehaviour::kNotCalled);
  coupon.series.services = coupon.series.GetServicesOrDefault();
  context.service = coupons::check::kLavkaService;

  auto error_code = RunCheck(CheckExternalService, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_INVALID_SERVICE);
}

UTEST(CheckExternal, LavkaNotInEmpty) {
  auto storage = dynamic_config::MakeDefaultStorage(
      {{taxi_config::COUPONS_EXTERNAL_VALIDATION_SERVICES, {"grocery"}}});
  auto coupon = MockSingleUserCoupon();

  ContextLifetimeWrapper context_wrapper(storage.GetSnapshot());

  auto context = context_wrapper.context_;

  context_wrapper.SetGroceryCouponsBehaviour(
      grocery_coupons::ClientBehaviour::kNotCalled);
  coupon.series.services = std::nullopt;
  context.service = coupons::check::kLavkaService;

  auto error_code = RunCheck(CheckExternalService, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_INVALID_SERVICE);
}

UTEST(CheckExternal, Err400Handling) {
  auto storage = dynamic_config::MakeDefaultStorage(
      {{taxi_config::COUPONS_EXTERNAL_VALIDATION_SERVICES, {"grocery"}}});
  auto coupon = MockSingleUserCoupon();

  ContextLifetimeWrapper context_wrapper(storage.GetSnapshot());

  auto context = context_wrapper.context_;

  context_wrapper.SetGroceryCouponsBehaviour(
      grocery_coupons::ClientBehaviour::kErr400);
  coupon.series.services = std::optional<Services>{Services{kLavkaService}};
  context.service = coupons::check::kLavkaService;

  auto error_code = RunCheck(CheckExternalService, coupon, context);
  EXPECT_EQ(error_code, CheckExceptionCode::ERROR_EXTERNAL_VALIDATION_FAILED);
}

UTEST(CheckFirstUsage, FirstUsageHandlingWithClasses) {
  auto coupon = MockSingleUserCoupon();

  ContextLifetimeWrapper context_wrapper;
  auto context = context_wrapper.context_;

  constexpr auto user_rides = 382;
  coupon.series.user_limit = 8;
  coupon.series.first_usage_by_classes = true;
  coupon.series.classes = {"test_class_1", "test_class_2"};

  ::utils::helpers::GroupCounter group_counter;
  for (const auto& class_name : *coupon.series.classes) {
    group_counter.Insert(class_name, "test", coupon.series.user_limit + 1);
  }

  context.user_rides_provider =
      UserRides{user_rides, {}, group_counter, {}, {}};

  auto error_code = RunCheck(CheckFirstUsage, coupon, context);
  EXPECT_EQ(error_code,
            coupons::check::CheckExceptionCode::ERROR_FIRST_RIDE_BY_CLASSES);
}

UTEST(CheckFirstUsage, FirstUsageHandlingWithPaymentMethods) {
  auto coupon = MockSingleUserCoupon();

  ContextLifetimeWrapper context_wrapper;
  auto context = context_wrapper.context_;

  constexpr auto user_rides = 283;
  coupon.series.user_limit = 82;
  coupon.series.first_usage_by_payment_methods = true;
  coupon.series.payment_methods = {"test_payment_method_1",
                                   "test_payment_method_2"};

  ::utils::helpers::GroupCounter group_counter;
  for (const auto& payment_method : coupon.series.payment_methods) {
    group_counter.Insert("test", payment_method, coupon.series.user_limit + 1);
  }

  context.user_rides_provider =
      UserRides{user_rides, {}, group_counter, {}, {}};

  auto error_code = RunCheck(CheckFirstUsage, coupon, context);
  EXPECT_EQ(
      error_code,
      coupons::check::CheckExceptionCode::ERROR_FIRST_RIDE_BY_PAYMENT_METHODS);
}

UTEST(CheckFirstUsage, FirstUsageHandlingWithClassesAndPaymentsMethods) {
  auto coupon = MockSingleUserCoupon();

  ContextLifetimeWrapper context_wrapper;
  auto context = context_wrapper.context_;

  constexpr auto user_rides = 10;
  coupon.series.user_limit = 25;
  coupon.series.first_usage_by_classes = true;
  coupon.series.classes = {"test_class_1", "test_class_2"};
  coupon.series.first_usage_by_payment_methods = true;
  coupon.series.payment_methods = {"test_payment_method_1",
                                   "test_payment_method_2"};

  ::utils::helpers::GroupCounter group_counter;
  for (const auto& class_name : *coupon.series.classes) {
    for (const auto& payment_method : coupon.series.payment_methods) {
      group_counter.Insert(class_name, payment_method,
                           coupon.series.user_limit + 1);
    }
  }

  context.user_rides_provider =
      UserRides{user_rides, {}, group_counter, {}, {}};

  auto error_code = RunCheck(CheckFirstUsage, coupon, context);
  EXPECT_EQ(error_code, coupons::check::CheckExceptionCode::
                            ERROR_FIRST_RIDE_BY_CLASSES_AND_PAYMENT_METHODS);
}

}  // namespace coupons::check
