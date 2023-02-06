#include "aliases.hpp"

#include <gtest/gtest.h>

namespace tests {

namespace {

void RunTest(const formats::json::Value& scheme) {
  transformer::strategy::Aliases strategy;
  strategy.Parse(scheme, {}, {});
}

}  // namespace

TEST(Aliases, HappyPath) {
  const auto scheme = formats::json::FromString(R"(
{
  "data1#string": "str",
  "data2#integer": 10
}
)");

  EXPECT_NO_THROW(RunTest(scheme));
}

TEST(Aliases, NoAglOperator) {
  const auto scheme = formats::json::FromString(R"(
{
  "data1#string": "str",
  "data2": 10
}
)");

  EXPECT_THROW(RunTest(scheme), std::runtime_error);
}

TEST(Aliases, NameConflict) {
  const auto scheme = formats::json::FromString(R"(
{
  "data#string": "str",
  "data#integer": 10
}
)");

  EXPECT_THROW(RunTest(scheme), std::runtime_error);
}

}  // namespace tests
