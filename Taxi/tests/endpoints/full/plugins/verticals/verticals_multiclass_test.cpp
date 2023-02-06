#include <endpoints/full/plugins/verticals/multiclass/multiclass_builder.hpp>

#include <fmt/format.h>
#include <tests/context/translator_mock_test.hpp>
#include <tests/context_mock_test.hpp>
#include <tests/endpoints/common/service_level_mock_test.hpp>
#include <userver/utest/utest.hpp>

namespace routestats::plugins::verticals {
bool operator==(const MulticlassTariff& l_tariff,
                const MulticlassTariff& r_tariff) {
  return (l_tariff.class_ == r_tariff.class_) &&
         (l_tariff.selected == r_tariff.selected);
}

std::ostream& operator<<(std::ostream& os, const MulticlassTariff& tariff) {
  return os << tariff.class_ << ", " << (tariff.selected ? "true" : "false");
}

bool operator==(const MulticlassEstimatedWaiting& l_eta,
                const MulticlassEstimatedWaiting& r_eta) {
  return (l_eta.seconds == r_eta.seconds) && (l_eta.message == r_eta.message);
}

std::ostream& operator<<(std::ostream& os,
                         const MulticlassEstimatedWaiting& eta) {
  return os << eta.seconds << ", " << eta.message;
}

bool operator==(const TariffUnavailable& l_unavailable,
                const TariffUnavailable& r_unavailable) {
  return (l_unavailable.code == r_unavailable.code) &&
         (l_unavailable.message == r_unavailable.message);
}

namespace {
struct TestMulticlass : public experiments3::verticals_selector::Multiclass {
  TestMulticlass(const std::vector<std::string>& tariffs_val) {
    tariffs = tariffs_val;
    position = 2;
    default_enabled = true;
  }
};

struct TestGroupVertical
    : public experiments3::verticals_selector::GroupVertical {
  TestGroupVertical(const std::string& id_val,
                    const std::vector<std::string>& tariffs_val) {
    type = experiments3::verticals_selector::GroupVerticalType::kGroup;
    title = "test_title";
    id = id_val;
    multiclass = TestMulticlass(tariffs_val);
  }
};

struct TestVerticalCoreInfo : public GroupVerticalCoreInfo {
  TestVerticalCoreInfo(const std::string& id_val,
                       const std::vector<std::string>& tariffs_val) {
    id = id_val;
    for (const auto& tariff : tariffs_val) {
      Tariff vertical_tariff{tariff};
      tariffs.emplace_back(vertical_tariff);
    }
  }
};

experiments3::VerticalsSelector::Value PrepareVerticalsMulticlassSettings() {
  experiments3::VerticalsSelector::Value multiclass_settings;

  TestGroupVertical delivery_vertical("delivery", {"cargo", "express"});
  multiclass_settings.verticals.emplace_back(delivery_vertical);

  TestGroupVertical ultima_vertical("ultima", {"business", "maybach", "vip"});
  multiclass_settings.verticals.emplace_back(ultima_vertical);

  multiclass_settings.rest_tariffs.id = "rest_tariffs";

  return multiclass_settings;
}

const core::CategoriesVisibilityAttributes& DEFAULT_VISIBILITY_ATTRIBUTES = {
    {"express", core::VisibilityAttributes{true, false}},
    {"cargo", core::VisibilityAttributes{true, false}},
    {"courier", core::VisibilityAttributes{true, false}},
    {"vip", core::VisibilityAttributes{true, false}},
    {"business", core::VisibilityAttributes{true, false}},
    {"maybach", core::VisibilityAttributes{true, false}},
    {"econom", core::VisibilityAttributes{true, false}},
};

full::ContextData PrepareCtxData(
    const core::CategoriesVisibilityAttributes& visibility_attributes,
    const bool key_missing,
    const handlers::RoutestatsRequestMulticlassoptions& multiclass_options,
    bool is_preorder = false, bool is_complement_payment = false) {
  full::ContextData ctx = test::full::GetDefaultContext();
  ctx.user.auth_context.locale = "ru";
  ctx.rendering = test::full::GetDefaultRendering();

  test::TranslationHandler handler =
      [key_missing](const core::Translation& translation,
                    const std::string& locale) -> std::optional<std::string> {
    if (key_missing) {
      return std::nullopt;
    }
    if (translation->main_key.key.find("price") != std::string::npos) {
      return translation->main_key.key + "##" + locale + "##" +
             translation->main_key.args["price"];
    }
    return translation->main_key.key + "##" + locale;
  };
  ctx.rendering.translator = std::make_shared<test::TranslatorMock>(handler);

  ctx.categories_visibility = core::CategoriesVisibility{};
  ctx.categories_visibility.attributes = visibility_attributes;
  ctx.input.original_request.multiclass_options = multiclass_options;

  if (is_preorder) {
    ctx.input.original_request.preorder_request_id = "test_id";
  }

  if (is_complement_payment) {
    handlers::RequestPayment payment;
    payment.complements = {
        handlers::RequestPaymentComplement{"personal_wallet", "w/123"}};
    ctx.input.original_request.payment = payment;
  }

  return ctx;
}

std::shared_ptr<const top_level::Context> GetContext(
    const core::CategoriesVisibilityAttributes& attributes =
        DEFAULT_VISIBILITY_ATTRIBUTES,
    bool key_missing = false,
    const handlers::RoutestatsRequestMulticlassoptions& multiclass_options = {},
    bool is_preorder = false, bool is_complement_payment = false) {
  return test::full::MakeTopLevelContext(
      PrepareCtxData(attributes, key_missing, multiclass_options, is_preorder,
                     is_complement_payment));
}

std::vector<GroupVerticalCoreInfo> BuildCoreInfo() {
  std::vector<GroupVerticalCoreInfo> core_info;
  TestVerticalCoreInfo delivery_info("delivery", {"cargo", "express"});
  core_info.emplace_back(delivery_info);

  TestVerticalCoreInfo ultima_info("ultima", {"business", "maybach", "vip"});
  core_info.emplace_back(ultima_info);

  return core_info;
}

void CheckResultMulticlass(
    const MulticlassInfo& multiclass,
    const std::vector<MulticlassTariff>& expected_tariffs,
    const std::optional<std::size_t>& expected_position,
    const bool expected_order_button_enabled,
    const MulticlassEstimatedWaiting& expected_eta, const int expected_price,
    bool show_max_price = false,
    std::optional<std::string> expected_unavailable_code = std::nullopt) {
  ASSERT_EQ(multiclass.name, "routestats.multiclass.name##ru");
  ASSERT_EQ(multiclass.selection_rules.min_selected_count.value, 2);
  ASSERT_EQ(multiclass.selection_rules.min_selected_count.text,
            "multiclass.min_selected_count.text##ru");
  ASSERT_EQ(multiclass.details.description.title,
            "routestats.multiclass.details.description.title##ru");
  ASSERT_EQ(multiclass.details.description.subtitle,
            "routestats.multiclass.details.description.subtitle##ru");
  ASSERT_EQ(multiclass.details.order_button.text,
            "routestats.multiclass.details.order_button.text##ru");
  ASSERT_EQ(multiclass.details.search_screen.title,
            "routestats.multiclass.search_screen.title##ru");
  ASSERT_EQ(multiclass.details.search_screen.subtitle,
            "routestats.multiclass.search_screen.subtitle##ru");
  ASSERT_EQ(multiclass.position, expected_position);
  ASSERT_EQ(multiclass.details.order_button.enabled.value_or(false),
            expected_order_button_enabled);
  ASSERT_EQ(multiclass.tariffs, expected_tariffs);
  if (multiclass.estimated_waiting) {
    ASSERT_EQ(*multiclass.estimated_waiting, expected_eta);
  }
  if (show_max_price) {
    const auto& expected_price_string = fmt::format(
        "routestats.multiclass.details.fixed_price##ru##{},0 $SIGN$$CURRENCY$",
        expected_price);
    ASSERT_EQ(multiclass.details.price, expected_price_string);
  } else {
    const auto& expected_price_string = fmt::format(
        "routestats.multiclass.details.not_fixed_price##ru##{},0 "
        "$SIGN$$CURRENCY$",
        expected_price);
    ASSERT_EQ(multiclass.details.price, expected_price_string);
  }
  if (expected_unavailable_code) {
    const auto& code = *expected_unavailable_code;
    ASSERT_EQ(multiclass.tariff_unavailable->code, code);
    ASSERT_EQ(multiclass.tariff_unavailable->message,
              "routestats.tariff_unavailable." + code + "##ru");
  }
}

core::ServiceLevel MockServiceLevel(std::string class_, core::Decimal price,
                                    core::EstimatedWaiting eta,
                                    bool is_fixed_price = true) {
  auto result = test::MockDefaultServiceLevel(class_);
  result.final_price = std::move(price);
  result.eta = std::move(eta);
  result.is_fixed_price = is_fixed_price;
  return result;
}

const auto default_service_levels = std::vector<core::ServiceLevel>{
    MockServiceLevel("maybach", core::Decimal{1500},
                     core::EstimatedWaiting{120, "2 минуты"}),
    MockServiceLevel("business", core::Decimal{800},
                     core::EstimatedWaiting{180, "3 минуты"}),
    MockServiceLevel("express", core::Decimal{200},
                     core::EstimatedWaiting{300, "5 минут"}),
    MockServiceLevel("cargo", core::Decimal{400},
                     core::EstimatedWaiting{180, "3 минуты"}),
    MockServiceLevel("econom", core::Decimal{100},
                     core::EstimatedWaiting{60, "1 минута"}),
    MockServiceLevel("vip", core::Decimal{1000},
                     core::EstimatedWaiting{240, "4 минуты"}),
};

}  // namespace

TEST(TestVerticalsPluginVerticalsMulticlass, HappyPath) {
  const auto selector_settings = PrepareVerticalsMulticlassSettings();
  const auto ctx = GetContext();
  const auto core_info = BuildCoreInfo();
  const auto multiclasses =
      BuildMulticlasses(ctx->Get<VerticalsMulticlassContext>(),
                        selector_settings, core_info, default_service_levels);

  ASSERT_EQ(multiclasses.size(), 2);
  CheckResultMulticlass(
      multiclasses.at(0),
      {MulticlassTariff{"cargo", false}, MulticlassTariff{"express", false}},
      2 /*position*/, false /*order_button_enabled*/,
      MulticlassEstimatedWaiting{"3 минуты", 180}, 200);
  CheckResultMulticlass(
      multiclasses.at(1),
      {MulticlassTariff{"business", false}, MulticlassTariff{"maybach", false},
       MulticlassTariff{"vip", false}},
      2 /*position*/, false /*order_button_enabled*/,
      MulticlassEstimatedWaiting{"2 минуты", 120}, 800);
}

TEST(TestVerticalsPluginVerticalsMulticlass, NoTranslations) {
  const auto selector_settings = PrepareVerticalsMulticlassSettings();
  const auto ctx =
      GetContext(DEFAULT_VISIBILITY_ATTRIBUTES, true /*key_missing*/);
  const auto core_info = BuildCoreInfo();
  const auto multiclasses =
      BuildMulticlasses(ctx->Get<VerticalsMulticlassContext>(),
                        selector_settings, core_info, default_service_levels);

  ASSERT_TRUE(multiclasses.empty());
}

TEST(TestVerticalsPluginVerticalsMulticlass, NotAllVerticalsInCoreInfo) {
  const auto selector_settings = PrepareVerticalsMulticlassSettings();
  const auto ctx = GetContext();

  std::vector<GroupVerticalCoreInfo> core_info;
  TestVerticalCoreInfo ultima_info("ultima", {"business", "maybach", "vip"});
  core_info.emplace_back(ultima_info);

  const auto multiclasses =
      BuildMulticlasses(ctx->Get<VerticalsMulticlassContext>(),
                        selector_settings, core_info, default_service_levels);

  ASSERT_EQ(multiclasses.size(), 1);
  CheckResultMulticlass(
      multiclasses.at(0),
      {MulticlassTariff{"business", false}, MulticlassTariff{"maybach", false},
       MulticlassTariff{"vip", false}},
      2 /*position*/, false /*order_button_enabled*/,
      MulticlassEstimatedWaiting{"2 минуты", 120}, 800);
}

TEST(TestVerticalsPluginVerticalsMulticlass, NotAllTariffsInVerticals) {
  const auto selector_settings = PrepareVerticalsMulticlassSettings();
  const auto ctx = GetContext();

  std::vector<GroupVerticalCoreInfo> core_info;

  TestVerticalCoreInfo delivery_info("delivery", {"express"});
  core_info.emplace_back(delivery_info);

  TestVerticalCoreInfo ultima_info("ultima", {"business"});
  core_info.emplace_back(ultima_info);

  const auto multiclasses =
      BuildMulticlasses(ctx->Get<VerticalsMulticlassContext>(),
                        selector_settings, core_info, default_service_levels);

  ASSERT_EQ(multiclasses.size(), 2);
  CheckResultMulticlass(multiclasses.at(0),
                        {MulticlassTariff{"express", false}}, 2 /*position*/,
                        false /*order_button_enabled*/,
                        MulticlassEstimatedWaiting{"5 минут", 300}, 200);
  CheckResultMulticlass(multiclasses.at(1),
                        {MulticlassTariff{"business", false}}, 2 /*position*/,
                        false /*order_button_enabled*/,
                        MulticlassEstimatedWaiting{"3 минуты", 180}, 800);
}

TEST(TestVerticalsPluginVerticalsMulticlass, HasSelectedClasses) {
  const auto selector_settings = PrepareVerticalsMulticlassSettings();
  const auto core_info = BuildCoreInfo();

  handlers::RoutestatsRequestMulticlassoptions multiclass_options;
  multiclass_options.verticals = {
      handlers::VerticalsMulticlassOptions{"delivery", {"express"}},
      handlers::VerticalsMulticlassOptions{"ultima", {"business", "vip"}}};

  const auto ctx = GetContext(DEFAULT_VISIBILITY_ATTRIBUTES,
                              false /*key_missing*/, multiclass_options);

  const auto multiclasses =
      BuildMulticlasses(ctx->Get<VerticalsMulticlassContext>(),
                        selector_settings, core_info, default_service_levels);

  ASSERT_EQ(multiclasses.size(), 2);
  CheckResultMulticlass(
      multiclasses.at(0),
      {MulticlassTariff{"cargo", false}, MulticlassTariff{"express", true}},
      2 /*position*/, false /*order_button_enabled*/,
      MulticlassEstimatedWaiting{"5 минут", 300}, 200, true /*show_max_price*/);
  CheckResultMulticlass(
      multiclasses.at(1),
      {MulticlassTariff{"business", true}, MulticlassTariff{"maybach", false},
       MulticlassTariff{"vip", true}},
      2 /*position*/, true /*order_button_enabled*/,
      MulticlassEstimatedWaiting{"3 минуты", 180}, 1000,
      true /*show_max_price*/);
}

TEST(TestVerticalsPluginVerticalsMulticlass, HasNoSelectedClasses) {
  const auto selector_settings = PrepareVerticalsMulticlassSettings();
  const auto core_info = BuildCoreInfo();

  const auto ctx =
      GetContext(DEFAULT_VISIBILITY_ATTRIBUTES, false /*key_missing*/, {});

  const auto multiclasses =
      BuildMulticlasses(ctx->Get<VerticalsMulticlassContext>(),
                        selector_settings, core_info, default_service_levels);

  ASSERT_EQ(multiclasses.size(), 2);
  CheckResultMulticlass(
      multiclasses.at(0),
      {MulticlassTariff{"cargo", false}, MulticlassTariff{"express", false}},
      2 /*position*/, false /*order_button_enabled*/,
      MulticlassEstimatedWaiting{"3 минуты", 180}, 200,
      false /*show_max_price*/);
  CheckResultMulticlass(
      multiclasses.at(1),
      {MulticlassTariff{"business", false}, MulticlassTariff{"maybach", false},
       MulticlassTariff{"vip", false}},
      2 /*position*/, false /*order_button_enabled*/,
      MulticlassEstimatedWaiting{"2 минуты", 120}, 800,
      false /*show_max_price*/);
}

TEST(TestVerticalsPluginVerticalsMulticlass,
     TariffHiddenMixFixedAndNonFixedPrice) {
  const auto selector_settings = PrepareVerticalsMulticlassSettings();
  const auto ctx = GetContext();
  const auto core_info = BuildCoreInfo();

  const auto service_levels = std::vector<core::ServiceLevel>{
      MockServiceLevel("maybach", core::Decimal{1500},
                       core::EstimatedWaiting{120, "2 минуты"}),
      MockServiceLevel("business", core::Decimal{800},
                       core::EstimatedWaiting{180, "3 минуты"}),
      MockServiceLevel("express", core::Decimal{200},
                       core::EstimatedWaiting{300, "5 минут"},
                       false /*is_fixed_price*/),
      MockServiceLevel("cargo", core::Decimal{400},
                       core::EstimatedWaiting{180, "3 минуты"}),
      MockServiceLevel("econom", core::Decimal{100},
                       core::EstimatedWaiting{60, "1 минута"}),
      MockServiceLevel("vip", core::Decimal{1000},
                       core::EstimatedWaiting{240, "4 минуты"},
                       false /*is_fixed_price*/),
  };

  const auto multiclasses =
      BuildMulticlasses(ctx->Get<VerticalsMulticlassContext>(),
                        selector_settings, core_info, service_levels);

  ASSERT_EQ(multiclasses.size(), 0);
}

TEST(TestVerticalsPluginVerticalsMulticlass, TariffUnavailable_Preorder) {
  const auto selector_settings = PrepareVerticalsMulticlassSettings();
  const auto ctx =
      GetContext(DEFAULT_VISIBILITY_ATTRIBUTES, false /*key_missing*/,
                 {} /*multiclass_options*/, true /*is_preorder*/);
  const auto core_info = BuildCoreInfo();
  const auto multiclasses =
      BuildMulticlasses(ctx->Get<VerticalsMulticlassContext>(),
                        selector_settings, core_info, default_service_levels);

  ASSERT_EQ(multiclasses.size(), 2);
  CheckResultMulticlass(
      multiclasses.at(0),
      {MulticlassTariff{"cargo", false}, MulticlassTariff{"express", false}},
      2 /*position*/, false /*order_button_enabled*/,
      MulticlassEstimatedWaiting{"3 минуты", 180}, 200,
      false /*show_max_price*/, "multiclass_preorder_unavailable");
  CheckResultMulticlass(
      multiclasses.at(1),
      {MulticlassTariff{"business", false}, MulticlassTariff{"maybach", false},
       MulticlassTariff{"vip", false}},
      2 /*position*/, false /*order_button_enabled*/,
      MulticlassEstimatedWaiting{"2 минуты", 120}, 800,
      false /*show_max_price*/, "multiclass_preorder_unavailable");
}

TEST(TestVerticalsPluginVerticalsMulticlass,
     TariffUnavailable_AllTariffsUnavailable) {
  handlers::RoutestatsRequestMulticlassoptions multiclass_options;
  multiclass_options.verticals = {
      handlers::VerticalsMulticlassOptions{"delivery", {"express"}},
      handlers::VerticalsMulticlassOptions{"ultima", {"maybach"}}};

  const auto ctx =
      GetContext(DEFAULT_VISIBILITY_ATTRIBUTES, false /*key_missing*/,
                 multiclass_options, false /*is_preorder*/);
  const auto core_info = BuildCoreInfo();

  const auto selector_settings = PrepareVerticalsMulticlassSettings();

  auto unavailable_service_levels = std::vector<core::ServiceLevel>{
      test::MockDefaultServiceLevel("maybach"),
      test::MockDefaultServiceLevel("express"),
  };

  routestats::core::TariffUnavailable ta{"no_free_cars_nearby", "unavailable"};
  unavailable_service_levels[0].tariff_unavailable = ta;
  unavailable_service_levels[1].tariff_unavailable = ta;
  const auto multiclasses = BuildMulticlasses(
      ctx->Get<VerticalsMulticlassContext>(), selector_settings, core_info,
      unavailable_service_levels);

  ASSERT_EQ(multiclasses.size(), 2);

  for (const auto& mc : multiclasses) {
    ASSERT_EQ(mc.tariff_unavailable->code, "multiclass_unavailable");
  }
}

TEST(TestVerticalsPluginVerticalsMulticlass,
     TariffUnavailable_UnsupportedPaymentMethod) {
  handlers::RoutestatsRequestMulticlassoptions multiclass_options;
  multiclass_options.verticals = {
      handlers::VerticalsMulticlassOptions{"delivery", {"express"}},
      handlers::VerticalsMulticlassOptions{"ultima", {"maybach"}}};

  const auto ctx = GetContext(
      DEFAULT_VISIBILITY_ATTRIBUTES, false /*key_missing*/, multiclass_options,
      false /*is_preorder*/, true /*is_complement_payment*/);
  const auto core_info = BuildCoreInfo();

  const auto selector_settings = PrepareVerticalsMulticlassSettings();
  const auto multiclasses =
      BuildMulticlasses(ctx->Get<VerticalsMulticlassContext>(),
                        selector_settings, core_info, default_service_levels);

  ASSERT_EQ(multiclasses.size(), 2);

  for (const auto& mc : multiclasses) {
    ASSERT_EQ(mc.tariff_unavailable->code, "unsupported_payment_method");
  }
}

}  // namespace routestats::plugins::verticals
