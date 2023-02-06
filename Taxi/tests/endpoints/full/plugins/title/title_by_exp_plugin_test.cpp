#include <endpoints/full/plugins/title/subplugins/title_by_exp.hpp>
#include <experiments3/order_button_title.hpp>
#include <tests/context_mock_test.hpp>

#include <userver/utest/utest.hpp>

namespace routestats::full::title {

namespace {

formats::json::Value MakeOrderTitleExp() {
  using formats::json::ValueBuilder;

  ValueBuilder TitleExp{};
  TitleExp["enabled"] = true;
  TitleExp["tanker_key"] = "yango_order_key";

  return TitleExp.ExtractValue();
}

std::shared_ptr<const plugins::top_level::Context> MakeContext() {
  auto ctx = test::full::GetDefaultContext();

  ctx.user.auth_context.locale = "ru";
  ctx.rendering = test::full::GetDefaultRendering();

  using TitleExp = experiments3::OrderButtonTitle;

  core::ExpMappedData exp_mapped_data{};
  exp_mapped_data[TitleExp::kName] = {TitleExp::kName, MakeOrderTitleExp(), {}};
  ctx.experiments.uservices_routestats_exps = {std::move(exp_mapped_data)};

  return test::full::MakeTopLevelContext(std::move(ctx));
}

void TestTitleByExpPlugin(const std::string& class_,
                          const std::optional<std::string>& expected_title) {
  TitleByExpPlugin plugin;
  const auto result_title = plugin.GetTitle(class_, MakeContext());
  ASSERT_EQ(result_title.value_or("(none)"), expected_title.value_or("(none)"));
}

}  // namespace

TEST(TitleDrivePlugin, Simple) {
  TestTitleByExpPlugin("econom", "yango_order_key##ru");
}

}  // namespace routestats::full::title
