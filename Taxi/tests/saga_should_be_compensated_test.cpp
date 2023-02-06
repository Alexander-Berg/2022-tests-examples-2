#include <userver/utest/utest.hpp>

#include <testing/taxi_config.hpp>

#include <taxi_config/variables/DRIVER_MODE_SUBSCRIPTION_SAGA_SETTINGS.hpp>

#include <logics/saga/plan.hpp>

using namespace std::chrono_literals;

namespace {

const models::saga::StepName kStepId{"id1"};

}

class SagaShouldBeCompensated : public ::testing::Test {
 public:
  dynamic_config::StorageMock GetTaxiConfig(
      std::optional<std::optional<std::chrono::seconds>> compensate_timeout)
      const {
    const auto& default_config = dynamic_config::GetDefaultSnapshot();
    auto saga_settings =
        default_config[taxi_config::DRIVER_MODE_SUBSCRIPTION_SAGA_SETTINGS];
    saga_settings.allow_saga_compensation = true;
    if (compensate_timeout) {
      saga_settings.compensate_failed_saga_timeout_s = *compensate_timeout;
    }

    return dynamic_config::StorageMock(
        {{taxi_config::DRIVER_MODE_SUBSCRIPTION_SAGA_SETTINGS, saga_settings}});
  }
};

UTEST_F(SagaShouldBeCompensated, CompensateWhenBlocked) {
  auto taxi_config = GetTaxiConfig(std::nullopt);
  models::saga::StepsState state;
  state.AddStep(kStepId, models::saga::StepStatus::Type::kBlocked,
                std::nullopt);

  const auto result = logics::saga::ShouldBeCompensated(
      state, 1s, models::saga::CompensationPolicy::kAllow, {},
      taxi_config.GetSnapshot());

  ASSERT_EQ(result, true);
}

UTEST_F(SagaShouldBeCompensated, CompensateWhenBlockedDisabled) {
  auto taxi_config = GetTaxiConfig(std::nullopt);
  models::saga::StepsState state;
  state.AddStep(kStepId, models::saga::StepStatus::Type::kBlocked,
                std::nullopt);

  const auto result = logics::saga::ShouldBeCompensated(
      state, 1s, models::saga::CompensationPolicy::kForbid, {},
      taxi_config.GetSnapshot());

  ASSERT_EQ(result, false);
}

UTEST_F(SagaShouldBeCompensated, NotCompensateWhenOk) {
  auto taxi_config = GetTaxiConfig(std::nullopt);
  models::saga::StepsState state;
  state.AddStep(kStepId, models::saga::StepStatus::Type::kOk, std::nullopt);

  const auto result = logics::saga::ShouldBeCompensated(
      state, 0s, models::saga::CompensationPolicy::kAllow, {},
      taxi_config.GetSnapshot());

  ASSERT_EQ(result, false);
}

UTEST_F(SagaShouldBeCompensated, NotCompensateWhenFail) {
  auto taxi_config = GetTaxiConfig(std::nullopt);
  models::saga::StepsState state;

  state.AddStep(kStepId, models::saga::StepStatus::Type::kFailed, std::nullopt);

  const auto result = logics::saga::ShouldBeCompensated(
      state, 0s, models::saga::CompensationPolicy::kAllow, {},
      taxi_config.GetSnapshot());

  ASSERT_EQ(result, false);
}

UTEST_F(SagaShouldBeCompensated, NotCompensateWhenFailBeforeTimeout) {
  auto taxi_config = GetTaxiConfig(2s);
  models::saga::StepsState state;

  state.AddStep(kStepId, models::saga::StepStatus::Type::kFailed, std::nullopt);

  const auto result = logics::saga::ShouldBeCompensated(
      state, 2s, models::saga::CompensationPolicy::kAllow, {},
      taxi_config.GetSnapshot());

  ASSERT_EQ(result, false);
}

UTEST_F(SagaShouldBeCompensated, CompensateWhenFailAfterTimeout) {
  auto taxi_config = GetTaxiConfig(1s);
  models::saga::StepsState state;

  state.AddStep(kStepId, models::saga::StepStatus::Type::kFailed, std::nullopt);

  const auto result = logics::saga::ShouldBeCompensated(
      state, 2s, models::saga::CompensationPolicy::kAllow, {},
      taxi_config.GetSnapshot());

  ASSERT_EQ(result, true);
}
