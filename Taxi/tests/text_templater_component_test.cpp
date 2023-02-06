#include <userver/utest/utest.hpp>

#include <optional>
#include <testing/taxi_config.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/utest/utest.hpp>
#include "types/metric_value.hpp"

#include "components/text_templater.hpp"

namespace eats_report_storage::components {

namespace impl {

inline bool operator==(const Param& lhs, const Param& rhs) {
  return std::make_tuple(lhs.arg, lhs.type, lhs.map) ==
         std::make_tuple(rhs.arg, rhs.type, rhs.map);
}

inline bool operator==(const Template& lhs, const Template& rhs) {
  return std::make_tuple(lhs.slug, lhs.text, lhs.params) ==
         std::make_tuple(rhs.slug, rhs.text, rhs.params);
}
}  // namespace impl

using namespace ::testing;

impl::ConfigTemplater MakeTemplatesEmpty() {
  const auto json_s =
      R"({
    "templates": []
})";
  const auto json = formats::json::FromString(json_s);
  return taxi_config::eats_report_storage_text_templater::Parse(
      json, formats::parse::To<impl::ConfigTemplater>());
}

impl::ConfigTemplater MakeTemplatesWithParams() {
  const auto json_s =
      R"({
"templates": [
  {
    "slug": "suggest_example_text",
    "template": "Просто текст без параметров"
  },
  {
    "slug": "metric_example_text",
    "template": "Текст только с метрикой {order_count:current}",
    "params": [
      {
        "type": "metric",
        "arg": "order_count"
      }
    ]
  },
  {
    "slug": "map_example_text",
    "template": "Текст только с мапой {period}",
    "params": [
      {
        "type": "map",
        "arg": "period",
        "map": [
          {
            "key": "day",
            "value": "день"
          },
          {
            "key": "week",
            "value": "неделя"
          },
          {
            "key": "year",
            "value": "год"
          }
        ]
      }
    ]
  },
  {
    "slug": "params_example_text",
    "template": "Текст с разными параметрами: {order_count:total}, {period}",
    "params": [
      {
        "type": "metric",
        "arg": "order_count"
      },
      {
        "type": "map",
        "arg": "period",
        "map": [
          {
            "key": "day",
            "value": "день"
          },
          {
            "key": "week",
            "value": "неделя"
          },
          {
            "key": "year",
            "value": "год"
          }
        ]
      }
    ]
  }
]
})";
  const auto json = formats::json::FromString(json_s);
  return taxi_config::eats_report_storage_text_templater::Parse(
      json, formats::parse::To<impl::ConfigTemplater>());
}

struct GetTextTemplaterTestAsIt {
  std::string data;
};

class TextTemplaterTestAsIt
    : public ::testing::TestWithParam<GetTextTemplaterTestAsIt> {
 public:
  impl::Templater impl_;
  TextTemplaterTestAsIt() : impl_() {}
};

const std::vector<GetTextTemplaterTestAsIt> kGetTextTemplaterTestAsIt{
    {"q"}, {"1"}, {"templ"}, {"template"}, {"template:"},
};

INSTANTIATE_TEST_SUITE_P(GetTextTemplaterTestAsIt, TextTemplaterTestAsIt,
                         ::testing::ValuesIn(kGetTextTemplaterTestAsIt));

TEST_P(TextTemplaterTestAsIt, success_fmt_format_metric_value) {
  const auto& param = GetParam();
  ASSERT_EQ(impl_.GetText(param.data), param.data);
}

struct TextTemplaterTest : public Test {
  impl::Templater impl_;
  TextTemplaterTest() : impl_() {}
};

TEST_F(TextTemplaterTest, parse_empty_list) {
  auto data = impl_.ParseTemplates(MakeTemplatesEmpty());

  auto expected = std::unordered_map<std::string, impl::Template>{};
  ASSERT_EQ(data, expected);
}

