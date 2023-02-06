#include <gtest/gtest.h>

#include <lookup-ordering/clients/driver_scoring.hpp>
#include <taxi_config/lookup-ordering/taxi_config.hpp>

// forward declaration
namespace lookup_ordering::clients::driver_scoring::detail {
taxi_config::driver_scoring_client_qos::QosInfo GetLimitedQos(
    const taxi_config::driver_scoring_client_qos::QosInfo& endpoint_config,
    const std::chrono::milliseconds timeout_limit);
}  // namespace lookup_ordering::clients::driver_scoring::detail

TEST(LookupOrdering, LimitedQos) {
  using lookup_ordering::clients::driver_scoring::detail::GetLimitedQos;
  using QosInfo = taxi_config::driver_scoring_client_qos::QosInfo;
  using milliseconds = std::chrono::milliseconds;

  QosInfo cfg_qos;
  cfg_qos.attempts = 3;
  cfg_qos.timeout_ms = milliseconds(200);
  QosInfo cfg_qos_2 = cfg_qos;
  cfg_qos_2.attempts = 2;
  QosInfo cfg_qos_1 = cfg_qos;
  cfg_qos_1.attempts = 1;
  const milliseconds ms_150(150);
  QosInfo cfg_qos_1_150 = cfg_qos;
  cfg_qos_1_150.attempts = 1;
  cfg_qos_1_150.timeout_ms = ms_150;

  EXPECT_EQ(GetLimitedQos(cfg_qos, milliseconds(600)), cfg_qos);
  EXPECT_EQ(GetLimitedQos(cfg_qos, milliseconds(500)), cfg_qos_2);
  EXPECT_EQ(GetLimitedQos(cfg_qos, cfg_qos.timeout_ms), cfg_qos_1);
  EXPECT_EQ(GetLimitedQos(cfg_qos, ms_150), cfg_qos_1_150);
}
