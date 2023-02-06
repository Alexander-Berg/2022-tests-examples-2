#include <endpoints/full/builders/input_builder.hpp>
#include <endpoints/full/core/input.hpp>
#include <endpoints/full/plugins/subtitle/subplugins/subtitle_by_payment.hpp>
#include <experiments3/new_summary_order_subtitle.hpp>

#include <clients/protocol-routestats/responses.hpp>
#include <l10n/errors.hpp>
#include <tests/context/translator_mock_test.hpp>
#include <tests/context_mock_test.hpp>
#include <tests/endpoints/common/service_level_mock_test.hpp>
#include <userver/utest/utest.hpp>

namespace routestats::plugins::subtitle {

namespace {

formats::json::Value MakeOrderSubtitleExp(
    bool enabled, const std::vector<std::string>& skip_categories) {
  using formats::json::ValueBuilder;

  ValueBuilder SubtitleExp{};
  SubtitleExp["enabled"] = enabled;

  SubtitleExp["skip_categories"] = ValueBuilder(formats::common::Type::kArray);
  for (const auto& class_ : skip_categories) {
    SubtitleExp["skip_categories"].PushBack(class_);
  }
  SubtitleExp["type"] = "payment";

  return SubtitleExp.ExtractValue();
}

full::ContextData PrepareContext(const bool exp_enabled, const bool key_missing,
                                 const bool no_payment) {
  full::ContextData context = test::full::GetDefaultContext();

  context.user.auth_context.locale = "ru";

  using SubtitleExp = experiments3::NewSummaryOrderSubtitle;
  core::ExpMappedData exp_mapped_data{};
  exp_mapped_data[SubtitleExp::kName] = {
      SubtitleExp::kName,
      MakeOrderSubtitleExp(exp_enabled, {"comfortplus"}),
      {}};
  context.experiments.uservices_routestats_exps = {std::move(exp_mapped_data)};
  full::RoutestatsRequest request;
  context.input = test::full::GetDefaultInput();
  if (!no_payment) {
    request.payment = handlers::RequestPayment{};
    request.payment->type = "card";
  }
  context.input = full::BuildRoutestatsInput(request, {}, {});

  context.rendering = test::full::GetDefaultRendering();
  if (key_missing) {
    test::TranslationHandler handler =
        []([[maybe_unused]] const core::Translation& translation,
           [[maybe_unused]] const std::string& locale)
        -> std::optional<std::string> { return std::nullopt; };
    context.rendering.translator =
        std::make_shared<test::TranslatorMock>(handler);
  }

  return context;
}

}  // namespace

void TestSubtitleByPaymentPlugin(
    const std::string& class_,
    const std::optional<std::string>& expected_subtitle,
    const bool exp_enabled = true, const bool key_missing = false,
    const bool no_payment = false) {
  SubtitleByPaymentPlugin plugin;
  const auto context = test::full::MakeTopLevelContext(
      PrepareContext(exp_enabled, key_missing, no_payment));
  const std::optional<std::string>& result_subtitle =
      plugin.GetSubtitle(class_, context);
  ASSERT_EQ(result_subtitle, expected_subtitle);
}

TEST(SubtitleByPaymentPlugin, valid) {
  TestSubtitleByPaymentPlugin("econom", "new_summary.order_subtitle.card##ru");
}

TEST(SubtitleByPaymentPlugin, disabled) {
  TestSubtitleByPaymentPlugin("econom", std::nullopt, false);
}

TEST(SubtitleByPaymentPlugin, key_missing) {
  TestSubtitleByPaymentPlugin("econom", std::nullopt, true, true);
}

TEST(SubtitleByPaymentPlugin, no_payment_type) {
  TestSubtitleByPaymentPlugin("econom", std::nullopt, true, false, true);
}

TEST(SubtitleByPaymentPlugin, skip_category) {
  TestSubtitleByPaymentPlugin("comfortplus", std::nullopt);
}

}  // namespace routestats::plugins::subtitle
