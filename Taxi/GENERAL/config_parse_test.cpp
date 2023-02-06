#include <chrono>
#include <internal/config_parse.hpp>

#include <testing/taxi_config.hpp>
#include <userver/utest/utest.hpp>

namespace {

namespace drwi = driver_route_watcher::internal;
namespace drwm = driver_route_watcher::models;

TEST(ParseConfig, Parse) {
  const auto& config = dynamic_config::GetDefaultSnapshot();
  const auto& watcher_config = config.Get<taxi_config::TaxiConfig>();
  drwi::Config::NextGenFeatures ng_features;
  ng_features.enable_timelefts_publish = true;

  const auto model_config = drwi::Parse(watcher_config, ng_features);

  ASSERT_EQ(model_config.GetEnableReturnFromFallback(), true);
  ASSERT_EQ(model_config.GetReturnFromFallbackTimeout(),
            std::chrono::seconds{60});
  ASSERT_EQ(model_config.GetRouterFallback(), false);
  const auto& expected_service_priorities =
      std::unordered_map<std::string, double>{
          {"processing:transporting", 100},
          {"processing:driving", 90},
      };
  ASSERT_EQ(model_config.GetServicePriorityConfig(),
            expected_service_priorities);
  ASSERT_EQ(model_config.GetYtLogPercentage(), 0u);
  ASSERT_EQ(model_config.GetEnableRebuildOldRoute(), true);
  ASSERT_EQ(model_config.GetRebuildOldRouteTimeout(),
            std::chrono::seconds{300});
  ASSERT_EQ(model_config.GetRebuildOldRouteMinEta(), std::chrono::seconds{300});
  ASSERT_EQ(model_config.GetMaxAdjustDistance(), 100 * ::geometry::meter);
  ASSERT_EQ(model_config.GetOldWatchTimeout(), std::chrono::hours{8});
  ASSERT_EQ(model_config.GetRouteTtlAddition(), std::chrono::minutes{10});
  ASSERT_EQ(model_config.GetLogbrokerProcessingPercentage(), 0u);
  ASSERT_EQ(model_config.GetDiscardLogbroker(), false);

  const auto& expected_chaining_rules =
      drwi::ChainingRules{{drwm::ServiceId("processing:transporting"),
                           {drwm::ServiceId("processing:driving")}}};
  ASSERT_EQ(model_config.GetChainingRules(), expected_chaining_rules);
}

}  // namespace
