#include <gmock/gmock.h>

#include <fmt/format.h>

#include <testing/taxi_config.hpp>
#include <userver/formats/json/value_builder.hpp>
#include <userver/utils/datetime.hpp>
#include <userver/utils/mock_now.hpp>

#include <clients/eats-core-order-support/client_mock_base.hpp>
#include "actions_filter/actions_filter.hpp"

namespace eats_proactive_support::models {

bool operator==(const Action& left, const Action& right) {
  return (left.id == right.id && left.external_id == right.external_id &&
          left.problem_id == right.problem_id &&
          left.order_nr == right.order_nr && left.type == right.type &&
          left.payload == right.payload && left.state == right.state &&
          left.skipped_at == right.skipped_at &&
          left.skip_reason == right.skip_reason &&
          left.performed_at == right.performed_at &&
          left.created_at == right.created_at &&
          left.updated_at == right.updated_at);
}

}  // namespace eats_proactive_support::models

namespace {

namespace models = eats_proactive_support::models;
namespace actions_filter = eats_proactive_support::actions_filter;

using defs::internal::pg_action::ActionState;
using defs::internal::pg_action::ActionType;
using defs::internal::pg_problem::ProblemType;

using models::Action;
using models::Problem;

using CoreClientRequest = clients::eats_core_order_support::
    internal_api_v1_order_support_meta::get::Request;
using CoreClientResponse = clients::eats_core_order_support::
    internal_api_v1_order_support_meta::get::Response;
using CoreClientCommandControl =
    clients::eats_core_order_support::CommandControl;
using clients::eats_core_order_support::CancellationInfo;
using clients::eats_core_order_support::OperatorInfo;

constexpr const char* kTestOrderNr = "201111-321456";
constexpr const char* kTimeMockNow = "2020-01-01T10:00:00.00Z";
constexpr const char* kTimeInFuture = "2020-01-01T10:00:01.00Z";
constexpr const char* kTimeBeforeOperatorAssignmentLimit =
    "2020-01-01T09:55:00.00Z";
constexpr const char* kTimeAfterOperatorAssignmentLimit =
    "2020-01-01T09:55:01.00Z";

struct TestParams {
  // Input.
  std::optional<std::string> time_operator_assigned_at;
  std::optional<bool> is_notified_by_operator;
  ProblemType problem_type;
  ActionType action_type;
  // Expected output.
  ActionState expected_state;
  std::optional<std::string> expected_skip_reason;
};

Problem InitProblem(ProblemType problem_type, const std::string& order_nr) {
  Problem problem;
  problem.id = 12345;
  problem.order_nr = order_nr;
  problem.type = problem_type;
  problem.created_at = std::chrono::system_clock::now();
  problem.updated_at = std::chrono::system_clock::now();

  return problem;
}

void InitAction(const TestParams& test_params, const std::string& order_nr,
                int iteration, Action& input, Action& expected_output) {
  // Init input action.
  input.id = iteration;
  input.external_id = fmt::format("external_id_{}", iteration);
  input.problem_id = 1000 + iteration;
  input.order_nr = order_nr;
  input.type = test_params.action_type;
  input.state = ActionState::kCreated;
  input.skipped_at = std::nullopt;
  input.skip_reason = std::nullopt;
  input.performed_at = std::nullopt;
  input.created_at = std::chrono::system_clock::now();
  input.updated_at = std::chrono::system_clock::now();

  formats::json::ValueBuilder json_builder(formats::json::Type::kObject);
  json_builder["test_param"] = "test_value";

  input.payload = json_builder.ExtractValue();

  // Init output action.
  expected_output = input;
  expected_output.state = test_params.expected_state;
  if (test_params.expected_state == ActionState::kSkipped)
    expected_output.skipped_at = utils::datetime::Now();
  if (test_params.expected_skip_reason.has_value())
    expected_output.skip_reason = test_params.expected_skip_reason;
}

class CoreOrderSupportClient
    : public clients::eats_core_order_support::ClientMockBase {
 public:
  CoreOrderSupportClient(const TestParams& test_params)
      : test_params_(test_params) {}

  CoreClientResponse InternalApiV1OrderSupportMeta(
      const CoreClientRequest& /*request*/,
      const CoreClientCommandControl& /*command_control*/ = {}) const override {
    CoreClientResponse response;

    if (test_params_.time_operator_assigned_at.has_value()) {
      const auto assigned_at = utils::datetime::Stringtime(
          *test_params_.time_operator_assigned_at, "UTC");

      response.operator_ = {"operator_login", assigned_at};
    }

    if (test_params_.is_notified_by_operator.has_value()) {
      response.cancellation = {*test_params_.is_notified_by_operator};
    }

    return response;
  }

 private:
  const TestParams& test_params_;
};

void TestExpectedOutputCase(const TestParams& test_params,
                            const taxi_config::TaxiConfig& taxi_config,
                            int iteration) {
  // Init test case.
  const Problem problem = InitProblem(test_params.problem_type, kTestOrderNr);

  std::vector<Action> input(1);
  std::vector<Action> expected_output(1);
  InitAction(test_params, kTestOrderNr, iteration, input[0],
             expected_output[0]);

  CoreOrderSupportClient core_client(test_params);

  // Call actions filter.
  for (auto& action : input) {
    eats_proactive_support::actions_filter::FilterAction(
        kTestOrderNr, problem, action, core_client, taxi_config);
  }

  // Check result.
  ASSERT_EQ(input, expected_output);
}

}  // namespace

