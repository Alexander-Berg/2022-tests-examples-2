#include "context_mock_test.hpp"
#include "clients/routing/test/router_selector_mock.hpp"
#include "context/attributed_text_maker_mock_test.hpp"
#include "context/eta_formatter_mock_test.hpp"
#include "context/image_getter_mock_test.hpp"
#include "context/price_formatter_mock_test.hpp"
#include "context/taxi_config_mock_test.hpp"
#include "context/translator_mock_test.hpp"
#include "context/wallets_mock_test.hpp"
#include "tests/context/geobase_mock.hpp"

#include <gtest/gtest.h>

namespace routestats::test {

core::WalletsPtr GetDefaultUserWallets() {
  return std::make_shared<WalletsMock>(
      [](const std::string&) { return std::nullopt; });
}

core::Configs3 GetDefaultConfigs3() { return core::Configs3{}; }

core::TaxiConfigsPtr GetDefaultTaxiConfigs() {
  return std::make_shared<TaxiConfigsMock>();
}

const core::Experiments& GetDefaultExperiments() {
  static const core::Experiments kDefault{};
  return kDefault;
}

core::Zone GetDefaultZone() { return core::Zone{}; }

const clients::routing::RouterSelector* GetDefaultRouterSelector() {
  static clients::routing::RouterSelectorMock rs_mock;
  return &rs_mock;
}

const std::shared_ptr<GeobaseWrapperMock> GetDefaultLookup() {
  return std::make_shared<GeobaseWrapperMock>();
}

namespace full {

routestats::full::ContextData GetDefaultContext() {
  routestats::full::ContextData context;

  context.input = GetDefaultInput();
  context.user = GetDefaultUser();
  context.user_wallets = GetDefaultUserWallets();
  context.taxi_configs = GetDefaultTaxiConfigs();
  context.experiments = {GetDefaultExperiments(), GetDefaultConfigs3()};
  context.zone = GetDefaultZone();
  context.rendering = GetDefaultRendering();
  context.router_selector = GetDefaultRouterSelector();
  context.geobase = GetDefaultLookup();

  return context;
}

std::shared_ptr<const plugins::top_level::Context> MakeTopLevelContext(
    routestats::full::ContextData context) {
  return std::make_shared<const plugins::top_level::Context>(
      std::move(context));
}

routestats::full::RoutestatsInput GetDefaultInput() {
  return routestats::full::RoutestatsInput{};
}

routestats::full::User GetDefaultUser() { return routestats::full::User{}; }

routestats::full::RenderingContext GetDefaultRendering() {
  return routestats::full::RenderingContext{
      std::make_shared<TranslatorMock>(
          [](const Translation& translation, const std::string& locale) {
            return translation->main_key.key + "##" + locale;
          }),
      std::make_shared<PriceFormatterMock>(),
      std::make_shared<AttributedTextMakerMock>(
          [](const Translation& translation, const std::string& locale) {
            extended_template::ATTextProperty at;
            at.text = translation->main_key.keyset + "##" +
                      translation->main_key.key + "##" + locale;
            return extended_template::AttributedText{{at}};
          }),
      std::make_shared<EtaFormatterMock>(),
      std::make_shared<ImageGetterMock>([](const std::string& tag,
                                           const std::optional<int>,
                                           const std::optional<std::string>&) {
        return core::Image{tag, 0, tag, tag, tag};
      })};
}

}  // namespace full

namespace lightweight {

routestats::lightweight::ContextData GetDefaultContext() {
  routestats::lightweight::ContextData context;

  context.experiments = {GetDefaultExperiments(), GetDefaultConfigs3()};
  context.zone = GetDefaultZone();

  return context;
}

std::shared_ptr<const routestats::lightweight::Context> MakeTopLevelContext(
    routestats::lightweight::ContextData context) {
  return std::make_shared<const routestats::lightweight::Context>(
      std::move(context));
}

}  // namespace lightweight

}  // namespace routestats::test
