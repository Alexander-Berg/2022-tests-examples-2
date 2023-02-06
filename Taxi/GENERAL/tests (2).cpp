#include "tests.hpp"
#include <taxi_config/taxi_config.hpp>
#include <userver/dynamic_config/snapshot.hpp>
#include <userver/logging/log.hpp>

namespace persey_labs::utils {

namespace {
const int kDefaultDaysToReady = 3;
}

std::optional<handlers::TestType> GetTestById(
    const std::string& id, const handlers::Dependencies& deps) {
  const auto& tariffs =
      deps.config.Get<taxi_config::TaxiConfig>().persey_labs_tests;
  const auto tariff_it = tariffs.extra.find(id);
  if (tariff_it == tariffs.extra.end()) {
    LOG_ERROR() << "unknown tariff " << id;
    return std::nullopt;
  }
  handlers::TestType result;
  result.id = id;
  result.name = tariff_it->second.name;
  result.days_to_ready =
      tariff_it->second.days_to_ready.value_or(kDefaultDaysToReady);
  if (tariff_it->second.test_systems) {
    for (const auto& test_system : *tariff_it->second.test_systems) {
      result.test_systems.push_back({test_system.name, test_system.qualities});
    }
  }
  result.price.logistics_rub = tariff_it->second.price.logistics_rub;
  result.price.test_rub = tariff_it->second.price.test_rub;
  result.price.sampling_rub = tariff_it->second.price.sampling_rub;
  return std::move(result);
}

std::optional<handlers::TestPrice> GetTestPrice(
    const std::string& id, const std::string& lab_entity_id,
    std::int32_t locality_id, const handlers::Dependencies& deps) {
  const auto& tests =
      deps.config.Get<taxi_config::TaxiConfig>().persey_labs_tests.extra;

  auto test_iter = tests.find(id);
  if (test_iter == tests.end()) {
    return std::nullopt;
  }
  const auto& test = test_iter->second;

  auto config_price = test.price;
  if (test.detailed_price) {
    auto detailed_price_iter = test.detailed_price->extra.find(lab_entity_id);
    if (detailed_price_iter != test.detailed_price->extra.end()) {
      config_price =
          detailed_price_iter->second.Get(std::to_string(locality_id));
    }
  }

  handlers::TestPrice result;
  result.test_rub = config_price.test_rub;
  result.logistics_rub = config_price.logistics_rub;
  result.sampling_rub = config_price.sampling_rub;

  return result;
}

std::vector<handlers::TestType> GetTests(const handlers::Dependencies& deps) {
  std::vector<handlers::TestType> tests;
  for (const auto& [k, v] :
       deps.config.Get<taxi_config::TaxiConfig>().persey_labs_tests.extra) {
    handlers::TestType test;
    test.id = k;
    test.name = v.name;
    test.days_to_ready = v.days_to_ready.value_or(kDefaultDaysToReady);
    if (v.test_systems) {
      for (const auto& test_system : *v.test_systems) {
        test.test_systems.push_back({test_system.name, test_system.qualities});
      }
    }
    test.price.logistics_rub = v.price.logistics_rub;
    test.price.test_rub = v.price.test_rub;
    test.price.sampling_rub = v.price.sampling_rub;
    tests.emplace_back(std::move(test));
  }
  return tests;
}

}  // namespace persey_labs::utils
