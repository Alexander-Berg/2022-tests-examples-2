#include "view.hpp"
#include <gtest/gtest.h>
namespace {

struct TestData {
  std::string app;
  std::vector<std::string> applications;
  bool expected;
};

class NotificationTest : public testing::TestWithParam<TestData> {};

const TestData kNotificationsTests[] = {
    {"go", {"go", "eda_native"}, true},
    {"go", {"eda_native"}, false},
    {"go", {"go"}, true},
    {"eda_native", {"go"}, false},
    {"eda_native", {}, true},
    {"eda_native", {"test", "test1", "eda_native", "test2"}, true},
    {"eda_native", {"test", "test1", "test2"}, false},
};
}  // namespace

TEST_P(NotificationTest, isApplicationAllowed) {
  const auto& data = GetParam();
  auto result = handlers::v1_notification::post::isApplicationAllowed(
      data.app, data.applications);
  EXPECT_EQ(result, data.expected);
}

INSTANTIATE_TEST_SUITE_P(NotificationValue, NotificationTest,
                         testing::ValuesIn(kNotificationsTests));
