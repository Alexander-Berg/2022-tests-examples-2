#include <gtest/gtest.h>

#include <userver/dynamic_config/snapshot.hpp>

#include <testing/taxi_config.hpp>
#include "layout_experiment.hpp"

namespace eats_layout_constructor::models {

namespace {

struct Config {
  std::string main_page{};
  std::string recomendations{};
  std::string collections{};
  std::string map{};
  std::string filters{};
  std::string tabs{};

  std::unordered_map<std::string, std::string> collections_slugs{};
  std::unordered_map<std::string, std::string> tabs_slugs{};
};

/*
 * NOTE: Если посто конктруировать snapshot в функции, то тест падает с азертом,
 * что RCU variable is destroyed while being used поэтому держим storage_mock_ в
 * поле класса
 */
class ConfigMock {
 public:
  explicit ConfigMock(const Config& config) {
    ::taxi_config::eats_layout_constructor_experiment_settings::
        EatsLayoutConstructorExperimentSettings settings;
    settings.experiment_name = config.main_page;
    settings.recommendations_experiment_name = config.recomendations;
    settings.collections_experiment_name = config.collections;
    settings.map_experiment_name = config.map;
    settings.filters_experiment_name = config.filters;
    settings.collections_slugs_experiment_name.emplace().extra =
        config.collections_slugs;
    settings.tabs_experiment_name = config.tabs;
    settings.tabs_slugs_experiment_names.emplace().extra = config.tabs_slugs;

    storage_mock_ = dynamic_config::StorageMock{
        {::taxi_config::EATS_LAYOUT_CONSTRUCTOR_EXPERIMENT_SETTINGS, settings}};
  };

  ::dynamic_config::Snapshot Get() const { return storage_mock_.GetSnapshot(); }

 private:
  ::dynamic_config::StorageMock storage_mock_;
};

}  // namespace

TEST(GetLayoutExperimentName, main) {
  Config config{};
  config.main_page = "main_page_exp";
  RequestParams params{};
  const auto experiment_name =
      GetLayoutExperimentName(params, ConfigMock{config}.Get());
  ASSERT_EQ(experiment_name, config.main_page);
}

TEST(GetLayoutExperimentName, recomandations) {
  Config config{};
  config.recomendations = "recomendations";
  RequestParams params{};
  params.view.emplace().type = ViewType::kRecommendation;
  const auto experiment_name =
      GetLayoutExperimentName(params, ConfigMock{config}.Get());
  ASSERT_EQ(experiment_name, config.recomendations);
}

TEST(GetLayoutExperimentName, collection) {
  Config config{};
  config.collections = "collections";
  RequestParams params{};
  params.view.emplace().type = ViewType::kCollection;
  const auto experiment_name =
      GetLayoutExperimentName(params, ConfigMock{config}.Get());
  ASSERT_EQ(experiment_name, config.collections);
}

TEST(GetLayoutExperimentName, map) {
  Config config{};
  config.map = "map";
  RequestParams params{};
  params.view.emplace().type = ViewType::kMap;
  const auto experiment_name =
      GetLayoutExperimentName(params, ConfigMock{config}.Get());
  ASSERT_EQ(experiment_name, config.map);
}

TEST(GetLayoutExperimentName, filters) {
  Config config{};
  config.filters = "filters";
  RequestParams params{};
  auto& filter = params.filters.emplace_back();
  filter.slug = FilterSlug{"slug"};
  filter.type = FilterType{"type"};
  const auto experiment_name =
      GetLayoutExperimentName(params, ConfigMock{config}.Get());
  ASSERT_EQ(experiment_name, config.filters);
}

TEST(GetLayoutExperimentName, filters_v2) {
  Config config{};
  config.filters = "filters";
  RequestParams params{};
  auto& filter = params.filters_v2.emplace_back();
  filter.slug = FilterSlug{"slug"};
  filter.type = FilterType{"type"};
  const auto experiment_name =
      GetLayoutExperimentName(params, ConfigMock{config}.Get());
  ASSERT_EQ(experiment_name, config.filters);
}

TEST(GetLayoutExperimentName, quick_filter_slug) {
  Config config{};
  config.filters = "filters";
  RequestParams params{};
  params.quick_filter_slug = FilterSlug{"slug"};
  const auto experiment_name =
      GetLayoutExperimentName(params, ConfigMock{config}.Get());
  ASSERT_EQ(experiment_name, config.filters);
}

TEST(GetLayoutExperimentName, collections_slugs_experiment_name) {
  const static std::string kShops{"shops"};
  Config config{};
  config.collections = "default_collections";
  config.collections_slugs[kShops] = "shops_collection";
  RequestParams params{};
  auto& view = params.view.emplace();
  view.type = ViewType::kCollection;
  view.slug = ViewSlug{kShops};
  const auto experiment_name =
      GetLayoutExperimentName(params, ConfigMock{config}.Get());
  ASSERT_EQ(experiment_name, config.collections_slugs.at(kShops));
}

TEST(GetLayoutExperimentName, collections_slugs_experiment_name_default) {
  const static std::string kShops{"shops"};
  const static std::string kNoShops{"no_shops"};
  Config config{};
  config.collections = "default_collections";
  config.collections_slugs[kShops] = "shops_collection";
  RequestParams params{};
  auto& view = params.view.emplace();
  view.type = ViewType::kCollection;
  view.slug = ViewSlug{kNoShops};
  const auto experiment_name =
      GetLayoutExperimentName(params, ConfigMock{config}.Get());
  ASSERT_EQ(experiment_name, config.collections);
}

TEST(GetLayoutExperimentName, tabs_slugs_experiment_name) {
  const static std::string kShops{"shops"};
  Config config{};
  config.tabs = "default_tabs";
  config.tabs_slugs[kShops] = "shops_tab";
  RequestParams params{};
  auto& view = params.view.emplace();
  view.type = ViewType::kTab;
  view.slug = ViewSlug{kShops};
  const auto experiment_name =
      GetLayoutExperimentName(params, ConfigMock{config}.Get());
  ASSERT_EQ(experiment_name, config.tabs_slugs.at(kShops));
}

TEST(GetLayoutExperimentName, tabs_slugs_experiment_name_default) {
  const static std::string kShops{"shops"};
  const static std::string kNoShops{"no_shops"};
  Config config{};
  config.tabs = "default_tabs";
  config.tabs_slugs[kShops] = "shops_tab";
  RequestParams params{};
  auto& view = params.view.emplace();
  view.type = ViewType::kTab;
  view.slug = ViewSlug{kNoShops};
  const auto experiment_name =
      GetLayoutExperimentName(params, ConfigMock{config}.Get());
  ASSERT_EQ(experiment_name, config.tabs);
}

}  // namespace eats_layout_constructor::models
