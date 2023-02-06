#include <configs/redis_config.hpp>
#include <testing/taxi_config.hpp>
#include <userver/utest/utest.hpp>

TEST(Configs, ParseRedisConfigFallback) {
  const auto& config = dynamic_config::GetDefaultSnapshot();
  const auto& command_control = configs::GetCommandControl(config);
  EXPECT_EQ(command_control.max_retries, 2);
  EXPECT_EQ(command_control.timeout_single, std::chrono::milliseconds(40));
  EXPECT_EQ(command_control.timeout_all, std::chrono::milliseconds(80));
}
