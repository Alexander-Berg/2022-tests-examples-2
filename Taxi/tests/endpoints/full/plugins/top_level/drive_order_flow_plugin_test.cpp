#include <testing/taxi_config.hpp>
#include <userver/dynamic_config/fwd.hpp>
#include <userver/dynamic_config/value.hpp>
#include <userver/utest/utest.hpp>

#include <json-diff/json_diff.hpp>

#include <clients/yandex-drive/client_mock_base.hpp>
#include <core/context/clients/clients_impl.hpp>
#include <tests/context/clients_mock_test.hpp>
#include <tests/context/taxi_config_mock_test.hpp>
#include <tests/context_mock_test.hpp>
#include <tests/endpoints/common/service_level_mock_test.hpp>

#include <endpoints/full/builders/input_builder.hpp>
#include <endpoints/full/common.hpp>
#include <endpoints/full/plugins/drive_order_flow/plugin.hpp>
#include <experiments3/drive_service_level_selector.hpp>
#include <tests/endpoints/full/plugins/drive_order_flow/drive_order_flow_common_test.hpp>
#include <tests/endpoints/full/plugins/drive_order_flow/strings.hpp>

#include <taxi_config/variables/DRIVE_ORDER_FLOW_SETTINGS.hpp>
#include <taxi_config/variables/YANDEX_DRIVE_CAR_SIDE_IMAGE_SETTINGS.hpp>

namespace routestats::plugins::top_level {

namespace {

const std::string kCarIconOverrides(R"({
    "__default__": "car_icon_default",
    "renault_kaptur": "car_icon_kaptur"
  })");

const std::string kCarImageSettings(R"({
  "rules": [
    {
      "by_app_name": {
        "android": [
          {
            "image_size": "4x",
            "size_hint": 640
          }
        ]
      },
      "type": "drive_car_side_image_from_meta_by_size_hint"
    }
  ]
})");

const std::string kExpDisabled = "{\"enabled\":false}";
const std::string kExpEnabled = "{\"enabled\":true}";

const core::CategoriesVisibility kCategoriesVisibility{
    {
        {
            "drive",
            {
                true,   // is_visible
                false,  // should_be_skipped
            },
        },
        {
            "skip",
            {
                true,  // is_visible
                true,  // should_be_skipped
            },
        },
        {
            "invis",
            {
                false,  // is_visible
                false,  // should_be_skipped
            },
        },
    },
    {},  // ordered_allowed_categories
};

dynamic_config::StorageMock GetTaxiConfigStorageMock() {
  const auto default_snapshot = dynamic_config::GetDefaultSnapshot();

  auto order_flow_settings =
      default_snapshot[taxi_config::DRIVE_ORDER_FLOW_SETTINGS];
  order_flow_settings.car_icons =
      formats::json::FromString(kCarIconOverrides)
          .As<dynamic_config::ValueDict<std::string>>();

  return dynamic_config::MakeDefaultStorage({
      {taxi_config::DRIVE_ORDER_FLOW_SETTINGS, order_flow_settings},
      {taxi_config::YANDEX_DRIVE_CAR_SIDE_IMAGE_SETTINGS,
       formats::json::FromString(kCarImageSettings)
           .As<taxi_config::yandex_drive_car_side_image_settings::
                   YandexDriveCarSideImageSettings>()},
  });
}

struct ContextOverrides {
  bool is_lightweight_request{};
  std::optional<std::string> full_offers{};
  std::optional<std::string> offers_for_noreg{};
};

template <class Experiment>
void SetExperimentValueFromJsonString(core::ExpMappedData& experiments,
                                      const std::string& json_value) {
  experiments[Experiment::kName] = {
      Experiment::kName,
      formats::json::FromString(json_value),
      {},
  };
}

core::Experiments MockExperiments() {
  core::ExpMappedData experiments;
  static const std::string kSelectorExp(R"({
    "enabled": true,
    "settings": {
       "service_level_class": "drive",
       "is_hidden_forced": true
    }
  })");
  SetExperimentValueFromJsonString<experiments3::DriveServiceLevelSelector>(
      experiments, kSelectorExp);
  return {std::move(experiments)};
}

core::Configs3 MockConfigs(const ContextOverrides& overrides) {
  core::ExpMappedData experiments;
  SetExperimentValueFromJsonString<experiments3::DriveFullOffersInfo>(
      experiments, overrides.full_offers.value_or(kExpDisabled));
  SetExperimentValueFromJsonString<experiments3::DriveOffersForNoreg>(
      experiments, overrides.offers_for_noreg.value_or(kExpDisabled));
  return {{std::move(experiments)}};
}

