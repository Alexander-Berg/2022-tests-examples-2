#include "json_test_utils.hpp"
#include "menu_json_version_types.hpp"

namespace eats_restapp_menu::merging {

bool OneWayCompare(const IdToJsonValueMap& first_id_map,
                   const IdToJsonValueMap& second_id_map) {
  for (const auto& [id, first_value] : first_id_map) {
    if (const auto& second_value_it = second_id_map.find(id);
        second_value_it != second_id_map.end()) {
      if (first_value != second_value_it->second) {
        return false;
      }
    } else {
      return false;
    }
  }
  return true;
}

bool AreJsonArrayEqualsById(const JsonVal& first, const JsonVal& second,
                            const std::string& id_field_name) {
  const auto& first_id_map = GenerateMap(first, id_field_name);
  const auto& second_id_map = GenerateMap(second, id_field_name);

  return OneWayCompare(first_id_map, second_id_map) &&
         OneWayCompare(second_id_map, first_id_map);
}

bool CheckJsonEquals(const JsonVal& first, const JsonVal& second) {
  return AreJsonArrayEqualsById(first[kJsonPathCategories],
                                second[kJsonPathCategories],
                                kCategoriesUniqueIdFieldName) &&
         AreJsonArrayEqualsById(first[kJsonPathItems], second[kJsonPathItems],
                                kItemsUniqueIdFieldName);
}

}  // namespace eats_restapp_menu::merging
