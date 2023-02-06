#include "call.hpp"

#include <gtest/gtest.h>

namespace tests {

namespace {

void RunTest(const formats::json::Value& scheme) {
  transformer::strategy::Call strategy;
  strategy.Parse(scheme, {}, {});
}

}  // namespace

TEST(Call, HappyPath) {
  const auto scheme = formats::json::FromString(R"(
  "custom_strategy_name"
)");

  EXPECT_NO_THROW(RunTest(scheme));
}

TEST(Call, SystemCallFail) {
  const auto scheme = formats::json::FromString(R"(
"__system__"
)");

  EXPECT_THROW(RunTest(scheme), std::runtime_error);
}

}  // namespace tests