class TestContext {
 public:
  TestContext(const std::shared_ptr<
                  drive_order_flow::test::MockYandexDriveClient>& drive_client,
              size_t drive_times_called_before,
              const std::shared_ptr<test::TaxiConfigsMock>& taxi_configs)
      : yandex_drive_client_(drive_client),
        yandex_drive_times_called_before_(drive_times_called_before),
        taxi_configs_(taxi_configs) {}

  std::shared_ptr<const top_level::Context> GetTopLevelContext(
      const ContextOverrides overrides = ContextOverrides{}) {
    auto context = test::full::GetDefaultContext();
    context.experiments.uservices_routestats_exps = MockExperiments();
    context.experiments.uservices_routestats_configs = MockConfigs(overrides);
    context.user = drive_order_flow::test::MakeUser();
    full::RoutestatsRequest request =
        drive_order_flow::test::MakeRoutestatsRequest();
    request.is_lightweight = overrides.is_lightweight_request;
    context.input = full::BuildRoutestatsInput(request, {}, {});
    context.clients.yandex_drive =
        core::MakeClient<clients::yandex_drive::Client>(*yandex_drive_client_);
    context.taxi_configs = taxi_configs_;
    context.categories_visibility = kCategoriesVisibility;
    return test::full::MakeTopLevelContext(context);
  }

  /// Note: returns times yandex-drive was called before current TestContext
  /// was created. Do not use this directly, use
  /// DriveOrderFlowPluginTest::GetDriveTimesCalled(TestContext) instead.
  size_t GetDriveTimesCalledBefore() const {
    return yandex_drive_times_called_before_;
  }

 private:
  std::shared_ptr<drive_order_flow::test::MockYandexDriveClient>
      yandex_drive_client_;
  size_t yandex_drive_times_called_before_;
  std::shared_ptr<test::TaxiConfigsMock> taxi_configs_;
};

class DriveOrderFlowPluginTest : public testing::Test {
 protected:
  void SetUp() override {
    taxi_configs_ =
        std::make_shared<test::TaxiConfigsMock>(GetTaxiConfigStorageMock());
    yandex_drive_client_ =
        std::make_shared<drive_order_flow::test::MockYandexDriveClient>(
            [this](const drive_order_flow::test::DriveRequest&)
                -> drive_order_flow::test::DriveResponse {
              ++yandex_drive_times_called_;
              // will fail if response is not set
              return yandex_drive_response_.value();
            });
  }

  TestContext GetTestContext(
      std::optional<drive_order_flow::test::DriveResponse> response) {
    yandex_drive_response_ = std::move(response);
    return {yandex_drive_client_, yandex_drive_times_called_, taxi_configs_};
  }

  size_t GetDriveTimesCalled(const TestContext& ctx) const {
    return yandex_drive_times_called_ - ctx.GetDriveTimesCalledBefore();
  }

 private:
  std::shared_ptr<drive_order_flow::test::MockYandexDriveClient>
      yandex_drive_client_;
  std::optional<drive_order_flow::test::DriveResponse> yandex_drive_response_;
  size_t yandex_drive_times_called_;
  std::shared_ptr<test::TaxiConfigsMock> taxi_configs_;
};

core::ServiceLevel MockServiceLevel(std::string class_,
                                    core::TariffUnavailable unavailable) {
  auto result = test::MockDefaultServiceLevel(class_);
  result.tariff_unavailable = std::move(unavailable);
  return result;
}

}  // namespace

UTEST_F(DriveOrderFlowPluginTest, HappyPath) {
  auto test_ctx = GetTestContext(
      drive_order_flow::test::DriveResponseBuilder().GetResponse());
  auto top_level_ctx = test_ctx.GetTopLevelContext();
  DriveOrderFlowPlugin plugin;
  plugin.OnContextBuilt(top_level_ctx);
  plugin.TestingWaitOffersRequest();
  EXPECT_EQ(GetDriveTimesCalled(test_ctx), 1);

  std::vector<ServiceLevel> service_levels{
      MockServiceLevel("drive",
                       core::TariffUnavailable{"no_free_cars_nearby", "msg"}),
  };
  auto& service_level = service_levels.front();
  const auto& result =
      plugin.ExtendServiceLevels(top_level_ctx, service_levels);
  test::ApplyExtensions(result, service_levels);
  ASSERT_FALSE(service_level.tariff_unavailable);
  ASSERT_EQ(service_level.description_parts.value().value,
            "74 $SIGN$$CURRENCY$");

  const auto plugin_res =
      plugin.OnServiceLevelRendering(service_level, top_level_ctx);
  ASSERT_TRUE(plugin_res);
  handlers::ServiceLevel sl_resp;
  plugins::common::ResultWrapper<handlers::ServiceLevel> wrapper(sl_resp);
  plugin_res->SerializeInPlace(wrapper);

  EXPECT_PRED_FORMAT2(json_diff::IsValueEqualToJsonString, sl_resp,
                      drive_order_flow::test::strings::kNonFullOffersResponse);
}

