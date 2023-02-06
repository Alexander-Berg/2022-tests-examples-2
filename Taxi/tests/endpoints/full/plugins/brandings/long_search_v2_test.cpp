#include <endpoints/full/core/input.hpp>
#include <endpoints/full/plugins/brandings/subplugins/long_search_v2.hpp>

#include <userver/utest/utest.hpp>

#include <tests/context_mock_test.hpp>
#include <tests/endpoints/common/service_level_mock_test.hpp>

namespace routestats::full::brandings {

namespace {
const std::string kDefaultLocale = "ru";

core::Experiments MockExperiments(bool client_enabled) {
  core::ExpMappedData experiments;
  {
    using ClientExp = experiments3::LongSearchV2;
    formats::json::ValueBuilder exp_value = formats::json::Type::kObject;
    exp_value["enabled"] = client_enabled;
    exp_value["tanker_keys"] = formats::json::Type::kArray;

    {
      formats::json::ValueBuilder tanker_key = formats::json::Type::kObject;
      tanker_key["key"] = "popup_title";
      tanker_key["tanker"] = formats::json::Type::kObject;
      tanker_key["tanker"]["key"] = "long_search_v2_popup_title";
      tanker_key["tanker"]["keyset"] = "client_messages";
      tanker_key["default"] = "default_1";
      exp_value["tanker_keys"].PushBack(std::move(tanker_key));
    }
    {
      formats::json::ValueBuilder tanker_key = formats::json::Type::kObject;
      tanker_key["key"] = "pin_hint_start_search";
      tanker_key["tanker"] = formats::json::Type::kObject;
      tanker_key["tanker"]["key"] = "pin_hint_start_search";
      tanker_key["tanker"]["keyset"] = "client_messages";
      tanker_key["default"] = "default_2";
      exp_value["tanker_keys"].PushBack(std::move(tanker_key));
    }
    {
      formats::json::ValueBuilder tanker_key = formats::json::Type::kObject;
      tanker_key["key"] = "pin_hint_radius_change";
      tanker_key["tanker"] = formats::json::Type::kObject;
      tanker_key["tanker"]["key"] = "pin_hint_radius_change";
      tanker_key["tanker"]["keyset"] = "client_messages";
      tanker_key["default"] = "default_3";
      exp_value["tanker_keys"].PushBack(std::move(tanker_key));
    }

    formats::json::ValueBuilder popup = formats::json::Type::kObject;
    popup["title_key"] = "popup_title";
    exp_value["popup"] = popup;
    exp_value["pin_hint_start_search"] = "pin_hint_start_search";
    exp_value["pin_hint_radius_change"] = "pin_hint_radius_change";
    exp_value["polling_interval_millis"] = 2000;
    exp_value["collapse_search_card_timeout_millis"] = 5000;
    experiments[ClientExp::kName] = {
        ClientExp::kName,
        formats::json::ValueBuilder{exp_value}.ExtractValue(),
        {}};
  }
  return {std::move(experiments)};
}

std::shared_ptr<const ::routestats::plugins::top_level::Context> CreateContext(
    bool client_enabled) {
  auto context = test::full::GetDefaultContext();
  context.user.auth_context.locale = kDefaultLocale;

  const auto exps = MockExperiments(client_enabled);
  context.get_experiments_mapped_data =
      [exps = std::move(exps)](
          const experiments3::models::KwargsBuilderWithConsumer& kwargs)
      -> core::ExpMappedData {
    kwargs.Build();
    return exps.mapped_data;
  };

  return test::full::MakeTopLevelContext(context);
}

core::ServiceLevel CreateServiceLevel(const std::string& class_) {
  auto service_level = test::MockDefaultServiceLevel(class_);
  return service_level;
}

std::string GetTextField(const std::string& text) {
  auto localize = [](const std::string& text) {
    return text + "##" + kDefaultLocale;
  };
  return localize(text);
}

service_level::LongSearchV2 CreateLongSearchV2() {
  service_level::LongSearchV2 long_search_v2;
  long_search_v2.collapse_search_card_timeout_millis = 5000;
  long_search_v2.polling_interval_millis = 2000;
  long_search_v2.pin_hint_start_search = GetTextField("pin_hint_start_search");
  long_search_v2.pin_hint_radius_change =
      GetTextField("pin_hint_radius_change");
  long_search_v2.popup = service_level::LongSearchV2::LongSearchV2Popup{};
  long_search_v2.popup->title = GetTextField("long_search_v2_popup_title");
  return long_search_v2;
}

service_level::TariffBranding CreateBranding() {
  service_level::TariffBranding branding;
  branding.type = "long_search_v2";
  branding.long_search_v2 = CreateLongSearchV2();
  return branding;
}

void AssertEq(const service_level::LongSearchV2& expected,
              const service_level::LongSearchV2& actual) {
  ASSERT_EQ(expected.collapse_search_card_timeout_millis,
            actual.collapse_search_card_timeout_millis);
  ASSERT_EQ(expected.pin_hint_start_search, actual.pin_hint_start_search);
  ASSERT_EQ(expected.pin_hint_radius_change, actual.pin_hint_radius_change);
  ASSERT_EQ(expected.polling_interval_millis, actual.polling_interval_millis);

  if (expected.popup.has_value()) {
    ASSERT_TRUE(actual.popup.has_value());
    ASSERT_EQ(expected.popup->title, actual.popup->title);
    ASSERT_EQ(expected.popup->description, actual.popup->description);
    ASSERT_EQ(expected.popup->button_title, actual.popup->button_title);
    ASSERT_EQ(expected.popup->search_card_subtitle,
              actual.popup->search_card_subtitle);
    ASSERT_EQ(expected.popup->search_card_title,
              actual.popup->search_card_title);
  } else {
    ASSERT_FALSE(actual.popup.has_value());
  }
}

void AssertEq(const service_level::TariffBranding& expected,
              const service_level::TariffBranding& actual) {
  ASSERT_EQ(expected.type, actual.type);
  if (expected.long_search_v2.has_value()) {
    ASSERT_TRUE(actual.long_search_v2.has_value());
    AssertEq(*expected.long_search_v2, *actual.long_search_v2);
  } else {
    ASSERT_FALSE(actual.long_search_v2.has_value());
  }
}

}  // namespace

class LongSearchV2DisabledExpParametrize
    : public ::testing::TestWithParam<std::tuple<bool>> {
 protected:
  LongSearchV2Plugin plugin;
};

TEST_P(LongSearchV2DisabledExpParametrize, BrandingsDisabledExp) {
  const auto [client_enabled] = GetParam();

  auto context = CreateContext(client_enabled);
  auto service_levels =
      std::vector<core::ServiceLevel>{CreateServiceLevel("uberx")};

  plugin.OnServiceLevelsReady(context, service_levels);
  if (client_enabled) {
    const auto& uberx_brandings = plugin.GetBrandings("uberx");
    ASSERT_EQ(uberx_brandings.size(), 1);

    const auto& branding = uberx_brandings.front();
    AssertEq(CreateBranding(), branding);
  } else {
    ASSERT_EQ(plugin.GetBrandings("uberx").size(), 0);
  }
  ASSERT_EQ(plugin.GetBrandings("uberx").size(), bool(client_enabled));
}

INSTANTIATE_TEST_SUITE_P(LongSearchV2Plugin, LongSearchV2DisabledExpParametrize,
                         ::testing::Values(std::make_tuple(false),
                                           std::make_tuple(true)));

}  // namespace routestats::full::brandings
