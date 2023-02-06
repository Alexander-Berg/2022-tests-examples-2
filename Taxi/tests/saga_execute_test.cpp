#include <userver/utest/utest.hpp>

#include <testing/taxi_config.hpp>

#include <logics/saga/execute.hpp>
#include <models/saga/step_base.hpp>

namespace {

const models::saga::StepName kPrepareStep1{"id1"};
const models::saga::StepName kPrepareStep2{"id2"};
const models::saga::StepName kPrepareStep3{"id3"};
const models::saga::StepName kChangeStep4{"id4"};
const models::saga::StepName kAfterStep5{"id5"};

class StepClientMock {
 public:
  StepClientMock(
      std::unordered_map<models::saga::StepName, models::saga::StepStatus>
          execute_result_by_step,
      const bool expect_compensate)
      : execute_result_by_step_(std::move(execute_result_by_step)),
        expect_compensate_(expect_compensate) {}

  models::saga::StepStatus Execute(const models::saga::StepName& step_name,
                                   bool is_compensate) {
    ++times_called_by_step_[step_name];
    EXPECT_EQ(is_compensate, expect_compensate_);
    return GetExecuteResult(step_name);
  }

  int TimesCalled(const models::saga::StepName& step_name) const {
    if (const auto it = times_called_by_step_.find(step_name);
        it != times_called_by_step_.end()) {
      return it->second;
    }
    return 0;
  }

  void ValidateResult(
      const std::vector<models::saga::ExecutedStep>& steps) const {
    ASSERT_EQ(steps.size(), times_called_by_step_.size());
    for (const auto& step : steps) {
      ASSERT_EQ(GetExecuteResult(step.name).GetType(), step.status.GetType());
    }
  }

 private:
  models::saga::StepStatus GetExecuteResult(
      const models::saga::StepName& step_name) const {
    if (const auto it = execute_result_by_step_.find(step_name);
        it != execute_result_by_step_.end()) {
      return it->second;
    }
    return models::saga::StepStatus::MakeOk();
  }

 private:
  std::unordered_map<models::saga::StepName, models::saga::StepStatus>
      execute_result_by_step_;
  std::unordered_map<models::saga::StepName, int> times_called_by_step_;
  bool expect_compensate_;
};

class StepMock final : public models::saga::StepBase {
 public:
  StepMock(models::saga::StepName step_name, models::saga::Epoch epoch,
           StepClientMock& step_client_mock)
      : StepBase(models::Saga{}, std::move(step_name), epoch),
        step_client_mock_(step_client_mock) {}

  models::saga::StepStatus Execute() override {
    return step_client_mock_.Execute(GetName(), false);
  }

  models::saga::StepStatus Compensate() override {
    return step_client_mock_.Execute(GetName(), true);
  }

 private:
  StepClientMock& step_client_mock_;
};

std::vector<std::unique_ptr<models::saga::StepBase>> CreateSteps(
    StepClientMock& step_client_mock) {
  std::vector<std::unique_ptr<models::saga::StepBase>> steps;

  steps.push_back(std::make_unique<StepMock>(
      kPrepareStep1, models::saga::Epoch::kPrepareModeChange,
      step_client_mock));

  steps.push_back(std::make_unique<StepMock>(
      kPrepareStep2, models::saga::Epoch::kPrepareModeChange,
      step_client_mock));

  steps.push_back(std::make_unique<StepMock>(
      kPrepareStep3, models::saga::Epoch::kPrepareModeChange,
      step_client_mock));

  steps.push_back(std::make_unique<StepMock>(
      kChangeStep4, models::saga::Epoch::kModeChange, step_client_mock));

  steps.push_back(std::make_unique<StepMock>(
      kAfterStep5, models::saga::Epoch::kAfterModeChange, step_client_mock));

  return steps;
}

}  // namespace

UTEST(SagaExecute, AllGoodExecute) {
  StepClientMock client_mock{{}, false};

  const auto result = logics::saga::Execute(CreateSteps(client_mock),
                                            &models::saga::StepBase::Execute);

  ASSERT_EQ(result.IsSuccess(), true);

  ASSERT_EQ(client_mock.TimesCalled(kPrepareStep1), 1);
  ASSERT_EQ(client_mock.TimesCalled(kPrepareStep2), 1);
  ASSERT_EQ(client_mock.TimesCalled(kPrepareStep3), 1);
  ASSERT_EQ(client_mock.TimesCalled(kChangeStep4), 1);
  ASSERT_EQ(client_mock.TimesCalled(kAfterStep5), 1);

  client_mock.ValidateResult(result.ExecutedSteps());
}

UTEST(SagaExecute, AllGoodCompensate) {
  StepClientMock client_mock{{}, true};

  const auto result = logics::saga::Execute(
      CreateSteps(client_mock), &models::saga::StepBase::Compensate);

  ASSERT_EQ(result.IsSuccess(), true);

  ASSERT_EQ(client_mock.TimesCalled(kPrepareStep1), 1);
  ASSERT_EQ(client_mock.TimesCalled(kPrepareStep2), 1);
  ASSERT_EQ(client_mock.TimesCalled(kPrepareStep3), 1);
  ASSERT_EQ(client_mock.TimesCalled(kChangeStep4), 1);
  ASSERT_EQ(client_mock.TimesCalled(kAfterStep5), 1);

  client_mock.ValidateResult(result.ExecutedSteps());
}

UTEST(SagaExecute, NotStartAnotherEpochOnError) {
  std::vector<std::unique_ptr<models::saga::StepBase>> steps;

  StepClientMock client_mock{
      {{kPrepareStep1, models::saga::StepStatus::MakeFailed("problem")}},
      false};

  const auto result = logics::saga::Execute(CreateSteps(client_mock),
                                            &models::saga::StepBase::Execute);

  ASSERT_EQ(result.IsSuccess(), false);

  ASSERT_EQ(client_mock.TimesCalled(kPrepareStep1), 1);
  ASSERT_EQ(client_mock.TimesCalled(kPrepareStep2), 1);
  ASSERT_EQ(client_mock.TimesCalled(kPrepareStep3), 1);
  ASSERT_EQ(client_mock.TimesCalled(kChangeStep4), 0);
  ASSERT_EQ(client_mock.TimesCalled(kAfterStep5), 0);

  client_mock.ValidateResult(result.ExecutedSteps());
}

UTEST(SagaExecute, NotStartAnotherEpochOnBlock) {
  std::vector<std::unique_ptr<models::saga::StepBase>> steps;

  StepClientMock client_mock{
      {{kChangeStep4, models::saga::StepStatus::MakeBlocked("problem")}},
      false};

  const auto result = logics::saga::Execute(CreateSteps(client_mock),
                                            &models::saga::StepBase::Execute);

  ASSERT_EQ(result.IsSuccess(), false);

  ASSERT_EQ(client_mock.TimesCalled(kPrepareStep1), 1);
  ASSERT_EQ(client_mock.TimesCalled(kPrepareStep2), 1);
  ASSERT_EQ(client_mock.TimesCalled(kPrepareStep3), 1);
  ASSERT_EQ(client_mock.TimesCalled(kChangeStep4), 1);
  ASSERT_EQ(client_mock.TimesCalled(kAfterStep5), 0);

  client_mock.ValidateResult(result.ExecutedSteps());
}
