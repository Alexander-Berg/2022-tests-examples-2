#include <gtest/gtest.h>

#include <fmt/format.h>

#include <userver/formats/json/inline.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/logging/log.hpp>

#include <radio/utils/meta_format.hpp>

namespace hejmdal::radio::utils::meta {

TEST(TestMetaFormat, MainTest) {
  auto meta_value = formats::json::MakeObject(
      "string_field", "string_value", "int_field", 1, "double_field", 1.1002,
      "bool_field", false, "nested_fields",
      formats::json::MakeObject(
          "nested_str_field", "nested_str_value", "nested_int_field", 2,
          "nested_double_field", 2.12234, "nested2_fields",
          formats::json::MakeObject("nested2_double_field", 3.3)));

  try {
    MetaToFormatConverter converter;
    fmt::dynamic_format_arg_store<fmt::format_context> store;
    converter.MetaFieldsToFormatArgs(store, meta_value);
    std::string tpl =
        "string field: {string_field}\n"
        "int field: {int_field:#}\n"
        "double field: {double_field:.1f}\n"
        "bool field: {bool_field}\n"
        "nst string field: {nested_fields__nested_str_field}\n"
        "nst int field: {nested_fields__nested_int_field:#}\n"
        "nst double field: {nested_fields__nested_double_field:.2f}\n"
        "nst2 double field: "
        "{nested_fields__nested2_fields__nested2_double_field:.0f}\n";
    std::string result = fmt::vformat(tpl, store);
    std::string expected =
        "string field: string_value\n"
        "int field: 1.0\ndouble field: 1.1\n"
        "bool field: false\n"
        "nst string field: nested_str_value\n"
        "nst int field: 2.0\nnst double field: 2.12\n"
        "nst2 double field: 3\n";
    EXPECT_EQ(expected, result);
  } catch (const std::exception& e) {
    LOG_INFO() << e;
    FAIL();
  }
}

TEST(TestMetaFormat, RealMeta) {
  constexpr auto kMetaStr = R"=(
{
  "circuit_id": "cargo-matcher_354065::timings-p98",
  "metric_link_list": [
    {
      "text": "entry_timings",
      "address": "https://solomon.yandex-team.ru/admin/...",
      "type": "solomon_auto_graph"
    },
    {
      "text": "entry_timings-7d",
      "address": "https://solomon.yandex-team.ru/admin/...",
      "type": "solomon_auto_graph"
    },
    {
      "text": "entry_rps",
      "address": "https://solomon.yandex-team.ru/admin/...",
      "type": "solomon_auto_graph"
    }
  ],
  "service_name": "cargo-matcher",
  "service_id": 354065,
  "project_name": "taxi",
  "grafana_dashboard_link": {
    "text": "grafana dashboard",
    "address": "https://grafana.yandex-team.ru/d/JDNh6HyZk/nanny_taxi_cargo-matcher_stable",
    "type": "grafana_dashboard"
  },
  "yasm_dashboard_link": {
    "text": "system dashboard",
    "address": "https://yasm.yandex-team.ru/panel/...",
    "type": "yasm_panel"
  },
  "block_params": {
    "iqr_bounds": {
      "median": 31.0
    }
  }
}
)=";

  {
    auto meta_value = formats::json::FromString(kMetaStr);
    std::string tpl = "median: {block_params__iqr_bounds__median:.0f}";
    MetaToFormatConverter converter;
    fmt::dynamic_format_arg_store<fmt::format_context> store;
    converter.MetaFieldsToFormatArgs(store, meta_value);
    std::string result = fmt::vformat(tpl, store);
    std::string expected = "median: 31";
    EXPECT_EQ(expected, result);
  }
  {
    auto meta_value = formats::json::FromString(kMetaStr);
    std::string tpl =
        "service_name: {service_name}, median: "
        "{block_params__iqr_bounds__median:.0f}";
    MetaToFormatConverter converter;
    fmt::dynamic_format_arg_store<fmt::format_context> store;
    std::vector<std::string> args{"block_params__iqr_bounds__median",
                                  "service_name"};
    converter.MetaFieldsToFormatArgs(store, meta_value, args);
    std::string result = fmt::vformat(tpl, store);
    std::string expected = "service_name: cargo-matcher, median: 31";
    EXPECT_EQ(expected, result);
  }
}

}  // namespace hejmdal::radio::utils::meta
