#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include "weather_suggest_settings.hpp"

TEST(TestWeatherSuggestSettings, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& weather_suggest_settings =
      config.Get<config::WeatherSuggestSettings>();
  ASSERT_EQ(weather_suggest_settings.api_host,
            "http://api.openweathermap.org/data/2.5/weather");
}