TEST(ActionsFilter, ExpectedOutput) {
  // Define test cases.
  const TestParams test_params_cases[] = {

      // Other types of actions must not be changed by filter.
      {std::nullopt, std::nullopt, ProblemType::kOrderCancelled,
       ActionType::kOrderCancel, ActionState::kCreated, std::nullopt},

      // ProblemType::kOrderCancelled. time_operator_assigned_at is null.
      // Result depends on is_notified_by_operator.
      {std::nullopt, std::nullopt, ProblemType::kOrderCancelled,
       ActionType::kEaterNotification, ActionState::kCreated, std::nullopt},
      {std::nullopt, false, ProblemType::kOrderCancelled,
       ActionType::kEaterNotification, ActionState::kCreated, std::nullopt},
      {std::nullopt, true, ProblemType::kOrderCancelled,
       ActionType::kEaterNotification, ActionState::kSkipped,
       models::action::skip_reasons::kNotifiedAboutCancellation},
      {std::nullopt, std::nullopt, ProblemType::kOrderCancelled,
       ActionType::kEaterRobocall, ActionState::kCreated, std::nullopt},
      {std::nullopt, false, ProblemType::kOrderCancelled,
       ActionType::kEaterRobocall, ActionState::kCreated, std::nullopt},
      {std::nullopt, true, ProblemType::kOrderCancelled,
       ActionType::kEaterRobocall, ActionState::kSkipped,
       models::action::skip_reasons::kNotifiedAboutCancellation},

      // Any problem type. is_notified_by_operator is null.
      // Result depends on operator assignment time.
      {std::nullopt, std::nullopt, ProblemType::kOrderCancelled,
       ActionType::kEaterNotification, ActionState::kCreated, std::nullopt},
      {kTimeInFuture, std::nullopt, ProblemType::kOrderCancelled,
       ActionType::kEaterNotification, ActionState::kCreated, std::nullopt},
      {kTimeBeforeOperatorAssignmentLimit, std::nullopt,
       ProblemType::kOrderCancelled, ActionType::kEaterNotification,
       ActionState::kCreated, std::nullopt},
      {kTimeAfterOperatorAssignmentLimit, std::nullopt,
       ProblemType::kOrderCancelled, ActionType::kEaterNotification,
       ActionState::kSkipped,
       models::action::skip_reasons::kAssignedOperatorTime},
      {std::nullopt, std::nullopt, ProblemType::kOrderCancelled,
       ActionType::kEaterRobocall, ActionState::kCreated, std::nullopt},
      {kTimeInFuture, std::nullopt, ProblemType::kOrderCancelled,
       ActionType::kEaterRobocall, ActionState::kCreated, std::nullopt},
      {kTimeBeforeOperatorAssignmentLimit, std::nullopt,
       ProblemType::kOrderCancelled, ActionType::kEaterRobocall,
       ActionState::kCreated, std::nullopt},
      {kTimeAfterOperatorAssignmentLimit, std::nullopt,
       ProblemType::kOrderCancelled, ActionType::kEaterRobocall,
       ActionState::kSkipped,
       models::action::skip_reasons::kAssignedOperatorTime},
  };

  // Mock now.
  const auto now = utils::datetime::Stringtime(kTimeMockNow, "UTC");
  utils::datetime::MockNowSet(now);

  // Taxi config.
  const auto taxi_config_ptr = dynamic_config::GetDefaultSnapshot();
  const auto taxi_config = taxi_config_ptr.Get<taxi_config::TaxiConfig>();

  // Execute all test cases.
  int iteration = 0;
  for (const auto& test_params : test_params_cases) {
    ++iteration;

    TestExpectedOutputCase(test_params, taxi_config, iteration);
  }
}

TEST(ActionsFilter, MultipleActions) {
  const TestParams test_params_cases[] = {
      {std::nullopt, true, ProblemType::kOrderCancelled,
       ActionType::kOrderCancel, ActionState::kCreated, std::nullopt},
      {std::nullopt, true, ProblemType::kOrderCancelled,
       ActionType::kEaterNotification, ActionState::kSkipped,
       models::action::skip_reasons::kNotifiedAboutCancellation},
      {std::nullopt, true, ProblemType::kOrderCancelled,
       ActionType::kOrderCancel, ActionState::kCreated, std::nullopt}};

  const auto now = utils::datetime::Stringtime(kTimeMockNow, "UTC");
  utils::datetime::MockNowSet(now);

  const auto taxi_config_ptr = dynamic_config::GetDefaultSnapshot();
  const auto taxi_config = taxi_config_ptr.Get<taxi_config::TaxiConfig>();

  const auto num_cases = std::size(test_params_cases);
  std::vector<Action> input(num_cases);
  std::vector<Action> expected_output(num_cases);
  for (size_t i = 0; i < num_cases; ++i) {
    InitAction(test_params_cases[i], kTestOrderNr, (int)i + 1, input[i],
               expected_output[i]);
  }

  const Problem problem =
      InitProblem(ProblemType::kOrderCancelled, kTestOrderNr);

  CoreOrderSupportClient core_client(test_params_cases[0]);

  for (auto& action : input) {
    eats_proactive_support::actions_filter::FilterAction(
        kTestOrderNr, problem, action, core_client, taxi_config);
  }

  // Check result.
  ASSERT_EQ(input, expected_output);
}
