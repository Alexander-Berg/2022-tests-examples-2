#include <gtest/gtest.h>

#include <userver/utest/utest.hpp>

#include <endpoints/common/builders/service_level_builder.hpp>
#include <endpoints/full/plugins/surge/plugin.hpp>
#include <tests/context/taxi_config_mock_test.hpp>
#include <tests/context_mock_test.hpp>
#include <tests/endpoints/common/service_level_mock_test.hpp>

#include <taxi_config/variables/ROUTESTATS_HIDE_SURGE_FOR_ZERO_PRICE.hpp>

namespace routestats::full {
namespace {

class ServiceLevelBaseProcessor : public ::testing::TestWithParam<std::string> {
 protected:
  handlers::ServiceLevel ProcessServiceLevel() {
    auto service_class = GetParam();
    auto service_level = test::MockDefaultServiceLevel(
        service_class, [](core::ServiceLevel& sl) {
          sl.final_price = core::Decimal{0};
          core::PaidOptions po;
          po.color_button = true;
          sl.paid_options = po;
        });
    plugins::top_level::SurgePlugin plugin;
    full::ContextData test_ctx = test::full::GetDefaultContext();

    test_ctx.taxi_configs = GetConfigMock();

    auto plugin_ctx = test::full::MakeTopLevelContext(test_ctx);
    auto sl_patch = plugin.OnServiceLevelRendering(service_level, plugin_ctx);
    handlers::ServiceLevel sl;
    sl.paid_options.emplace();
    sl.paid_options->color_button = service_level.paid_options->color_button;
    plugins::common::ResultWrapper<handlers::ServiceLevel> wrapper(sl);
    sl_patch->SerializeInPlace(wrapper);
    return sl;
  }

 public:
  virtual void UpdateTaxiConfig(taxi_config::TaxiConfig&){};

  virtual std::shared_ptr<test::TaxiConfigsMock> GetConfigMock() const {
    return std::make_shared<test::TaxiConfigsMock>();
  }
};

class SurgePluginParametrizedSkip : public ServiceLevelBaseProcessor {};
class SurgePluginParametrizedNull : public ServiceLevelBaseProcessor {
 public:
  std::shared_ptr<test::TaxiConfigsMock> GetConfigMock() const override {
    auto config_storage = dynamic_config::MakeDefaultStorage({
        {taxi_config::ROUTESTATS_HIDE_SURGE_FOR_ZERO_PRICE, true},
    });
    return std::make_shared<test::TaxiConfigsMock>(std::move(config_storage));
  }
};
}  // namespace

TEST_P(SurgePluginParametrizedSkip, SkipServiceClasses) {
  auto sl = ProcessServiceLevel();
  ASSERT_TRUE(sl.paid_options);
  ASSERT_EQ(sl.paid_options->color_button, true);
}

INSTANTIATE_TEST_SUITE_P(SurgeTests, SurgePluginParametrizedSkip,
                         ::testing::Values("shuttle", "selfdriving"));

TEST_P(SurgePluginParametrizedNull, NullPaidOptions) {
  auto sl = ProcessServiceLevel();
  ASSERT_FALSE(sl.paid_options);
}

INSTANTIATE_TEST_SUITE_P(SurgeTests, SurgePluginParametrizedNull,
                         ::testing::Values("econom", "business"));

}  // namespace routestats::full