TEST_F(TextTemplaterTest, parse_list_with_params) {
  auto data = impl_.ParseTemplates(MakeTemplatesWithParams());

  auto expected = std::unordered_map<std::string, impl::Template>{};
  {
    std::unordered_map<std::string, std::string> map{};
    map["day"] = "день";
    map["week"] = "неделя";
    map["year"] = "год";
    impl::ParamList params{};
    params["order_count"] =
        impl::Param{"order_count", impl::ParamType::kMetric, std::nullopt};
    params["period"] = impl::Param{"period", impl::ParamType::kMap, map};
    expected["params_example_text"] = impl::Template{
        "params_example_text",
        "Текст с разными параметрами: {order_count:total}, {period}", params};
  }

  {
    std::unordered_map<std::string, std::string> map{};
    map["day"] = "день";
    map["week"] = "неделя";
    map["year"] = "год";
    impl::ParamList params{};
    params["period"] = impl::Param{"period", impl::ParamType::kMap, map};
    expected["map_example_text"] = impl::Template{
        "map_example_text", "Текст только с мапой {period}", params};
  }

  {
    expected["suggest_example_text"] =
        impl::Template{"suggest_example_text", "Просто текст без параметров",
                       impl::ParamList{}};
  }
  {
    impl::ParamList params{};
    std::unordered_map<std::string, std::string> map{};
    params["order_count"] =
        impl::Param{"order_count", impl::ParamType::kMetric, std::nullopt};

    expected["metric_example_text"] =
        impl::Template{"metric_example_text",
                       "Текст только с метрикой {order_count:current}", params};
  }

  ASSERT_EQ(data, expected);
}

TEST_F(TextTemplaterTest, using_get_text_with_empty_slug) {
  std::unordered_map<std::string, std::string> map{};
  ASSERT_THROW(impl_.GetText<types::MetricValue>("", nullptr, map),
               ErrorGetTemplate);
}

TEST_F(TextTemplaterTest, using_get_text_with_not_find_slug) {
  std::unordered_map<std::string, std::string> map{};
  ASSERT_THROW(impl_.GetText<types::MetricValue>("template:slug_not_found",
                                                 nullptr, map),
               ErrorGetTemplate);
}

TEST_F(TextTemplaterTest, using_get_text_find_slug) {
  impl_.ParseTemplates(MakeTemplatesWithParams());
  std::unordered_map<std::string, std::string> map{};
  ASSERT_EQ(impl_.GetText<types::MetricValue>("template:suggest_example_text",
                                              nullptr, map),
            "Просто текст без параметров");
}

TEST_F(TextTemplaterTest, using_get_text_find_slug_with_map) {
  impl_.ParseTemplates(MakeTemplatesWithParams());
  std::unordered_map<std::string, std::string> map{};
  map["period"] = "week";
  ASSERT_EQ(impl_.GetText<types::MetricValue>("template:map_example_text",
                                              nullptr, map),
            "Текст только с мапой неделя");
}

TEST_F(TextTemplaterTest, using_get_text_find_slug_with_map_error_key) {
  impl_.ParseTemplates(MakeTemplatesWithParams());
  std::unordered_map<std::string, std::string> map{};
  map["perio"] = "week";
  ASSERT_THROW(impl_.GetText<types::MetricValue>("template:map_example_text",
                                                 nullptr, map),
               ErrorGetTemplate);
}

TEST_F(TextTemplaterTest, using_get_text_find_slug_with_map_error_value) {
  impl_.ParseTemplates(MakeTemplatesWithParams());
  std::unordered_map<std::string, std::string> map{};
  map["period"] = "weekly";
  ASSERT_EQ(impl_.GetText<types::MetricValue>("template:map_example_text",
                                              nullptr, map),
            "Текст только с мапой weekly");
}

TEST_F(TextTemplaterTest, using_get_text_find_slug_with_metric_error_snapshot) {
  impl_.ParseTemplates(MakeTemplatesWithParams());
  std::unordered_map<std::string, std::string> map{};
  ASSERT_THROW(impl_.GetText<types::MetricValue>("template:metric_example_text",
                                                 nullptr, map),
               ErrorGetTemplate);
}

};  // namespace eats_report_storage::components
