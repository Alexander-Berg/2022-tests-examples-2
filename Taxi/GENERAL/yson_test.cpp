#include "yson.hpp"

#include <functional>
#include <limits>
#include <sstream>

#include <gtest/gtest.h>
#include <json/value.h>

class TestYsonWriter
    : public ::testing::TestWithParam<
          std::tuple<std::function<Json::Value()>, std::string>> {};

TEST_P(TestYsonWriter, AddField) {
  std::ostringstream ss;
  auto writer = yson::text_writer(yson::output::from_ostream(ss),
                                  yson::stream_type::list_fragment);
  writer.begin_stream();
  writer.begin_map();

  utils::helpers::AddField(writer, "key", std::get<0>(GetParam())());

  writer.end_map();
  writer.end_stream();

  ASSERT_EQ(ss.str(), std::get<1>(GetParam()));
}

INSTANTIATE_TEST_CASE_P(
    TestYsonWriterPairs, TestYsonWriter,
    ::testing::Values(
        std::make_tuple([]() { return Json::Value{}; }, "{\"key\" = #};\n"),
        std::make_tuple([]() { return Json::Value{true}; },
                        "{\"key\" = %true};\n"),
        std::make_tuple([]() { return Json::Value{false}; },
                        "{\"key\" = %false};\n"),
        std::make_tuple([]() { return Json::Value{-1}; }, "{\"key\" = -1};\n"),
        std::make_tuple([]() { return Json::Value{1u}; }, "{\"key\" = 1u};\n"),
        std::make_tuple([]() { return Json::Value{1.0}; },
                        "{\"key\" = 1.0000000000000000};\n"),
        std::make_tuple([]() { return Json::Value{-1.0}; },
                        "{\"key\" = -1.0000000000000000};\n"),
        std::make_tuple(
            []() {
              return Json::Value{std::numeric_limits<double>::infinity()};
            },
            "{\"key\" = %inf};\n"),
        std::make_tuple(
            []() {
              return Json::Value{-std::numeric_limits<double>::infinity()};
            },
            "{\"key\" = %-inf};\n"),
        std::make_tuple(
            []() {
              return Json::Value{std::numeric_limits<double>::quiet_NaN()};
            },
            "{\"key\" = %nan};\n"),
        std::make_tuple([]() { return Json::Value{""}; },
                        "{\"key\" = \"\"};\n"),
        std::make_tuple([]() { return Json::Value{"value"}; },
                        "{\"key\" = \"value\"};\n"),
        std::make_tuple(
            []() {
              Json::Value res(Json::objectValue);
              res["subkey"] = "value";
              return res;
            },
            "{\"key\" = {\"subkey\" = \"value\"}};\n"),
        std::make_tuple(
            []() {
              Json::Value res(Json::arrayValue);
              res.append("value1");
              res.append("value2");
              return res;
            },
            "{\"key\" = [\"value1\"; \"value2\"]};\n")), );
