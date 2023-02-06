#include <userver/utest/utest.hpp>

#include <testing/taxi_config.hpp>

#include <boost/range/adaptor/transformed.hpp>
#include <logics/saga/plan.hpp>
#include <models/saga/step_base.hpp>
#include <models/saga/steps_state.hpp>
#include <utils/utils.hpp>

namespace {

const models::saga::StepName kPrepareStep1{"id1"};
const models::saga::StepName kBeforeStep2{"id2"};
const models::saga::StepName kChangeStep3{"id3"};
const models::saga::StepName kAfterStep4{"id4"};

class StepMock final : public models::saga::StepBase {
 public:
  StepMock(models::saga::StepName step_name, models::saga::Epoch epoch)
      : StepBase(models::Saga{}, std::move(step_name), epoch) {}

  models::saga::StepStatus Execute() override {
    return models::saga::StepStatus::MakeOk();
  }

  models::saga::StepStatus Compensate() override {
    return models::saga::StepStatus::MakeOk();
  }
};

std::vector<std::unique_ptr<models::saga::StepBase>> CreateSteps() {
  std::vector<std::unique_ptr<models::saga::StepBase>> steps;

  steps.push_back(std::make_unique<StepMock>(
      kBeforeStep2, models::saga::Epoch::kBeforeModeChange));

  steps.push_back(std::make_unique<StepMock>(
      kAfterStep4, models::saga::Epoch::kAfterModeChange));

  steps.push_back(std::make_unique<StepMock>(
      kPrepareStep1, models::saga::Epoch::kPrepareModeChange));

  steps.push_back(std::make_unique<StepMock>(kChangeStep3,
                                             models::saga::Epoch::kModeChange));

  return steps;
}

void CheckStepsEqual(
    const std::vector<std::unique_ptr<models::saga::StepBase>>& steps,
    const std::vector<models::saga::StepName>& expect_steps) {
  const auto simple_steps =
      utils::Eval(steps | boost::adaptors::transformed([](const auto& step) {
                    return step->GetName();
                  }));

  EXPECT_EQ(std::equal(simple_steps.begin(), simple_steps.end(),
                       expect_steps.begin(), expect_steps.end()),
            true);
}

}  // namespace

UTEST(SagaPlanContinuation, EmptyState) {
  const auto result = logics::saga::PlanContinuation(CreateSteps(), {});

  CheckStepsEqual(result,
                  {kPrepareStep1, kBeforeStep2, kChangeStep3, kAfterStep4});
}

UTEST(SagaPlanContinuation, SkipExecutedSteps) {
  models::saga::StepsState state;
  state.AddStep(kPrepareStep1, models::saga::StepStatus::Type::kOk,
                std::nullopt);
  state.AddStep(kChangeStep3, models::saga::StepStatus::Type::kOk,
                std::nullopt);

  const auto result = logics::saga::PlanContinuation(CreateSteps(), state);

  CheckStepsEqual(result, {kBeforeStep2, kAfterStep4});
}

UTEST(SagaPlanCompensation, EmptyState) {
  const auto result = logics::saga::PlanCompensation(CreateSteps(), {});

  CheckStepsEqual(result, {});
}

UTEST(SagaPlanCompensation, SkipNotExecutedSteps) {
  models::saga::StepsState state;
  state.AddStep(kBeforeStep2, models::saga::StepStatus::Type::kFailed,
                std::nullopt);
  state.AddStep(kPrepareStep1, models::saga::StepStatus::Type::kOk,
                std::nullopt);
  state.AddStep(kChangeStep3, models::saga::StepStatus::Type::kFailed,
                std::nullopt);
  const auto result = logics::saga::PlanCompensation(CreateSteps(), state);

  CheckStepsEqual(result, {kChangeStep3, kBeforeStep2, kPrepareStep1});
}

UTEST(SagaPlanCompensation, SkipBlockedSteps) {
  models::saga::StepsState state;
  state.AddStep(kBeforeStep2, models::saga::StepStatus::Type::kFailed,
                std::nullopt);
  state.AddStep(kPrepareStep1, models::saga::StepStatus::Type::kOk,
                std::nullopt);
  state.AddStep(kChangeStep3, models::saga::StepStatus::Type::kBlocked,
                std::nullopt);
  const auto result = logics::saga::PlanCompensation(CreateSteps(), state);

  CheckStepsEqual(result, {kBeforeStep2, kPrepareStep1});
}

UTEST(SagaPlanCompensation, SkipAlreadyCompensatedSteps) {
  models::saga::StepsState state;
  state.AddStep(kBeforeStep2, models::saga::StepStatus::Type::kOk,
                std::nullopt);
  state.AddStep(kPrepareStep1, models::saga::StepStatus::Type::kOk,
                std::nullopt);
  state.AddStep(kChangeStep3, models::saga::StepStatus::Type::kOk,
                models::saga::StepStatus::Type::kOk);
  state.AddStep(kAfterStep4, models::saga::StepStatus::Type::kOk,
                models::saga::StepStatus::Type::kOk);
  const auto result = logics::saga::PlanCompensation(CreateSteps(), state);

  CheckStepsEqual(result, {kBeforeStep2, kPrepareStep1});
}
