#include <gtest/gtest.h>

#include <userver/formats/json/serialize.hpp>

#include "json.hpp"

TEST(Json, AssignAtPath) {
  formats::json::ValueBuilder actual_bld{formats::json::Type::kObject};
  utils::json::AssignAtPath(actual_bld, "one", 1);
  utils::json::AssignAtPath(actual_bld, "hello.two", 2.0);
  utils::json::AssignAtPath(actual_bld, "hello.world.three", "three");

  formats::json::ValueBuilder expected_bld{formats::json::Type::kObject};
  expected_bld["one"] = 1;
  expected_bld["hello"]["two"] = 2.0;
  expected_bld["hello"]["world"]["three"] = "three";

  const auto expected = expected_bld.ExtractValue();
  const auto actual = actual_bld.ExtractValue();

  EXPECT_EQ(expected, actual)
      << "Expect: " << formats::json::ToString(expected) << std::endl
      << "Actual: " << formats::json::ToString(actual);
}
