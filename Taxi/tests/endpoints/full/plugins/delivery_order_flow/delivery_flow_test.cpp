#include "common_test.hpp"

#include <experiments3/delivery_slow_courier_flow.hpp>
#include <taxi_config/variables/CARGO_C2C_ROUTESTATS_TARIFF_UNAVAILABLE_SETTINGS.hpp>
#include <taxi_config/variables/ORDER_FLOW_DELIVERY_DISABLED_PAYMENT_TYPES.hpp>
#include <tests/context/translator_mock_test.hpp>

namespace routestats::plugins::delivery_order_flow {

using namespace clients::cargo_c2c::v1_delivery_estimate::post;

UTEST(DeliveryOrderFlowTest, BasicTest) {
  PluginTest test;
  const auto service_levels = test.RunDeliveryPlugin();
  std::set<std::string> delivery_classes = {"express", "courier"};

  ASSERT_EQ(test.CargoC2cTimesCalled(), 1);
  ASSERT_EQ(service_levels.size(), 2);

  for (const auto& level : service_levels) {
    ASSERT_TRUE(delivery_classes.count(level.Class()));
  }
}

UTEST(DeliveryOrderFlowTest, DisabledPaymentType) {
  handlers::RequestPayment payment;
  payment.type = "yandex-card";
  payment.payment_method_id = "yandex-card-47474747";

  auto config_storage = dynamic_config::MakeDefaultStorage({
      {taxi_config::ORDER_FLOW_DELIVERY_DISABLED_PAYMENT_TYPES,
       {{"yandex-card"}, {} /* complement_types */}},
  });
  const auto config =
      std::make_shared<test::TaxiConfigsMock>(std::move(config_storage));

  ContextOverrides overrides;
  overrides.payment = payment;
  overrides.config = config;

  PluginTest test(overrides);
  const auto service_levels = test.RunDeliveryPlugin();

  ASSERT_EQ(test.CargoC2cTimesCalled(), 0);
  ASSERT_EQ(service_levels.size(), 2);
}

UTEST(DeliveryOrderFlowTest, EnabledPaymentType) {
  auto config_storage = dynamic_config::MakeDefaultStorage({
      {taxi_config::ORDER_FLOW_DELIVERY_DISABLED_PAYMENT_TYPES,
       {{"yandex-card"}, {} /* complement_types */}},
  });
  const auto config =
      std::make_shared<test::TaxiConfigsMock>(std::move(config_storage));

  ContextOverrides overrides;
  overrides.config = config;

  PluginTest test(overrides);
  const auto service_levels = test.RunDeliveryPlugin();

  ASSERT_EQ(test.CargoC2cTimesCalled(), 1);
  ASSERT_EQ(service_levels.size(), 2);
}

UTEST(DeliveryOrderFlowTest, OrderAlwaysAllowed1) {
  routestats::full::GetConfigsMappedData experiments_mapped_data =
      [](const experiments3::models::KwargsBuilderWithConsumer &
         /*kwargs*/) -> experiments3::models::ClientsCache::MappedData {
    auto result = experiments3::models::ClientsCache::MappedData{};

    result[experiments3::DeliverySlowCourierFlow::kName] =
        experiments3::models::ExperimentResult{
            experiments3::DeliverySlowCourierFlow::kName,
            LoadJsonFromFile("slow_courier_flow.json"),
            experiments3::models::ResultMetaInfo{}};
    return result;
  };

  const auto faulty_handler = [&](const C2cRequest& request) -> C2cResponse {
    C2cResponse response;
    for (const auto& tariff : request.body.taxi_tariffs) {
      clients::cargo_c2c::TariffClassEstimatingResult estimation;
      estimation.taxi_tariff = tariff.taxi_tariff;
      estimation.type = "succeed";
      estimation.offer_id = "offer_id_1";
      estimation.price = "4747.4747";
      estimation.currency = "RUB";
      estimation.decision = clients::cargo_c2c::OfferDecision::kOrderProhibited;
      response.estimations.push_back((Response200EstimationsA)estimation);
    }
    return response;
  };

  ContextOverrides overrides;
  overrides.get_experiments_mapped_data = experiments_mapped_data;
  overrides.c2c_handler = faulty_handler;

  PluginTest test(overrides);
  const auto service_levels = test.RunDeliveryPlugin();

  ASSERT_EQ(test.CargoC2cTimesCalled(), 1);
  ASSERT_EQ(service_levels.size(), 2);
  ASSERT_EQ(service_levels[0].tariff_unavailable, std::nullopt);
  ASSERT_EQ(service_levels[0].is_fixed_price, true);
}

UTEST(DeliveryOrderFlowTest, OrderAlwaysAllowed2) {
  routestats::full::GetConfigsMappedData experiments_mapped_data =
      [](const experiments3::models::KwargsBuilderWithConsumer &
         /*kwargs*/) -> experiments3::models::ClientsCache::MappedData {
    auto result = experiments3::models::ClientsCache::MappedData{};

    result[experiments3::DeliverySlowCourierFlow::kName] =
        experiments3::models::ExperimentResult{
            experiments3::DeliverySlowCourierFlow::kName,
            LoadJsonFromFile("slow_courier_flow.json"),
            experiments3::models::ResultMetaInfo{}};
    return result;
  };
  const routestats::core::TariffUnavailable err = {
      "no_free_cars_nearby", "Привет! Я такси без машин :("};

  ContextOverrides overrides;
  overrides.get_experiments_mapped_data = experiments_mapped_data;
  overrides.tariff_unavailable = err;

  PluginTest test(overrides);
  const auto service_levels = test.RunDeliveryPlugin();

  ASSERT_EQ(test.CargoC2cTimesCalled(), 1);
  ASSERT_EQ(service_levels.size(), 2);
  ASSERT_EQ(service_levels[0].tariff_unavailable, std::nullopt);
  ASSERT_EQ(service_levels[0].is_fixed_price, true);
}

UTEST(DeliveryOrderFlowTest, OrderFailsWhileNoExp) {
  const auto faulty_handler = [&](const C2cRequest& request) -> C2cResponse {
    C2cResponse response;
    for (const auto& tariff : request.body.taxi_tariffs) {
      clients::cargo_c2c::TariffClassEstimatingResult estimation;
      estimation.taxi_tariff = tariff.taxi_tariff;
      estimation.type = "succeed";
      estimation.offer_id = "offer_id_1";
      estimation.price = "4747.4747";
      estimation.currency = "RUB";
      estimation.decision = clients::cargo_c2c::OfferDecision::kOrderProhibited;
      response.estimations.push_back((Response200EstimationsA)estimation);
    }
    return response;
  };

  ContextOverrides overrides;
  overrides.c2c_handler = faulty_handler;

  PluginTest test(overrides);
  const auto service_levels = test.RunDeliveryPlugin();

  ASSERT_EQ(test.CargoC2cTimesCalled(), 1);
  ASSERT_EQ(service_levels.size(), 2);
  ASSERT_NE(service_levels[0].tariff_unavailable, std::nullopt);
}

UTEST(DeliveryOrderFlowTest, MinimalPriceOffer) {
  const auto faulty_handler = [&](const C2cRequest& request) -> C2cResponse {
    C2cResponse response;
    for (const auto& tariff : request.body.taxi_tariffs) {
      clients::cargo_c2c::TariffClassEstimatingResult estimation;
      estimation.taxi_tariff = tariff.taxi_tariff;
      estimation.type = "succeed";
      estimation.offer_id = "offer_id_1";
      estimation.price = "4747.4747";
      estimation.currency = "RUB";
      estimation.decision =
          clients::cargo_c2c::OfferDecision::kMinimalPriceOffer;
      response.estimations.push_back((Response200EstimationsA)estimation);
    }
    return response;
  };

  test::TranslationHandler handler =
      [](const core::Translation& translation,
         const std::string& locale) -> std::optional<std::string> {
    return translation->main_key.key + "##" + locale + "##" +
           translation->main_key.args["minimal_price"];
  };

  ContextOverrides overrides;
  overrides.c2c_handler = faulty_handler;
  overrides.translator = std::make_shared<test::TranslatorMock>(handler);

  PluginTest test(overrides);
  const auto service_levels = test.RunDeliveryPlugin();

  ASSERT_EQ(test.CargoC2cTimesCalled(), 1);
  ASSERT_EQ(service_levels.size(), 2);
  ASSERT_NE(service_levels[0].description_parts, std::nullopt);
  ASSERT_EQ(service_levels[0].description_parts->value,
            std::string{"interval_description####4747 $SIGN$$CURRENCY$"});
}

UTEST(DeliveryOrderFlowTest, TariffUnavailable) {
  static const std::string kErrorCode = "pickup_point_not_selected";

  const auto faulty_handler = [&](const C2cRequest& request) -> C2cResponse {
    C2cResponse response;
    for (const auto& tariff : request.body.taxi_tariffs) {
      clients::cargo_c2c::TariffClassEstimatingError estimation;
      estimation.taxi_tariff = tariff.taxi_tariff;
      estimation.error.code = "pickup_point_not_selected";
      response.estimations.push_back((Response200EstimationsA)estimation);
    }
    return response;
  };

  taxi_config::cargo_c2c_routestats_tariff_unavailable_settings::Settings
      settings;
  settings.show_price = true;
  settings.subtitle = {"some_key"};
  auto config_storage = dynamic_config::MakeDefaultStorage({
      {taxi_config::CARGO_C2C_ROUTESTATS_TARIFF_UNAVAILABLE_SETTINGS,
       {{"__default__", std::move(settings)}}},
  });
  const auto config =
      std::make_shared<test::TaxiConfigsMock>(std::move(config_storage));

  ContextOverrides overrides;
  overrides.c2c_handler = faulty_handler;
  overrides.config = config;

  PluginTest test(overrides);
  const auto service_levels = test.RunDeliveryPlugin();

  ASSERT_EQ(test.CargoC2cTimesCalled(), 1);
  ASSERT_EQ(service_levels.size(), 2);
  ASSERT_NE(service_levels[0].tariff_unavailable, std::nullopt);
  ASSERT_EQ(service_levels[0].tariff_unavailable->code, kErrorCode);
  ASSERT_EQ(service_levels[0].tariff_unavailable->show_price, true);
  ASSERT_NE(service_levels[0].tariff_unavailable->subtitle, std::nullopt);
  ASSERT_NE(service_levels[0].tariff_unavailable->order_button_action,
            std::nullopt);
}

UTEST(DeliveryOrderFlowTest, PersonalWallet) {
  clients::cargo_c2c::PaymentInfo actual;
  const auto c2c_handler = [&](const C2cRequest& request) -> C2cResponse {
    actual = request.body.delivery_description.payment_info;

    return C2cResponse{};
  };

  handlers::RequestPaymentComplement complement;
  complement.type = "personal_wallet";
  complement.payment_method_id = "w/7c4cbe75-9d33-5406-8830-258aeaa7f922";

  handlers::RequestPayment payment;
  payment.type = "card";
  payment.payment_method_id = "card-xa65d481a0d5aec80b9b3b291";
  payment.complements.emplace({complement});

  ContextOverrides overrides;
  overrides.c2c_handler = c2c_handler;
  overrides.payment = payment;

  PluginTest test(overrides);
  test.RunDeliveryPlugin();

  ASSERT_EQ(test.CargoC2cTimesCalled(), 1);
  ASSERT_EQ(actual.complements.has_value(), true);
  ASSERT_EQ(actual.complements->at(0).type, complement.type);
  ASSERT_EQ(actual.complements->at(0).payment_method_id,
            complement.payment_method_id);
}

}  // namespace routestats::plugins::delivery_order_flow
