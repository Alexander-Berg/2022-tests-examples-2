#include <gtest/gtest.h>

#include <eats-shared/defs/definitions.hpp>

#include <sources/catalog/catalog_data_source.hpp>
#include <sources/data_source.hpp>
#include "tab_bar.hpp"

namespace eats_layout_constructor::static_widgets::tab_bar {

namespace {

namespace config = ::experiments3::eats_layout_constructor_tab_bar;
namespace predicate = ::clients::catalog::libraries::eats_catalog_predicate;
namespace eats_shared = handlers::libraries::eats_shared;
namespace source = eats_layout_constructor::sources;

sources::CatalogDataSource::Params GetCatalogParams(
    const sources::DataSourceParams& params) {
  return sources::GetSourceParams<sources::CatalogDataSource>(params);
}

config::ViewAction MakeViewAction(const std::string& view_slug) {
  config::ViewAction action{};
  auto& view = action.view.emplace();
  view.type = config::ViewType::kTab;
  view.slug = view_slug;
  return action;
}

TabBar::Config MakeConfig() {
  TabBar::Config config{};
  config.enabled = true;
  auto& rest_tab = config.tabs.emplace_back();
  rest_tab.id = "rest";
  rest_tab.icon = "rest/icon";
  rest_tab.name = "ресты";
  rest_tab.action = MakeViewAction("rest");
  rest_tab.business.push_back(eats_shared::Business::kRestaurant);

  auto& shops_tab = config.tabs.emplace_back();
  shops_tab.id = "shops";
  shops_tab.icon = "shops/icon";
  shops_tab.name = "магазы";
  shops_tab.action = MakeViewAction("shops");
  shops_tab.business.push_back(eats_shared::Business::kShop);

  return config;
}

sources::DataSourceResponses GetDataSourceResponse(
    const std::unordered_map<std::string, int>& block_counts) {
  using Catalog = eats_layout_constructor::sources::CatalogDataSource;
  auto catalog_response =
      std::make_shared<Catalog::Response>(Catalog::Response{});

  for (const auto& [block_id, count] : block_counts) {
    sources::catalog::Block::Stats stats{};
    stats.places_count = count;
    catalog_response->blocks[block_id].stats = stats;
  }

  eats_layout_constructor::sources::DataSourceResponses response;
  response[Catalog::kName] = catalog_response;
  return response;
}

sources::DataSourceResponses GetDefaultDataSourceResponse() {
  std::unordered_map<std::string, int> block_counts{
      {"tab_bar_rest", 1},
      {"tab_bar_shops", 1},
  };
  return GetDataSourceResponse(block_counts);
}

}  // namespace

TEST(TabBar, Generic) {
  // Общий случай, получаем конфиг, рисуем таб бар
  eats_layout_constructor::models::RequestParams params{};
  experiments3::models::CacheManagerPtr experiments3{};
  const auto config = MakeConfig();
  TabBar tab_bar{experiments3, params, TabBar::Config{config}, std::nullopt};

  formats::json::ValueBuilder layout_builder{formats::common::Type::kObject};
  tab_bar.FilterSourceResponse(GetDefaultDataSourceResponse());
  tab_bar.UpdateLayout(layout_builder);
  auto layout = layout_builder.ExtractValue();

  const static std::string kDataSection = "tab_bar";

  auto widget = layout["data"][kDataSection];
  ASSERT_TRUE(widget.IsObject());

  ASSERT_EQ(widget["id"].As<std::string>(), kDataSection);
  ASSERT_EQ(widget["template_name"].As<std::string>(), kDataSection);

  auto payload = widget["payload"];
  ASSERT_TRUE(payload.IsObject());

  ASSERT_EQ(payload["current_id"].As<std::string>(), config.tabs.front().id);

  ASSERT_TRUE(payload["list"].IsArray());
  ASSERT_EQ(payload["list"].GetSize(), config.tabs.size());

  size_t idx = 0;
  for (const auto& item : payload["list"]) {
    const auto& config_tab = config.tabs[idx];

    ASSERT_EQ(item["id"].As<std::string>(), config_tab.id);
    ASSERT_EQ(item["icon"].As<std::string>(), config_tab.icon);
    ASSERT_EQ(item["name"].As<std::string>(), config_tab.name);
    ASSERT_EQ(item["action_type"].As<std::string>(), "view");

    ASSERT_EQ(item["action_payload"]["view"]["type"].As<std::string>(), "tab");
    const auto& config_action =
        std::get<config::ViewAction>(config_tab.action.AsVariant());
    ASSERT_EQ(item["action_payload"]["view"]["slug"].As<std::string>(),
              config_action.view.value().slug);

    idx++;
  }
}

TEST(TabBar, NulloptConfig) {
  // Проверяем, что если в конфиге == nullopt
  eats_layout_constructor::models::RequestParams params{};
  experiments3::models::CacheManagerPtr experiments3{};
  TabBar tab_bar{experiments3, params, std::nullopt, std::nullopt};

  formats::json::ValueBuilder layout_builder{formats::common::Type::kObject};
  tab_bar.FilterSourceResponse(GetDefaultDataSourceResponse());
  tab_bar.UpdateLayout(layout_builder);
  auto layout = layout_builder.ExtractValue();

  ASSERT_TRUE(layout.IsEmpty());
}

TEST(TabBar, Disabled) {
  // Проверяем, что если в конфиге
  // enabled = false, то виджет не отрисуется

  auto config = MakeConfig();
  config.enabled = false;
  eats_layout_constructor::models::RequestParams params{};
  experiments3::models::CacheManagerPtr experiments3{};
  TabBar tab_bar{experiments3, params, TabBar::Config{config}, std::nullopt};

  formats::json::ValueBuilder layout_builder{formats::common::Type::kObject};
  tab_bar.FilterSourceResponse(GetDefaultDataSourceResponse());
  tab_bar.UpdateLayout(layout_builder);
  auto layout = layout_builder.ExtractValue();

  ASSERT_TRUE(layout.IsEmpty());
}

TEST(TabBar, DafultTab) {
  // Проверяем, что если в конфиге
  // задан default_tab, то он будет в current

  auto config = MakeConfig();
  const static std::string kDefaultTab = "SHOPS";
  config.default_tab = kDefaultTab;
  config.tabs.back().id = kDefaultTab;

  std::unordered_map<std::string, int> block_counts{
      {"tab_bar_rest", 1},
      {fmt::format("tab_bar_{}", kDefaultTab), 1},
  };
  eats_layout_constructor::models::RequestParams params{};
  experiments3::models::CacheManagerPtr experiments3{};
  TabBar tab_bar{experiments3, params, TabBar::Config{config}, std::nullopt};

  formats::json::ValueBuilder layout_builder{formats::common::Type::kObject};
  tab_bar.FilterSourceResponse(GetDataSourceResponse(block_counts));
  tab_bar.UpdateLayout(layout_builder);
  auto layout = layout_builder.ExtractValue();

  auto payload = layout["data"]["tab_bar"]["payload"];
  ASSERT_TRUE(payload.IsObject());
  ASSERT_EQ(payload["current_id"].As<std::string>(), kDefaultTab);
}

TEST(TabBar, DafultTabInvalid) {
  // Проверяем, что если в конфиге
  // задан default_tab, но такого слага
  // нет в списке, как current возьмется первый таб

  auto config = MakeConfig();
  const static std::string kDefaultTab = "SHOPS";
  config.default_tab = kDefaultTab;
  eats_layout_constructor::models::RequestParams params{};
  experiments3::models::CacheManagerPtr experiments3{};
  TabBar tab_bar{experiments3, params, TabBar::Config{config}, std::nullopt};

  formats::json::ValueBuilder layout_builder{formats::common::Type::kObject};
  tab_bar.FilterSourceResponse(GetDefaultDataSourceResponse());
  tab_bar.UpdateLayout(layout_builder);
  const auto layout = layout_builder.ExtractValue();

  const auto payload = layout["data"]["tab_bar"]["payload"];
  ASSERT_TRUE(payload.IsObject());
  const auto current = payload["current_id"].As<std::string>();
  ASSERT_NE(current, kDefaultTab);
  ASSERT_EQ(current, config.tabs.front().id);
}

TEST(TabBar, ViewTab) {
  // Проверяем, что если
  // view.type = tab и слаг таба есть конфиге
  // он будет помечен как current

  models::View view{};
  view.type = models::ViewType::kTab;
  view.slug = models::ViewSlug{"shops"};
  eats_layout_constructor::models::RequestParams params{};
  experiments3::models::CacheManagerPtr experiments3{};
  TabBar tab_bar{experiments3, params, MakeConfig(), view};

  formats::json::ValueBuilder layout_builder{formats::common::Type::kObject};
  tab_bar.FilterSourceResponse(GetDefaultDataSourceResponse());
  tab_bar.UpdateLayout(layout_builder);
  const auto layout = layout_builder.ExtractValue();

  const auto payload = layout["data"]["tab_bar"]["payload"];
  const auto current = payload["current_id"].As<std::string>();
  ASSERT_EQ(current, view.slug.GetUnderlying());
}

TEST(TabBar, ViewTabInvalid) {
  // Проверяем, что если
  // view.type = tab и слага таба нет в конфиге
  // он не будет в current

  models::View view;
  view.type = models::ViewType::kTab;
  view.slug = models::ViewSlug{"SHOPS"};
  eats_layout_constructor::models::RequestParams params{};
  experiments3::models::CacheManagerPtr experiments3{};
  TabBar tab_bar{experiments3, params, MakeConfig(), view};

  formats::json::ValueBuilder layout_builder{formats::common::Type::kObject};
  tab_bar.FilterSourceResponse(GetDefaultDataSourceResponse());
  tab_bar.UpdateLayout(layout_builder);
  const auto layout = layout_builder.ExtractValue();

  const auto payload = layout["data"]["tab_bar"]["payload"];
  const auto current = payload["current_id"].As<std::string>();
  ASSERT_NE(current, view.slug.GetUnderlying());
}

TEST(TabBar, ViewTabNonTabType) {
  // Проверяем, что если
  // view.type != tab и даже если слаг есть в
  // списке, таб не будет помечен как current

  models::View view{};
  view.type = models::ViewType::kCollection;
  view.slug = models::ViewSlug{"shops"};
  eats_layout_constructor::models::RequestParams params{};
  experiments3::models::CacheManagerPtr experiments3{};
  TabBar tab_bar{experiments3, params, MakeConfig(), view};

  formats::json::ValueBuilder layout_builder{formats::common::Type::kObject};
  tab_bar.FilterSourceResponse(GetDefaultDataSourceResponse());
  tab_bar.UpdateLayout(layout_builder);
  const auto layout = layout_builder.ExtractValue();

  const auto payload = layout["data"]["tab_bar"]["payload"];
  const auto current = payload["current_id"].As<std::string>();
  ASSERT_NE(current, view.slug.GetUnderlying());
}

TEST(TabBar, RequestCatalog) {
  // Проверяем, что виджет запрашивает
  // у каталога блоки с no_data для проверки доступности
  // табов

  auto config = MakeConfig();
  auto& main_tab = config.tabs.emplace_back();
  main_tab.id = "main";
  main_tab.icon = "main/icon";
  main_tab.name = "главная";
  main_tab.action = config::ViewAction{};
  main_tab.business = {};

  const static std::string kRestBlockId = "tab_bar_rest";
  const static std::string kShopsBlockId = "tab_bar_shops";

  std::unordered_map<std::string, int> block_counts{
      {kRestBlockId, 1},
      // Отдаем 0 магазинов и ожидаем, что вернуться только табы главной и
      // ресторанов
      {kShopsBlockId, 0},
  };
  eats_layout_constructor::models::RequestParams params{};
  experiments3::models::CacheManagerPtr experiments3{};
  TabBar tab_bar{experiments3, params, config, std::nullopt};

  sources::DataSourceParams source_params;
  tab_bar.FillSourceRequestParams(source_params);
  auto catalog_params = GetCatalogParams(source_params);

  ASSERT_EQ(catalog_params.blocks.size(), block_counts.size());
  // Проверяем, что для таба рестов запросили предикат
  // с бизнесом ресторанов, а для таба магазинов предикат
  // с юизнесом магазинов
  std::vector<std::pair<std::string, std::string>> block_params{
      {kRestBlockId, "restaurant"}, {kShopsBlockId, "shop"}};
  for (const auto& [block_id, business] : block_params) {
    ASSERT_TRUE(catalog_params.blocks.count(block_id) == 1)
        << "failed to find block: " << block_id;

    const auto& block = catalog_params.blocks.at(block_id);
    ASSERT_TRUE(block.no_data);
    ASSERT_TRUE(block.condition.has_value());
    const auto& init = block.condition.value().init.value();
    ASSERT_EQ(init.arg_name, predicate::Argument::kBusiness);
    std::unordered_set<std::variant<std::string, int>> expected_business;
    expected_business.insert(business);
    ASSERT_EQ(init.set.value(), expected_business);
  }

  formats::json::ValueBuilder layout_builder{formats::common::Type::kObject};
  tab_bar.FilterSourceResponse(GetDataSourceResponse(block_counts));
  tab_bar.UpdateLayout(layout_builder);
  auto layout = layout_builder.ExtractValue();

  const static std::string kDataSection = "tab_bar";

  auto list = layout["data"][kDataSection]["payload"]["list"];
  ASSERT_EQ(list.GetSize(),
            2u);  // rest + main, магазины должны быть отфильтрованы

  const size_t first_idx = 0;
  const size_t last_idx = list.GetSize() - 1;

  ASSERT_EQ(list[first_idx]["id"].As<std::string>(), config.tabs.front().id);
  ASSERT_EQ(list[last_idx]["id"].As<std::string>(), config.tabs.back().id);
}

TEST(TabBar, ForceSelect) {
  // Проверяем, что если был запрошен недоступный таб
  // он отдается в выдаче

  auto config = MakeConfig();

  std::unordered_map<std::string, int> block_counts{
      {"tab_bar_rest", 1},
      // Отдаем 0 магазинов и так как таб выбран, он должен быть в выдаче
      {"tab_bar_shops", 0},
  };
  models::View view;
  view.type = models::ViewType::kTab;
  view.slug = models::ViewSlug{"shops"};
  eats_layout_constructor::models::RequestParams params{};
  experiments3::models::CacheManagerPtr experiments3{};
  TabBar tab_bar{experiments3, params, config, view};

  sources::DataSourceParams source_params;

  formats::json::ValueBuilder layout_builder{formats::common::Type::kObject};
  tab_bar.FilterSourceResponse(GetDataSourceResponse(block_counts));
  tab_bar.UpdateLayout(layout_builder);
  auto layout = layout_builder.ExtractValue();

  const static std::string kDataSection = "tab_bar";

  const auto widget = layout["data"][kDataSection]["payload"];
  const auto list = widget["list"];
  ASSERT_EQ(list.GetSize(), config.tabs.size());

  const size_t first_idx = 0;
  const size_t last_idx = list.GetSize() - 1;

  ASSERT_EQ(list[first_idx]["id"].As<std::string>(), config.tabs.front().id);
  ASSERT_EQ(list[last_idx]["id"].As<std::string>(), config.tabs.back().id);

  ASSERT_EQ(widget["current_id"].As<std::string>(), view.slug.GetUnderlying());
}

TEST(TabBar, CartTab) {
  // Проверяем формирование таба, который ведет на коризину

  TabBar::Config config{};
  config.enabled = true;
  auto& cart_tab = config.tabs.emplace_back();
  cart_tab.id = "cart";
  cart_tab.icon = "cart/icon";
  cart_tab.name = "Корзина";

  config::ScreenAction screen_action{};
  screen_action.screen = config::Screen::kCart;
  cart_tab.action = screen_action;
  cart_tab.business = {};

  models::View view;
  view.type = models::ViewType::kTab;
  view.slug = models::ViewSlug{"shops"};
  eats_layout_constructor::models::RequestParams params{};
  experiments3::models::CacheManagerPtr experiments3{};
  TabBar tab_bar{experiments3, params, config, view};

  sources::DataSourceParams source_params;
  formats::json::ValueBuilder layout_builder{formats::common::Type::kObject};
  tab_bar.FilterSourceResponse(GetDefaultDataSourceResponse());
  tab_bar.UpdateLayout(layout_builder);
  auto layout = layout_builder.ExtractValue();

  const static std::string kDataSection = "tab_bar";

  const auto list = layout["data"][kDataSection]["payload"]["list"];
  ASSERT_EQ(list.GetSize(), config.tabs.size());

  const auto tab = list[0];
  ASSERT_EQ(tab["id"].As<std::string>(), cart_tab.id);
  ASSERT_EQ(tab["action_type"].As<std::string>(), "screen");
  ASSERT_EQ(tab["action_payload"]["screen"].As<std::string>(), "cart");
}

TEST(TabBar, Deeplink) {
  TabBar::Config config{};
  config.enabled = true;
  config.tabs.emplace_back(config::Tab{
      "deeplink_tab",  // id
      "lavka.ico",     // icon
      "Uber Eats",     // name
      config::TabAction{config::DeeplinkAction{
          config::DeeplinkActionType::kDeeplink,  // type
          "lavka://not_here/",                    // deeplink
      }},
      {eats_shared::Business::kStore},
  });

  const static std::string kStoreBlockId = "tab_bar_deeplink_tab";

  std::unordered_map<std::string, int> block_counts{
      {kStoreBlockId, 1},
  };
  eats_layout_constructor::models::RequestParams params{};
  experiments3::models::CacheManagerPtr experiments3{};
  TabBar tab_bar{experiments3, params, config, std::nullopt};

  sources::DataSourceParams source_params;
  tab_bar.FillSourceRequestParams(source_params);
  auto catalog_params = GetCatalogParams(source_params);

  ASSERT_EQ(catalog_params.blocks.size(), block_counts.size());
  std::vector<std::pair<std::string, std::string>> block_params{
      {kStoreBlockId, "store"}};

  for (const auto& [block_id, business] : block_params) {
    ASSERT_TRUE(catalog_params.blocks.count(block_id) == 1)
        << "failed to find block: " << block_id;

    const auto& block = catalog_params.blocks.at(block_id);
    ASSERT_TRUE(block.no_data);
    ASSERT_TRUE(block.condition.has_value());
    const auto& init = block.condition.value().init.value();
    ASSERT_EQ(init.arg_name, predicate::Argument::kBusiness);
    std::unordered_set<std::variant<std::string, int>> expected_business;
    expected_business.insert(business);
    ASSERT_EQ(init.set.value(), expected_business);
  }

  formats::json::ValueBuilder layout_builder{formats::common::Type::kObject};
  tab_bar.FilterSourceResponse(GetDataSourceResponse(block_counts));
  tab_bar.UpdateLayout(layout_builder);
  auto layout = layout_builder.ExtractValue();

  const static std::string kDataSection = "tab_bar";

  auto list = layout["data"][kDataSection]["payload"]["list"];
  ASSERT_EQ(list.IsArray() && list.GetSize(), 1u);

  ASSERT_EQ(list[0]["id"].As<std::string>(), config.tabs.front().id);
}

}  // namespace eats_layout_constructor::static_widgets::tab_bar
