#include <endpoints/full/plugins/subtitle/subplugins/subtitle_waiting.hpp>
#include <experiments3/new_summary_order_subtitle.hpp>

#include <l10n/errors.hpp>
#include <tests/context_mock_test.hpp>
#include <tests/endpoints/common/service_level_mock_test.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

namespace routestats::plugins::subtitle {

namespace {

using namespace client_zone_geoindex::models;

formats::json::Value MakeOrderSubtitleExp() {
  using formats::json::ValueBuilder;

  ValueBuilder SubtitleExp{};
  SubtitleExp["enabled"] = true;
  SubtitleExp["type"] = "free_waiting";

  return SubtitleExp.ExtractValue();
}

MinimalPrice BuildDefaultMinimalPrice(const std::string& category_name,
                                      const double waiting_included) {
  MinimalPrice price{};
  price.category_name = category_name;
  price.category_type = MinimalPrice::CategoryType::kApplication;
  // 00:00 - 22:00
  price.time_from = std::chrono::minutes(0);
  price.time_to = std::chrono::minutes(1320);
  price.day_type =
      client_zone_geoindex::models::MinimalPrice::DayType::kEveryday;
  price.waiting_included = waiting_included;
  return price;
}

full::ContextData PrepareContext() {
  full::ContextData context = test::full::GetDefaultContext();

  context.user.auth_context.locale = "ru";

  using SubtitleExp = experiments3::NewSummaryOrderSubtitle;
  core::ExpMappedData exp_mapped_data{};
  exp_mapped_data[SubtitleExp::kName] = {
      SubtitleExp::kName, MakeOrderSubtitleExp(), {}};
  context.experiments.uservices_routestats_exps = {std::move(exp_mapped_data)};
  context.rendering = test::full::GetDefaultRendering();

  context.zone->tariff = {"moscow",
                          "moscow",
                          {},
                          {BuildDefaultMinimalPrice("econom", 3.0),
                           BuildDefaultMinimalPrice("vip", 0.0)}};

  return context;
}

}  // namespace

void TestSubtitlePlugin(const std::string& class_,
                        const std::optional<std::string>& expected_subtitle) {
  SubtitleWaitingPlugin plugin;
  const auto context = test::full::MakeTopLevelContext(PrepareContext());
  const std::optional<std::string>& result_subtitle =
      plugin.GetSubtitle(class_, context);
  ASSERT_EQ(result_subtitle, expected_subtitle);
}

TEST(SubtitleByWaitingPlugin, waiting_valid) {
  // 9:15 Wed
  const auto now =
      std::chrono::system_clock::time_point(std::chrono::seconds(1605075300));
  utils::datetime::MockNowSet(now);

  TestSubtitlePlugin("econom", "new_summary.order_subtitle.waiting_time##ru");
}

TEST(SubtitleByWaitingPlugin, paid_waiting_valid) {
  // 9:15 Wed
  const auto now =
      std::chrono::system_clock::time_point(std::chrono::seconds(1605075300));
  utils::datetime::MockNowSet(now);

  TestSubtitlePlugin("vip", "new_summary.order_subtitle.paid_waiting##ru");
}
}  // namespace routestats::plugins::subtitle
