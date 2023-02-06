#include "utils_test.hpp"

#include <gtest/gtest.h>

#include <eats-analytics/context.hpp>

namespace eats_layout_constructor::widgets::turbo_buttons::tests {

namespace {

EtaColors GetEtaColors() {
  EtaColors eta_colors;
  eta_colors.open.light = "open_light";
  eta_colors.open.dark = "open_dark";
  eta_colors.closed.light = "closed_light";
  eta_colors.closed.dark = "closed_dark";
  return eta_colors;
}

Colors GetColors() {
  Colors colors;
  colors.light = "light";
  colors.dark = "dark";
  return colors;
}

formats::json::Value GetPlaceJson(const Place& input) {
  defs::internal::turbo_buttons::PlaceForButton place;
  place.name = input.name;
  place.slug = input.slug;
  place.brand.business = input.business;
  place.availability.is_available = input.available;
  auto& delivery = place.data.features.delivery.emplace();
  delivery.text = input.eta;
  auto& logos = place.data.features.logo.emplace();
  auto& logo = logos.emplace_back();
  auto& value = logo.value.emplace_back();
  value.logo_url = input.logo_url;
  value.size = defs::internal::turbo_buttons::Size::kSmall;

  if (input.plus_badge.has_value()) {
    defs::internal::turbo_buttons::YandexPlusMeta plus{};
    plus.text = input.plus_badge.value().text;
    plus.icon_url = input.plus_badge.value().icon;
    auto& meta = place.data.meta.emplace();
    auto& plus_meta = meta.emplace_back();
    plus_meta.id = "id";
    plus_meta.type = "yandex_plus";
    plus_meta.payload.extra =
        formats::json::ValueBuilder{std::move(plus)}.ExtractValue();
  }
  return formats::json::ValueBuilder{place}.ExtractValue();
}

}  // namespace

sources::catalog::Place GetCatalogPlace(const Place& input) {
  sources::catalog::Place result{};
  result.meta.place_id = sources::PlaceId{input.place_id};
  result.meta.brand_id = sources::BrandId{input.brand_id};
  result.meta.is_avaialbe_now = input.is_avaialbe_now;

  result.payload = GetPlaceJson(input);

  return result;
}

ColorConfig GetColorConfig() {
  ColorConfig result{};
  result.eta_colors = GetEtaColors();
  result.description_colors = GetColors();
  result.plus_badge_background = GetColors();

  return result;
}

eats_layout_constructor::sources::DataSourceResponses GetDataSourceResponse(
    const std::string& block_id, const std::vector<Place>& places) {
  using Catalog = eats_layout_constructor::sources::CatalogDataSource;
  auto catalog_response =
      std::make_shared<Catalog::Response>(Catalog::Response{});

  std::vector<sources::catalog::Place> catalog_places;
  catalog_places.reserve(places.size());
  for (size_t i = 0; i < places.size(); i++) {
    catalog_places.push_back(GetCatalogPlace(places[i]));
  }
  catalog_response->blocks[block_id].places = std::move(catalog_places);

  eats_layout_constructor::sources::DataSourceResponses response;
  response[Catalog::kName] = catalog_response;
  return response;
}

void AssertColor(const std::vector<::handlers::ThemedColorA>& color,
                 const std::string& light, const std::string& dark) {
  ASSERT_EQ(color.size(), 2);
  for (const auto& item : color) {
    if (item.theme == ::handlers::Theme::kLight) {
      ASSERT_EQ(item.value, light);
    }
    if (item.theme == ::handlers::Theme::kDark) {
      ASSERT_EQ(item.value, dark);
    }
  }
  ASSERT_NE(color.front().theme, color.back().theme);
}

formats::json::Value Render(const ButtonGroup& group) {
  formats::json::ValueBuilder result{formats::common::Type::kArray};

  std::vector<Button> buttons;
  group.Fill(buttons);
  for (const auto& button : buttons) {
    if (!button.IsValid()) {
      continue;
    }
    formats::json::ValueBuilder builder{formats::common::Type::kObject};
    button.Render(builder, eats_analytics::AnalyticsContext{});
    if (!builder.IsEmpty()) {
      result.PushBack(std::move(builder));
    }
  }

  return result.ExtractValue();
}

}  // namespace eats_layout_constructor::widgets::turbo_buttons::tests
