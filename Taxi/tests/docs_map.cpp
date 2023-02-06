#include "docs_map.hpp"

#include <taxi_config/variables/APPLICATION_BRAND_RELATED_BRANDS.hpp>
#include <taxi_config/variables/APPLICATION_MAP_BRAND.hpp>
#include <taxi_config/variables/FRIEND_BRANDS.hpp>

std::vector<dynamic_config::KeyValue> DefaultConfigsForTests() {
  return {
      {taxi_config::FRIEND_BRANDS, {}},
      {taxi_config::APPLICATION_MAP_BRAND, {}},
      {taxi_config::APPLICATION_BRAND_RELATED_BRANDS, {}},
  };
}
