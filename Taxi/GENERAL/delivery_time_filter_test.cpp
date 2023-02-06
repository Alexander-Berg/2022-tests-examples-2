#include <gtest/gtest.h>

#include "delivery_time_filter.hpp"

namespace {

using std::literals::chrono_literals::operator""min;

using DeliveryTimeFilter =
    handlers::internal_v1_catalog_for_layout::post::filters::DeliveryTimeFilter;

using DeliveryTimeFilterSettings = handlers::internal_v1_catalog_for_layout::
    post::filters::DeliveryTimeFilterSettings;

using DeliveryTimeFilterValue = handlers::internal_v1_catalog_for_layout::post::
    filters::DeliveryTimeFilterValue;

using DeliveryTimeFilterUnlimitedValue =
    handlers::internal_v1_catalog_for_layout::post::filters::
        DeliveryTimeFilterUnlimitedValue;

using FilterState = handlers::FilterState;

using eats_catalog::models::Place;
using eats_catalog::models::PlaceInfo;

DeliveryTimeFilterSettings MakeSettings(const bool forced = false) {
  DeliveryTimeFilterSettings settings{};
  settings.min_items = 3;
  settings.values = {
      DeliveryTimeFilterValue{
          "zero",
          "0",
          true,
          0min,
      },
      DeliveryTimeFilterValue{
          "thirty",
          "30",
          forced,
          30min,
      },
      DeliveryTimeFilterValue{
          "forty_five",
          "45",
          forced,
          45min,
      },
      DeliveryTimeFilterValue{
          "sixty",
          "60",
          forced,
          60min,
      },
      DeliveryTimeFilterValue{
          "sixty_plus",
          "60+",
          forced,
          DeliveryTimeFilterUnlimitedValue::kUnlimited,
      },
  };
  return settings;
}

class PlaceStorage {
 public:
  PlaceStorage(const std::vector<std::chrono::minutes>& max_times) {
    // reserve нужен, чтобы ссылки на PlaceInfo не инвалидировались
    place_infos_.reserve(max_times.size());
    places_.reserve(max_times.size());
    for (const auto max : max_times) {
      auto& place_info = place_infos_.emplace_back();
      auto& place = places_.emplace_back(place_info);
      place.timings.estimated.min = max - 10min;
      place.timings.estimated.max = max;
    }
  }

  // Копирование инвалидирует ссылки на PlaceInfo
  PlaceStorage(const PlaceStorage&) = delete;
  PlaceStorage& operator=(const PlaceStorage&) = delete;

  void Fill(DeliveryTimeFilter& delivery_time_filter) const {
    for (const auto& place : places_) {
      delivery_time_filter.Fill(place);
    }
  }

 private:
  std::vector<PlaceInfo> place_infos_;
  std::vector<Place> places_;
};

}  // namespace

TEST(DeliveryTimeFilter, EmptyInput) {
  // Проверяем что на пустых настройках фильтр не возвращает значений
  DeliveryTimeFilterSettings settings{};
  settings.min_items = 2;
  settings.values = {};
  DeliveryTimeFilter filter{settings, false};
  const auto result = filter.BuildRenderFilter(std::nullopt);
  ASSERT_FALSE(result.has_value());
}

TEST(DeliveryTimeFilter, ForcedValues) {
  // Проверяем что если все значения помечены force, то не зависимо
  // от диапазона времени с плейсов, все значения возвращаются
  const auto settings = MakeSettings(/*force=*/true);
  DeliveryTimeFilter filter{settings, false};
  const auto result = filter.BuildRenderFilter(std::nullopt);

  ASSERT_TRUE(result.has_value());

  const auto& actual = result.value().values;
  ASSERT_EQ(actual.size(), settings.values.size());

  for (size_t i = 0; i < actual.size(); i++) {
    ASSERT_EQ(actual[i].slug, settings.values[i].slug);
    ASSERT_EQ(actual[i].text, settings.values[i].text);
  }
}

TEST(DeliveryTimeFilter, Border) {
  // Проверяем что плейс с временем доставки 20-30 минут
  // активирует только интервал 0-30
  auto settings = MakeSettings();
  settings.min_items = 2;

  PlaceStorage places({
      30min,
  });

  DeliveryTimeFilter filter{settings, false};
  places.Fill(filter);
  const auto result = filter.BuildRenderFilter(std::nullopt);

  ASSERT_TRUE(result.has_value());

  const auto& actual = result.value().values;
  std::vector<std::string_view> expected_slugs = {"zero", "thirty"};
  ASSERT_EQ(actual.size(), expected_slugs.size());

  for (size_t i = 0; i < actual.size(); i++) {
    ASSERT_EQ(actual[i].slug, expected_slugs[i]);
  }
}

