#include <gtest/gtest.h>

#include <eats-analytics/context.hpp>

#include <widgets/turbo_buttons/place_button.hpp>

#include "utils_test.hpp"

#include <fmt/format.h>

namespace eats_layout_constructor::widgets::turbo_buttons::tests {

namespace {

PlaceButtonMapper MakePlaceButtonMapper(const ColorConfig& color_config) {
  const static std::unordered_map<sources::BrandId, std::string> kBrandIcons;
  return PlaceButtonMapper{kBrandIcons, color_config};
}

}  // namespace

TEST(PlaceButtonMapper, Generic) {
  // Проверяет общее преекладывание полей из
  // ответа каталога в кнопку
  Place place{};

  auto color_config = GetColorConfig();
  auto mapper = MakePlaceButtonMapper(color_config);
  auto button = mapper.Map(GetCatalogPlace(place));

  formats::json::ValueBuilder builder;
  const bool ok = button.Render(builder, eats_analytics::AnalyticsContext{});
  ASSERT_TRUE(ok);

  auto result = builder.ExtractValue().As<::handlers::TurboButton>();

  ASSERT_FALSE(result.id.empty());
  ASSERT_EQ(result.name, place.name);
  ASSERT_EQ(result.description.value().text, place.eta);
  ASSERT_EQ(result.app_link,
            fmt::format("eda.yandex://restaurant/{}", place.slug));
  ASSERT_EQ(result.icon, place.logo_url);
}

TEST(PlaceButtonMapper, LavkaDeeplink) {
  // Проверяет, что для лавки формируется
  // правильный диплинк
  Place place{};
  place.business = defs::internal::turbo_buttons::Business::kStore;

  const auto color_config = GetColorConfig();

  auto mapper = MakePlaceButtonMapper(color_config);
  auto button = mapper.Map(GetCatalogPlace(place));

  formats::json::ValueBuilder builder;
  const bool ok = button.Render(builder, eats_analytics::AnalyticsContext{});
  ASSERT_TRUE(ok);

  auto result = builder.ExtractValue().As<::handlers::TurboButton>();

  ASSERT_EQ(result.app_link, "eda.yandex://lavka");
}

TEST(PlaceButtonMapper, Colors) {
  // Проверяет, что описанию можно задать цвет
  Place place{};

  const auto color_config = GetColorConfig();
  const auto& eta_colors = color_config.eta_colors;

  auto mapper = MakePlaceButtonMapper(color_config);
  auto button = mapper.Map(GetCatalogPlace(place));

  formats::json::ValueBuilder builder;
  const bool ok = button.Render(builder, eats_analytics::AnalyticsContext{});
  ASSERT_TRUE(ok);

  auto result = builder.ExtractValue().As<::handlers::TurboButton>();

  ASSERT_TRUE(result.description.has_value());
  const auto& value = result.description.value();
  ASSERT_EQ(value.text, place.eta);
  AssertColor(value.color, eta_colors.open.light, eta_colors.open.dark);
}

TEST(PlaceButtonMapper, ClosedColors) {
  // Проверяет, что ETA красится в нужный цвет
  // в зависимости от доступности реста
  Place place{};
  auto color_config = GetColorConfig();
  auto& eta_colors = color_config.eta_colors;
  eta_colors.open.light = "open_light";
  eta_colors.open.dark = "open_dark";
  eta_colors.closed.light = "closed_light";
  eta_colors.closed.dark = "closed_dark";

  auto mapper = MakePlaceButtonMapper(color_config);
  auto button = mapper.Map(GetCatalogPlace(place));

  formats::json::ValueBuilder builder;
  const bool ok = button.Render(builder, eats_analytics::AnalyticsContext{});
  ASSERT_TRUE(ok);

  auto result = builder.ExtractValue().As<::handlers::TurboButton>();

  ASSERT_TRUE(result.description.has_value());
  const auto& value = result.description.value();
  ASSERT_EQ(value.text, place.eta);
  AssertColor(value.color, eta_colors.open.light, eta_colors.open.dark);
}

TEST(PlaceButtonMapper, BrandIcon) {
  // Проверяет, что иконка переопределяется
  // мапой из конструктора
  Place place{};

  const sources::BrandId kBrandId{1};
  const std::string kBrandIcon = "brand_icon";

  auto color_config = GetColorConfig();
  auto catalog_place = GetCatalogPlace(place);

  catalog_place.meta.brand_id = kBrandId;

  std::unordered_map<sources::BrandId, std::string> brand_icons;
  brand_icons.emplace(kBrandId, kBrandIcon);

  PlaceButtonMapper mapper{brand_icons, color_config};

  auto button = mapper.Map(catalog_place);

  formats::json::ValueBuilder builder;
  const bool ok = button.Render(builder, eats_analytics::AnalyticsContext{});
  ASSERT_TRUE(ok);

  auto result = builder.ExtractValue().As<::handlers::TurboButton>();

  ASSERT_EQ(result.icon, kBrandIcon);
}

TEST(PlaceButtonMapper, PlusBadge) {
  // Проверяет, что фича плюса корректно перекладывается
  // в фичу кнопки
  Place place{};
  auto& plus = place.plus_badge.emplace();
  plus.icon = "plus/icon";
  plus.text = "plus_text";

  auto catalog_place = GetCatalogPlace(place);
  EtaColors eta_colors;
  auto color_config = GetColorConfig();
  color_config.plus_badge_background.light = "light_plus";
  color_config.plus_badge_background.dark = "dark_plus";

  const sources::BrandId kBrandId{1};
  const std::string kBrandIcon = "brand_icon";

  catalog_place.meta.brand_id = kBrandId;

  std::unordered_map<sources::BrandId, std::string> brand_icons;
  brand_icons.emplace(kBrandId, kBrandIcon);

  PlaceButtonMapper mapper{brand_icons, color_config};

  auto button = mapper.Map(catalog_place);

  formats::json::ValueBuilder builder;
  const bool ok = button.Render(builder, eats_analytics::AnalyticsContext{});
  ASSERT_TRUE(ok);

  auto result = builder.ExtractValue().As<::handlers::TurboButton>();

  ASSERT_TRUE(result.features.has_value());
  ASSERT_TRUE(result.features.value().badge.has_value());
  const auto& badge = result.features.value().badge.value();
  ASSERT_TRUE(badge.icon.has_value());
  ASSERT_EQ(badge.icon.value(), plus.icon);
  ASSERT_EQ(badge.text.text, plus.text);
  ASSERT_TRUE(badge.styles.has_value());
  ASSERT_TRUE(badge.styles.value().rainbow.has_value());
  ASSERT_TRUE(badge.styles.value().rainbow.value());
  AssertColor(badge.background_color, color_config.plus_badge_background.light,
              color_config.plus_badge_background.dark);
}

}  // namespace eats_layout_constructor::widgets::turbo_buttons::tests
