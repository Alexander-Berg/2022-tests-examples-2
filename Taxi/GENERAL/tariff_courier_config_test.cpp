#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include "tariff_courier_config.hpp"

TEST(TestTariffCourierConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::TariffCourierConfig& courier_settings =
      config.Get<config::TariffCourierConfig>();

  ASSERT_EQ(courier_settings.enable_eta_requesting, true);
  ASSERT_EQ(courier_settings.enable_eta_substitution, false);
  ASSERT_EQ(courier_settings.eta_fallback.use_stub_values, false);
  ASSERT_EQ(courier_settings.eta_fallback.default_eta_seconds, 900);
  ASSERT_EQ(courier_settings.GetMaxSearchDistanceByConsumer("some_consumer"),
            2000);
}
