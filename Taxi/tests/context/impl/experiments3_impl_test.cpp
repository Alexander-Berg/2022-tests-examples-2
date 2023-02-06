#include <core/context/experiments3.hpp>

#include <userver/utest/utest.hpp>

namespace routestats::core {
TEST(ExperimentsEnabled, Basic) {
  {
    core::Experiments exps;
    ASSERT_FALSE(exps.IsEnabled("test_exp"));
  }

  {
    experiments3::models::ExperimentResult exp_result;
    exp_result.value = formats::json::FromString(R"({"key": "value"})");

    core::Experiments exps{{{"test_exp", exp_result}}};
    ASSERT_FALSE(exps.IsEnabled("test_exp"));
  }

  {
    experiments3::models::ExperimentResult exp_result;
    exp_result.value = formats::json::FromString(R"({"enabled": 1234})");

    core::Experiments exps{{{"test_exp", exp_result}}};
    ASSERT_FALSE(exps.IsEnabled("test_exp"));
  }

  {
    experiments3::models::ExperimentResult exp_result;
    exp_result.value = formats::json::FromString(R"({"enabled": true})");

    core::Experiments exps{{{"test_exp", exp_result}}};
    ASSERT_TRUE(exps.IsEnabled("test_exp"));
  }
}
}  // namespace routestats::core
