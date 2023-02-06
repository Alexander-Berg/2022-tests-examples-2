#include <logging/log_extra.hpp>
#include <models/cached/user_antifraud_rules.hpp>

#include <gtest/gtest.h>

#include <string>
#include <vector>

static std::vector<std::string> genRange(const std::string& prefix,
                                         size_t count) {
  std::vector<std::string> result;
  while (count-- != 0) {
    result.push_back(prefix + std::to_string(count));
  }
  return result;
}

TEST(TestUserAntifraudRules, TryForBigAmount) {
  models::UserAntifraudRules rules;

  const std::vector<std::string>& values = genRange("value", 2000);
  const std::vector<std::string> prop_names{"metrica_uuid", "metrica_device_id",
                                            "ip", "mac", "instance_id"};
  for (const auto& name : prop_names) {
    for (const auto& value : values) {
      rules.AddStringRule(name, value);
    }
  }
  EXPECT_EQ(rules.Size(), 10000u);

  // worst case
  {
    models::UserAntifraudProperties props;
    props.str_props["instance_id"] = "sdfsdfsdfsdfsdf";
    EXPECT_EQ(rules.Satisfy(props, LogExtra{}), false);
  }

  // average case
  {
    models::UserAntifraudProperties props;
    props.str_props["metrica_uuid"] = values[values.size() / 2];
    EXPECT_EQ(rules.Satisfy(props, LogExtra{}), true);
  }

  // worst case
  {
    models::UserAntifraudProperties props;
    props.str_props["instance_id"] = "";
    EXPECT_EQ(rules.Satisfy(props, LogExtra{}), false);
  }

  // "best" case
  {
    models::UserAntifraudProperties props;
    props.str_props["metrica_uuid"] = values.front();
    EXPECT_EQ(rules.Satisfy(props, LogExtra{}), true);
  }
}
