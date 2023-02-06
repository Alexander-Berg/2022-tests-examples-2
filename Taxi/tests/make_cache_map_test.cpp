#include <tariff_settings/models.hpp>

#include <userver/cache/statistics_mock.hpp>
#include <userver/utest/utest.hpp>

#include <tariff_settings/utils.hpp>

namespace taxi_tariffs {

models::TariffSettings MockItem(
    const std::string& zone, std::optional<bool> is_disabled = std::nullopt) {
  return models::TariffSettings{std::string("identifier"), zone, is_disabled};
}

UTEST(TestMakeMap, Simple) {
  cache::UpdateStatisticsScopeMock stats(cache::UpdateType::kFull);

  const auto& item = MockItem("magadan");
  auto result = MakeCacheMap({item}, stats.GetScope());

  ASSERT_EQ(result.size(), 1);
  ASSERT_EQ(result.at("magadan"), item);

  // duplicate key
  result = MakeCacheMap({item, item}, stats.GetScope());
  ASSERT_EQ(result.size(), 1);
}

UTEST(TestMakeMap, NoZone) {
  cache::UpdateStatisticsScopeMock stats(cache::UpdateType::kFull);
  std::vector<models::TariffSettings> items{MockItem("moscow"), MockItem("spb"),
                                            MockItem("tula"),
                                            models::TariffSettings{}};

  const auto& result = MakeCacheMap(std::move(items), stats.GetScope());
  ASSERT_EQ(result.size(), 3);
}

UTEST(TestMakeMap, WithOldMap) {
  cache::UpdateStatisticsScopeMock stats(cache::UpdateType::kFull);
  std::vector<models::TariffSettings> items{MockItem("moscow"), MockItem("spb"),
                                            MockItem("tula"),
                                            models::TariffSettings{}};
  auto old_map = MakeCacheMap(std::move(items), stats.GetScope());
  ASSERT_EQ(old_map.at("moscow").is_disabled, std::nullopt);

  auto new_map = taxi_tariffs::MakeCacheMap(
      {MockItem("tel-aviv"), MockItem("moscow", true)}, stats.GetScope(),
      std::move(old_map));

  ASSERT_EQ(new_map.size(), 4);
  ASSERT_EQ(new_map.at("moscow").is_disabled, true);
  ASSERT_TRUE(new_map.count("moscow") == 1);
  ASSERT_TRUE(new_map.count("tel-aviv") == 1);
  ASSERT_TRUE(new_map.count("spb") == 1);
  ASSERT_TRUE(new_map.count("tula") == 1);
}

}  // namespace taxi_tariffs
