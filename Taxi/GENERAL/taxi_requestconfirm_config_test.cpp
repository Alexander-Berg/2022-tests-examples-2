#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/taxi_requestconfirm_config.hpp>

TEST(TestTaxiRequestconfirmConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::TaxiRequestconfirm& taxi_requestconfirm_config =
      config.Get<config::TaxiRequestconfirm>();
  ASSERT_EQ(taxi_requestconfirm_config.live_location_in_waiting_status_enabled,
            false);
}