UTEST_F(DriveOrderFlowPluginTest, FullOffersInfo) {
  auto test_ctx = GetTestContext(
      drive_order_flow::test::DriveResponseBuilder().GetResponse());
  ContextOverrides overrides;
  overrides.full_offers = kExpEnabled;
  auto top_level_ctx = test_ctx.GetTopLevelContext(overrides);
  DriveOrderFlowPlugin plugin;
  plugin.OnContextBuilt(top_level_ctx);
  plugin.TestingWaitOffersRequest();
  EXPECT_EQ(GetDriveTimesCalled(test_ctx), 1);

  std::vector<ServiceLevel> service_levels{
      MockServiceLevel("drive",
                       core::TariffUnavailable{"no_free_cars_nearby", "msg"}),
  };
  auto& service_level = service_levels.front();
  const auto& result =
      plugin.ExtendServiceLevels(top_level_ctx, service_levels);
  test::ApplyExtensions(result, service_levels);
  ASSERT_FALSE(service_level.tariff_unavailable);
  ASSERT_EQ(service_level.description_parts.value().value,
            "74 $SIGN$$CURRENCY$");

  const auto plugin_res =
      plugin.OnServiceLevelRendering(service_level, top_level_ctx);
  ASSERT_TRUE(plugin_res);
  handlers::ServiceLevel sl_resp;
  plugins::common::ResultWrapper<handlers::ServiceLevel> wrapper(sl_resp);
  plugin_res->SerializeInPlace(wrapper);

  EXPECT_PRED_FORMAT2(json_diff::IsValueEqualToJsonString, sl_resp,
                      drive_order_flow::test::strings::kFullOffersResponse);
}

UTEST_F(DriveOrderFlowPluginTest, SkipUnavailabilityCodes) {
  auto test_ctx = GetTestContext(
      drive_order_flow::test::DriveResponseBuilder().GetResponse());
  auto top_level_ctx = test_ctx.GetTopLevelContext();
  DriveOrderFlowPlugin plugin;
  plugin.OnContextBuilt(top_level_ctx);
  plugin.TestingWaitOffersRequest();
  EXPECT_EQ(GetDriveTimesCalled(test_ctx), 1);

  std::vector<ServiceLevel> service_levels{
      MockServiceLevel("drive",
                       core::TariffUnavailable{"code_to_proxy", "msg"}),
  };
  auto& service_level = service_levels.front();
  const auto& result =
      plugin.ExtendServiceLevels(top_level_ctx, service_levels);
  test::ApplyExtensions(result, service_levels);
  ASSERT_TRUE(service_level.tariff_unavailable);
  ASSERT_EQ(service_level.tariff_unavailable->code, "code_to_proxy");
}

UTEST_F(DriveOrderFlowPluginTest, HasActiveSessions) {
  auto test_ctx = GetTestContext(drive_order_flow::test::DriveResponseBuilder()
                                     .HasActiveSessions()
                                     .GetResponse());
  auto top_level_ctx = test_ctx.GetTopLevelContext();
  DriveOrderFlowPlugin plugin;
  plugin.OnContextBuilt(top_level_ctx);
  plugin.TestingWaitOffersRequest();
  EXPECT_EQ(GetDriveTimesCalled(test_ctx), 1);

  std::vector<ServiceLevel> service_levels{
      MockServiceLevel("drive",
                       core::TariffUnavailable{"no_free_cars_nearby", "msg"}),
  };
  auto& service_level = service_levels.front();
  const auto& result =
      plugin.ExtendServiceLevels(top_level_ctx, service_levels);
  test::ApplyExtensions(result, service_levels);

  ASSERT_TRUE(service_level.tariff_unavailable);
  ASSERT_EQ(service_level.tariff_unavailable->code, "drive_active_order");
}

