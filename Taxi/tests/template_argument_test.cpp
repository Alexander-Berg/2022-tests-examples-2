#include <userver/utest/utest.hpp>

#include <models/template_argument.hpp>

namespace testing {
using ::eats_restapp_communications::models::ConfigDeliveryTypes;
using ::eats_restapp_communications::models::ConfigFormats;
using ::eats_restapp_communications::models::TemplateArgument;
using ::eats_restapp_communications::models::TemplateContext;

struct ConfigDeliveryTypesFixture {
  ConfigDeliveryTypes delivery_types;
  ConfigDeliveryTypesFixture() {
    delivery_types.push_back({"native", "доставка Яндекса"});
    delivery_types.push_back({"marketplace", "своя доставка"});
  }
};

struct TemplateArgumentParams {
  std::string templ{};
  std::string value{};
  std::optional<std::string> timezone{};
  std::optional<std::string> format{};
  std::string expected{};
};

struct TemplateArgumentTest : public ConfigDeliveryTypesFixture,
                              public TestWithParam<TemplateArgumentParams> {};

INSTANTIATE_TEST_SUITE_P(
    TemplateArgumentTest, TemplateArgumentTest,
    Values(TemplateArgumentParams{"{param}", "value", {}, {}, "value"},
           TemplateArgumentParams{"{param:spec}", "value", {}, {}, "value"},
           TemplateArgumentParams{
               "{param:delivery_type}", "value", {}, {}, "value"},
           TemplateArgumentParams{
               "{param:delivery_type}", "native", {}, {}, "доставка Яндекса"},
           TemplateArgumentParams{
               "{param:delivery_type}", "marketplace", {}, {}, "своя доставка"},
           TemplateArgumentParams{"{param:date}", "value", {}, {}, "value"},
           TemplateArgumentParams{
               "{param:date}", "2022-05-01", {}, {}, "01.05.2022"},
           TemplateArgumentParams{"{param:date#}", "value", {}, {}, "value"},
           TemplateArgumentParams{
               "{param:date#}", "2022-05-01", {}, {}, "01.05.2022"},
           TemplateArgumentParams{
               "{param:date#%m/%d/%Y}", "value", {}, {}, "value"},
           TemplateArgumentParams{
               "{param:date#%m/%d/%Y}", "05/01/2022", {}, {}, "01.05.2022"},
           TemplateArgumentParams{
               "{param:date}", "2022-05-01", {}, "%d|%m|%Y", "01|05|2022"},
           TemplateArgumentParams{"{param:datetime}", "value", {}, {}, "value"},
           TemplateArgumentParams{"{param:datetime}",
                                  "2022-05-01T12:05:30.123456+0000",
                                  {},
                                  {},
                                  "12:05 01.05.2022"},
           TemplateArgumentParams{
               "{param:datetime#}", "value", {}, {}, "value"},
           TemplateArgumentParams{"{param:datetime#}",
                                  "2022-05-01T12:05:30.123456+0000",
                                  {},
                                  {},
                                  "12:05 01.05.2022"},
           TemplateArgumentParams{
               "{param:datetime#iso}", "value", {}, {}, "value"},
           TemplateArgumentParams{"{param:datetime#iso}",
                                  "2022-05-01T12:05:30Z",
                                  {},
                                  {},
                                  "12:05 01.05.2022"},
           TemplateArgumentParams{
               "{param:datetime#rfc3339}", "value", {}, {}, "value"},
           TemplateArgumentParams{"{param:datetime#rfc3339}",
                                  "2022-05-01T12:05:30.123456+00:00",
                                  {},
                                  {},
                                  "12:05 01.05.2022"},
           TemplateArgumentParams{
               "{param:datetime#taximeter}", "value", {}, {}, "value"},
           TemplateArgumentParams{"{param:datetime#taximeter}",
                                  "2022-05-01T12:05:30.123456Z",
                                  {},
                                  {},
                                  "12:05 01.05.2022"},
           TemplateArgumentParams{
               "{param:datetime#%m/%d/%Y %H:%M:%S}", "value", {}, {}, "value"},
           TemplateArgumentParams{"{param:datetime#%m/%d/%Y %H:%M:%S}",
                                  "05/01/2022 12:05:30",
                                  {},
                                  {},
                                  "12:05 01.05.2022"},
           TemplateArgumentParams{"{param:datetime}",
                                  "2022-05-01T12:05:30.123456+0000",
                                  {},
                                  "%H:%M:%S",
                                  "12:05:30"},
           TemplateArgumentParams{"{param:datetime}",
                                  "2022-05-01T12:05:30.123456+0000",
                                  "Europe/Moscow",
                                  {},
                                  "15:05 01.05.2022"},
           TemplateArgumentParams{"{param:datetime#%m/%d/%Y %H:%M:%S}",
                                  "05/01/2022 12:05:30",
                                  "Europe/Moscow",
                                  {},
                                  "12:05 01.05.2022"}));

TEST_P(TemplateArgumentTest, should_format_arguments_with_specifiers) {
  const auto& params = GetParam();
  const ConfigFormats formats{params.format, params.format};
  const TemplateContext context{params.timezone, formats, delivery_types};
  TemplateArgument argument(params.value, context);
  ASSERT_EQ(fmt::format(params.templ, fmt::arg("param", argument)),
            params.expected);
}

}  // namespace testing
