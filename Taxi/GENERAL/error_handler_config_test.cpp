#include <userver/utest/utest.hpp>

#include <eventus/pipeline/config/error_handler.hpp>
#include <eventus/pipeline/config/fanout.hpp>
#include <eventus/pipeline/config/list_of_filters.hpp>
#include <eventus/pipeline/config/operation.hpp>
#include <eventus/pipeline/config/operation_node.hpp>
#include <eventus/pipeline/config/sink.hpp>
#include <eventus/pipeline/config/switch_operation.hpp>

namespace schema {

struct RetryPolicyT {
  int32_t attempts = 0;
  int32_t min_delay_ms = 0;
  std::optional<int32_t> max_delay_ms;
  int32_t delay_factor = 1;
};

struct ErrorHandlingPolicyT {
  std::unique_ptr<RetryPolicyT> retry_policy;
};

struct OperationNodeT {
  std::string name;
  bool disabled = false;
  std::unique_ptr<ErrorHandlingPolicyT> error_handling_policy;
};

}  // namespace schema

namespace eventus::pipeline::config {

template <>
RetryPolicy::RetryPolicy(const schema::RetryPolicyT& ext_config)
    : RetryPolicy(ext_config.attempts, ext_config.min_delay_ms,
                  ext_config.max_delay_ms, ext_config.delay_factor) {}

template <>
ErrorHandlingPolicy::ErrorHandlingPolicy(
    const schema::ErrorHandlingPolicyT& ext_config)
    : retry_policy{ext_config.retry_policy
                       ? std::optional<RetryPolicy>{*ext_config.retry_policy}
                       : std::nullopt},
      action_after_error{ActionAfterErroneousExecution::kPropagate} {}

template <>
OperationNode::OperationNode(const schema::OperationNodeT& ext_config)
    : name{ext_config.name},
      disabled{ext_config.disabled},
      error_policy(ext_config.error_handling_policy) {}

}  // namespace eventus::pipeline::config

TEST(PipelineBuilderSuite, ErorrHandlingPolicyTest) {
  {
    auto node = std::make_unique<eventus::pipeline::config::OperationNode>(
        std::make_unique<schema::OperationNodeT>());
    ASSERT_EQ(node->error_policy.has_value(), true);
    ASSERT_EQ(node->error_policy->retry_policy.has_value(), false);
  }

  {
    auto node_cfg = schema::OperationNodeT{
        "x", true, std::make_unique<schema::ErrorHandlingPolicyT>()};

    auto node = std::make_unique<eventus::pipeline::config::OperationNode>(
        std::make_unique<schema::OperationNodeT>(std::move(node_cfg)));
    ASSERT_EQ(node->error_policy.has_value(), true);
    ASSERT_EQ(node->error_policy->retry_policy.has_value(), false);
  }

  {
    schema::RetryPolicyT retry_policy{2, 0, {}, 1};

    schema::ErrorHandlingPolicyT error_handling_policy{
        std::make_unique<schema::RetryPolicyT>(std::move(retry_policy))};

    auto node_cfg =
        schema::OperationNodeT{"x", true,
                               std::make_unique<schema::ErrorHandlingPolicyT>(
                                   std::move(error_handling_policy))};

    auto node = std::make_unique<eventus::pipeline::config::OperationNode>(
        std::make_unique<schema::OperationNodeT>(std::move(node_cfg)));

    ASSERT_EQ(node->error_policy.has_value(), true);
    ASSERT_EQ(node->error_policy.value().retry_policy.has_value(), true);
    ASSERT_EQ(node->error_policy.value().retry_policy.value().attempts, 2);
  }
}