UTEST_F(DriveOrderFlowPluginTest, LightweightRequest) {
  auto test_ctx = GetTestContext(
      drive_order_flow::test::DriveResponseBuilder().GetResponse());

  ContextOverrides overrides;
  overrides.is_lightweight_request = true;
  auto top_level_ctx = test_ctx.GetTopLevelContext(overrides);
  DriveOrderFlowPlugin plugin;

  plugin.OnContextBuilt(top_level_ctx);
  plugin.TestingWaitOffersRequest();
  EXPECT_EQ(GetDriveTimesCalled(test_ctx), 0);

  std::vector<ServiceLevel> service_levels{
      MockServiceLevel("drive",
                       core::TariffUnavailable{"no_free_cars_nearby", "msg"}),
  };
  auto& service_level = service_levels.front();
  const auto& result =
      plugin.ExtendServiceLevels(top_level_ctx, service_levels);
  test::ApplyExtensions(result, service_levels);

  ASSERT_TRUE(service_level.tariff_unavailable);
  ASSERT_EQ(service_level.tariff_unavailable->code, "drive_loading_skipped");
}

UTEST_F(DriveOrderFlowPluginTest, DriveRequestError) {
  auto test_ctx = GetTestContext(/*drive response*/ std::nullopt);
  auto top_level_ctx = test_ctx.GetTopLevelContext();
  DriveOrderFlowPlugin plugin;

  plugin.OnContextBuilt(top_level_ctx);
  plugin.TestingWaitOffersRequest();
  EXPECT_EQ(GetDriveTimesCalled(test_ctx), 1);

  std::vector<ServiceLevel> service_levels{
      MockServiceLevel("drive",
                       core::TariffUnavailable{"no_free_cars_nearby", "msg"}),
  };
  auto& service_level = service_levels.front();
  const auto& result =
      plugin.ExtendServiceLevels(top_level_ctx, service_levels);
  test::ApplyExtensions(result, service_levels);

  ASSERT_TRUE(service_level.tariff_unavailable);
  ASSERT_EQ(service_level.tariff_unavailable->code, "drive_unknown_error");
}

UTEST_F(DriveOrderFlowPluginTest, DriveNoRegNoOffers) {
  auto test_ctx = GetTestContext(drive_order_flow::test::DriveResponseBuilder()
                                     .NoOffers("some_reason")
                                     .NotRegistered()
                                     .GetResponse());
  ContextOverrides ctx_overrides;
  ctx_overrides.offers_for_noreg = kExpEnabled;
  auto top_level_ctx = test_ctx.GetTopLevelContext(ctx_overrides);
  DriveOrderFlowPlugin plugin;

  plugin.OnContextBuilt(top_level_ctx);
  plugin.TestingWaitOffersRequest();
  EXPECT_EQ(GetDriveTimesCalled(test_ctx), 1);

  std::vector<ServiceLevel> service_levels{
      MockServiceLevel("drive",
                       core::TariffUnavailable{"no_free_cars_nearby", "msg"}),
  };
  auto& service_level = service_levels.front();
  const auto& result =
      plugin.ExtendServiceLevels(top_level_ctx, service_levels);
  test::ApplyExtensions(result, service_levels);
  ASSERT_TRUE(service_level.tariff_unavailable);
  ASSERT_EQ(service_level.tariff_unavailable->code, "drive_not_registered");

  const auto plugin_res =
      plugin.OnServiceLevelRendering(service_level, top_level_ctx);
  ASSERT_TRUE(plugin_res);
  handlers::ServiceLevel sl_resp;
  plugins::common::ResultWrapper<handlers::ServiceLevel> wrapper(sl_resp);
  plugin_res->SerializeInPlace(wrapper);

  ASSERT_EQ(sl_resp.drive_extra, std::nullopt);
}

UTEST_F(DriveOrderFlowPluginTest, DriveNoRegWithOffersDisabled) {
  auto test_ctx = GetTestContext(drive_order_flow::test::DriveResponseBuilder()
                                     .NotRegistered()
                                     .GetResponse());
  ContextOverrides ctx_overrides;
  ctx_overrides.full_offers = kExpEnabled;
  ctx_overrides.offers_for_noreg = kExpDisabled;
  auto top_level_ctx = test_ctx.GetTopLevelContext(ctx_overrides);
  DriveOrderFlowPlugin plugin;

  plugin.OnContextBuilt(top_level_ctx);
  plugin.TestingWaitOffersRequest();
  EXPECT_EQ(GetDriveTimesCalled(test_ctx), 1);

  std::vector<ServiceLevel> service_levels{
      MockServiceLevel("drive",
                       core::TariffUnavailable{"no_free_cars_nearby", "msg"}),
  };
  auto& service_level = service_levels.front();
  const auto& result =
      plugin.ExtendServiceLevels(top_level_ctx, service_levels);
  test::ApplyExtensions(result, service_levels);
  ASSERT_TRUE(service_level.tariff_unavailable);
  ASSERT_EQ(service_level.tariff_unavailable->code, "drive_not_registered");

  const auto plugin_res =
      plugin.OnServiceLevelRendering(service_level, top_level_ctx);
  ASSERT_TRUE(plugin_res);
  handlers::ServiceLevel sl_resp;
  plugins::common::ResultWrapper<handlers::ServiceLevel> wrapper(sl_resp);
  plugin_res->SerializeInPlace(wrapper);

  ASSERT_EQ(sl_resp.drive_extra, std::nullopt);
}

