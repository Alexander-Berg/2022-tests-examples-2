#include <gtest/gtest.h>

#include <iostream>

#include <testing/source_path.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value.hpp>

#include <experiments3/utils/aggregators.hpp>

namespace exp3 = experiments3::utils;

namespace {
const std::string kFilesDir =
    utils::CurrentSourcePath("src/tests/static/experiment_result/");
}

TEST(MergeValues, CorrectSimpleMerge) {
  formats::json::ValueBuilder result;
  std::vector<formats::json::Value> values(2);
  values[0] = formats::json::FromString("{\"key1\":\"value\"}");
  values[1] = formats::json::FromString("{\"key2\":\"value\"}");

  ASSERT_EQ(
      exp3::DictsRecursiveMerge(values),
      formats::json::FromString("{\"key1\":\"value\",\"key2\":\"value\"}"));
}

TEST(MergeValues, CorrectRecursiveMerge) {
  formats::json::ValueBuilder result;
  std::vector<formats::json::Value> values(3);
  values[0] = formats::json::FromString("{\"key1\":{\"subkey1\":228}}");
  values[1] = formats::json::FromString("{\"key1\":{\"subkey2\":\"value\"}}");
  values[2] = formats::json::FromString("{\"key2\":{\"subkey3\":228.228}}");

  ASSERT_EQ(exp3::DictsRecursiveMerge(values),
            formats::json::blocking::FromFile(kFilesDir + "value1.json"));
}

TEST(MergeValues, IncorrectRecursiveMerge) {
  formats::json::ValueBuilder result;
  std::vector<formats::json::Value> values(3);
  values[0] = formats::json::FromString("{\"key1\":{\"subkey1\":228}}");
  values[1] = formats::json::FromString("{\"key1\":228}");

  bool exception_caught = false;

  try {
    ASSERT_EQ(exp3::DictsRecursiveMerge(values),
              formats::json::blocking::FromFile(kFilesDir + "value1.json"));
  } catch (const std::logic_error& logic_exc) {
    exception_caught = true;
  }

  ASSERT_TRUE(exception_caught);
}

TEST(MergeValues, NullOrEmptyCases) {
  formats::json::ValueBuilder result;

  auto value1 = formats::json::FromString("{\"key\":null}");
  auto value2 = formats::json::FromString("{\"key\":[]}");
  auto value3 = formats::json::FromString("{\"key\":{}}");

  size_t exceptions_caught = 0;

  try {
    std::vector<formats::json::Value> values(2);
    exp3::DictsRecursiveMerge({value1, value2});
  } catch (const std::logic_error& logic_exc) {
    ++exceptions_caught;
  }
}