TEST(DeliveryTimeFilter, Unlimited) {
  // Проверяем что плейсы с временем доставки
  // 120 - 130 минут
  // активирует только интервал 0 - 60+
  auto settings = MakeSettings();
  settings.min_items = 2;

  PlaceStorage places({
      130min,
  });

  DeliveryTimeFilter filter{settings, false};
  places.Fill(filter);
  const auto result = filter.BuildRenderFilter(std::nullopt);

  ASSERT_TRUE(result.has_value());

  const auto& actual = result.value().values;
  std::vector<std::string_view> expected_slugs = {"zero", "sixty_plus"};
  ASSERT_EQ(actual.size(), expected_slugs.size());

  for (size_t i = 0; i < actual.size(); i++) {
    ASSERT_EQ(actual[i].slug, expected_slugs[i]);
  }
}

TEST(DeliveryTimeFilter, PlaceRangeGreaterThenLastValue) {
  // Проверяем что фильтр не возвращает значений,
  // если диапазон времени с плейсa (120 - 130) больше диапазона
  // в настройках (0 - 60)
  auto settings = MakeSettings();
  settings.values.pop_back();

  PlaceStorage places({
      130min,
  });

  DeliveryTimeFilter filter{settings, false};
  places.Fill(filter);
  const auto result = filter.BuildRenderFilter(std::nullopt);

  ASSERT_FALSE(result.has_value());
}

TEST(DeliveryTimeFilter, DefaultSelected) {
  // Проверяем что selected проставляется на последний элемент по умолчанию
  const auto settings = MakeSettings();
  PlaceStorage places({
      30min,
      40min,
      50min,
      70min,
  });
  DeliveryTimeFilter filter{settings, false};
  places.Fill(filter);
  const auto result = filter.BuildRenderFilter(std::nullopt);

  ASSERT_TRUE(result.has_value());

  const auto& actual = result.value().values;
  ASSERT_EQ(actual.size(), settings.values.size());
  ASSERT_EQ(actual.back().state, FilterState::kSelected);

  for (size_t i = 0; i < actual.size() - 1; i++) {
    ASSERT_EQ(actual[i].state, FilterState::kEnabled);
  }
}

TEST(DeliveryTimeFilter, BottomAndLimitSelected) {
  // Проверяем что selected проставляется на последний элемент,
  // если он явно передан
  const auto settings = MakeSettings();
  PlaceStorage places({
      30min,
      40min,
      50min,
      70min,
  });
  DeliveryTimeFilter filter{settings, false};
  places.Fill(filter);

  const auto result = filter.BuildRenderFilter("sixty_plus");

  ASSERT_TRUE(result.has_value());

  const auto& actual = result.value().values;
  ASSERT_EQ(actual.size(), settings.values.size());
  ASSERT_EQ(actual.back().state, FilterState::kSelected);

  for (size_t i = 0; i < actual.size() - 1; i++) {
    ASSERT_EQ(actual[i].state, FilterState::kEnabled);
  }
}

TEST(DeliveryTimeFilter, FourtyFilveSelected) {
  // Проверяем что selected проставляется в середине диапазона
  const auto settings = MakeSettings();
  PlaceStorage places({
      30min,
      40min,
      50min,
      70min,
  });
  DeliveryTimeFilter filter{settings, false};
  places.Fill(filter);
  const auto result = filter.BuildRenderFilter("forty_five");

  ASSERT_TRUE(result.has_value());

  const auto& actual = result.value().values;
  ASSERT_EQ(actual.size(), settings.values.size());

  bool has_forty_five = false;

  for (size_t i = 0; i < actual.size() - 1; i++) {
    if (actual[i].slug == "forty_five") {
      ASSERT_EQ(actual[i].state, FilterState::kSelected);
      has_forty_five = true;
    } else {
      ASSERT_EQ(actual[i].state, FilterState::kEnabled);
    }
  }

  ASSERT_TRUE(has_forty_five);
}

TEST(DeliveryTimeFilter, DefaultValue) {
  // Проверяем, что дефолтное значение проставляется
  // как последний элемент из списка значений
  const auto settings = MakeSettings();
  PlaceStorage places({
      30min,
      40min,
      50min,
  });
  DeliveryTimeFilter filter{settings, false};
  places.Fill(filter);
  const auto result = filter.BuildRenderFilter(std::nullopt);

  ASSERT_TRUE(result.has_value());
  ASSERT_FALSE(result->values.empty());
  ASSERT_EQ(result->default_, result->values.back().slug);
}

TEST(DeliveryTimeFilter, IsAvailable) {
  // Проверяем, что дефолтное значение проставляется
  // как последний элемент из списка значений
  const auto settings = MakeSettings();
  PlaceStorage places({
      30min,
      40min,
      50min,
  });
  DeliveryTimeFilter filter{settings, true};
  places.Fill(filter);
  ASSERT_FALSE(filter.IsActive());
}