UTEST_F(DriveOrderFlowPluginTest, DriveNoRegWithOffersFull) {
  auto test_ctx = GetTestContext(drive_order_flow::test::DriveResponseBuilder()
                                     .NotRegistered()
                                     .GetResponse());
  ContextOverrides ctx_overrides;
  ctx_overrides.full_offers = kExpEnabled;
  ctx_overrides.offers_for_noreg = kExpEnabled;
  auto top_level_ctx = test_ctx.GetTopLevelContext(ctx_overrides);
  DriveOrderFlowPlugin plugin;

  plugin.OnContextBuilt(top_level_ctx);
  plugin.TestingWaitOffersRequest();
  EXPECT_EQ(GetDriveTimesCalled(test_ctx), 1);

  std::vector<ServiceLevel> service_levels{
      MockServiceLevel("drive",
                       core::TariffUnavailable{"no_free_cars_nearby", "msg"}),
  };
  auto& service_level = service_levels.front();
  const auto& result =
      plugin.ExtendServiceLevels(top_level_ctx, service_levels);
  test::ApplyExtensions(result, service_levels);
  ASSERT_TRUE(service_level.tariff_unavailable);
  ASSERT_EQ(service_level.tariff_unavailable->code, "drive_not_registered");

  const auto plugin_res =
      plugin.OnServiceLevelRendering(service_level, top_level_ctx);
  ASSERT_TRUE(plugin_res);
  handlers::ServiceLevel sl_resp;
  plugins::common::ResultWrapper<handlers::ServiceLevel> wrapper(sl_resp);
  plugin_res->SerializeInPlace(wrapper);

  EXPECT_PRED_FORMAT2(
      json_diff::IsValueEqualToJsonString, sl_resp,
      drive_order_flow::test::strings::kFullOffersResponseNoReg);
}

UTEST_F(DriveOrderFlowPluginTest, DriveNoRegWithOffersNonFull) {
  auto test_ctx = GetTestContext(drive_order_flow::test::DriveResponseBuilder()
                                     .NotRegistered()
                                     .GetResponse());
  ContextOverrides ctx_overrides;
  ctx_overrides.full_offers = kExpDisabled;
  ctx_overrides.offers_for_noreg = kExpEnabled;
  auto top_level_ctx = test_ctx.GetTopLevelContext(ctx_overrides);
  DriveOrderFlowPlugin plugin;

  plugin.OnContextBuilt(top_level_ctx);
  plugin.TestingWaitOffersRequest();
  EXPECT_EQ(GetDriveTimesCalled(test_ctx), 1);

  std::vector<ServiceLevel> service_levels{
      MockServiceLevel("drive",
                       core::TariffUnavailable{"no_free_cars_nearby", "msg"}),
  };
  auto& service_level = service_levels.front();
  const auto& result =
      plugin.ExtendServiceLevels(top_level_ctx, service_levels);
  test::ApplyExtensions(result, service_levels);
  ASSERT_TRUE(service_level.tariff_unavailable);
  ASSERT_EQ(service_level.tariff_unavailable->code, "drive_not_registered");

  const auto plugin_res =
      plugin.OnServiceLevelRendering(service_level, top_level_ctx);
  ASSERT_TRUE(plugin_res);
  handlers::ServiceLevel sl_resp;
  plugins::common::ResultWrapper<handlers::ServiceLevel> wrapper(sl_resp);
  plugin_res->SerializeInPlace(wrapper);

  EXPECT_PRED_FORMAT2(
      json_diff::IsValueEqualToJsonString, sl_resp,
      drive_order_flow::test::strings::kNonFullOffersResponseNoReg);
}

}  // namespace routestats::plugins::top_level
