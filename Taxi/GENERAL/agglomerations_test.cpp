#include <gtest/gtest.h>

#include <utils/helpers/json.hpp>

#include <clients/taxi_agglomerations.hpp>
#include <taxi_agglomerations/api/list_geo_nodes.hpp>

#include <models/agglomerations/tree.hpp>

using utils::helpers::ParseJson;

generated::taxi_agglomerations::api::ListGeoNodes GetBrGeoNodesResponse() {
  const std::string kJson = R"JSON(
{
    "items": [
        {
            "name": "br_kazakhstan",
            "name_en": "Kazakhstan",
            "name_ru": "Казахстан",
            "node_type": "country",
            "parent_name": "br_root"
        },
        {
            "name": "br_moscow",
            "name_en": "Moscow",
            "name_ru": "Москва",
            "tanker_key": "name.br_moscow",
            "node_type": "agglomeration",
            "parent_name": "br_moskovskaja_obl"
        },
        {
            "name": "br_moscow_adm",
            "name_en": "Moscow (adm)",
            "name_ru": "Москва (адм)",
            "tanker_key": "name.br_moscow_adm",
            "node_type": "node",
            "parent_name": "br_moscow",
            "tariff_zones": [
                "boryasvo",
                "moscow",
                "vko"
            ]
        },
        {
            "name": "br_moscow_middle_region",
            "name_en": "Moscow (Middle Region)",
            "name_ru": "Москва (среднее)",
            "tanker_key": "name.br_moscow_middle_region",
            "node_type": "node",
            "parent_name": "br_moscow"
        },
        {
            "name": "br_moskovskaja_obl",
            "name_en": "Moscow Region",
            "name_ru": "Московская область",
            "tanker_key": "name.br_moskovskaja_obl",
            "node_type": "node",
            "parent_name": "br_tsentralnyj_fo"
        },
        {
            "name": "br_root",
            "name_en": "Basic Hierarchy",
            "name_ru": "Базовая иерархия",
            "tanker_key": "name.br_root",
            "node_type": "root"
        },
        {
            "name": "br_russia",
            "name_en": "Russia",
            "name_ru": "Россия",
            "tanker_key": "name.br_russia",
            "node_type": "country",
            "parent_name": "br_root"
        },
        {
            "name": "br_tsentralnyj_fo",
            "name_en": "Central Federal District",
            "name_ru": "Центральный ФО",
            "tanker_key": "name.br_tsentralnyj_fo",
            "node_type": "node",
            "parent_name": "br_russia"
        }
    ]
}
)JSON";

  const auto kBrGeoNodesResponseJson = ParseJson(kJson);

  generated::taxi_agglomerations::api::ListGeoNodes ret;
  generated::taxi_agglomerations::api::SafeUnpackMember(
      ret, kBrGeoNodesResponseJson, "br_geo_nodes");
  return ret;
}

TEST(Tree, GetByNameRoot) {
  models::agglomerations::Tree tree(GetBrGeoNodesResponse());
  const auto node = tree.GetByName("br_root");
  ASSERT_EQ(node->GetName(), "br_root");
  ASSERT_EQ(node->GetNameRu(), "Базовая иерархия");
  ASSERT_EQ(node->GetNameEn(), "Basic Hierarchy");
  ASSERT_EQ(node->GetTankerKey(), std::string_view{"name.br_root"});
  ASSERT_EQ(node->GetNodeType(),
            generated::taxi_agglomerations::api::NodeType::kRoot);
  ASSERT_EQ(node->GetTariffZones(), std::vector<std::string>());
  ASSERT_EQ(node->GetParent(), nullptr);
  std::set<std::string> children_names;
  for (const auto& child : node->GetChildren()) {
    children_names.emplace(child->GetName());
  }
  std::set<std::string> expected_children_names{"br_kazakhstan", "br_russia"};
  ASSERT_EQ(children_names, expected_children_names);
}

TEST(Tree, GetByNameCountry) {
  models::agglomerations::Tree tree(GetBrGeoNodesResponse());
  const auto node = tree.GetByName("br_russia");
  ASSERT_EQ(node->GetName(), "br_russia");
  ASSERT_EQ(node->GetNameRu(), "Россия");
  ASSERT_EQ(node->GetNameEn(), "Russia");
  ASSERT_EQ(node->GetNodeType(),
            generated::taxi_agglomerations::api::NodeType::kCountry);
  ASSERT_EQ(node->GetTariffZones(), std::vector<std::string>());
  ASSERT_EQ(node->GetParent()->GetName(), "br_root");
}

TEST(Tree, GetByTariffZone) {
  models::agglomerations::Tree tree(GetBrGeoNodesResponse());
  const auto node = tree.GetByTariffZone("moscow");
  ASSERT_EQ(node->GetName(), "br_moscow_adm");
  ASSERT_EQ(node->GetNameRu(), "Москва (адм)");
  ASSERT_EQ(node->GetNameEn(), "Moscow (adm)");
  ASSERT_EQ(node->GetNodeType(),
            generated::taxi_agglomerations::api::NodeType::kNode);
  std::vector<std::string> expected_tariff_zones{
      "boryasvo",
      "moscow",
      "vko",
  };
  ASSERT_EQ(node->GetTariffZones(), expected_tariff_zones);
  ASSERT_EQ(node->GetParent()->GetName(), "br_moscow");
}

TEST(Tree, GetAncestorsForMoscow) {
  models::agglomerations::Tree tree(GetBrGeoNodesResponse());

  std::vector<std::string> ancestor_names;

  for (const auto& ancestor : tree.GetAncestors("moscow")) {
    ancestor_names.push_back(std::string(ancestor->GetName()));
  }
  std::vector<std::string> expected_ancestor_names{
      "br_moscow_adm",     "br_moscow", "br_moskovskaja_obl",
      "br_tsentralnyj_fo", "br_russia", "br_root",
  };
  ASSERT_EQ(ancestor_names, expected_ancestor_names);
  ASSERT_EQ(tree.GetAncestorNames("moscow"), expected_ancestor_names);
}

TEST(Tree, GetAncestorsForInvalid) {
  models::agglomerations::Tree tree(GetBrGeoNodesResponse());

  std::vector<std::string> ancestor_names;

  for (const auto& ancestor : tree.GetAncestors("invalid")) {
    ancestor_names.push_back(std::string(ancestor->GetName()));
  }
  std::vector<std::string> expected_ancestor_names;
  ASSERT_EQ(ancestor_names, expected_ancestor_names);
  ASSERT_EQ(tree.GetAncestorNames("invalid"), expected_ancestor_names);
}

TEST(Tree, Empty) {
  ASSERT_FALSE(models::agglomerations::Tree(GetBrGeoNodesResponse()).IsEmpty());
  ASSERT_TRUE(models::agglomerations::Tree{}.IsEmpty());
}

TEST(Tree, Size) {
  ASSERT_EQ(models::agglomerations::Tree(GetBrGeoNodesResponse()).GetSize(),
            8u);
  ASSERT_EQ(models::agglomerations::Tree{}.GetSize(), 0u);
}

TEST(Tree, GetTariffZonesRoot) {
  models::agglomerations::Tree tree(GetBrGeoNodesResponse());

  std::vector<std::string> tariff_zones;
  for (auto tariff_zone : tree.GetTariffZones("br_root")) {
    tariff_zones.push_back(std::string(tariff_zone));
  }
  std::vector<std::string> expected_tariff_zones{
      "boryasvo",
      "moscow",
      "vko",
  };
  ASSERT_EQ(tariff_zones, expected_tariff_zones);
}

TEST(Tree, GetTariffZonesInvalid) {
  models::agglomerations::Tree tree(GetBrGeoNodesResponse());
  const auto tariff_zones = tree.GetTariffZones("invalid");
  std::vector<std::string_view> expected_tariff_zones{};
  ASSERT_EQ(tariff_zones, expected_tariff_zones);
}

TEST(Tree, GetResponse) {
  models::agglomerations::Tree tree(GetBrGeoNodesResponse());
  ASSERT_EQ(
      generated::taxi_agglomerations::api::PackToJson(tree.GetResponse()),
      generated::taxi_agglomerations::api::PackToJson(GetBrGeoNodesResponse()));
}

TEST(GeoNode, GetAncestorsInLeaf) {
  models::agglomerations::Tree tree(GetBrGeoNodesResponse());
  const auto node = tree.GetByName("br_moscow_middle_region");
  std::vector<std::string> ancestor_names;

  for (const auto& ancestor : node->GetAncestors()) {
    ancestor_names.push_back(std::string(ancestor->GetName()));
  }
  std::vector<std::string> expected_ancestor_names{
      "br_moscow", "br_moskovskaja_obl", "br_tsentralnyj_fo", "br_russia",
      "br_root",
  };
  ASSERT_EQ(ancestor_names, expected_ancestor_names);
}

TEST(GeoNode, GetDescendantsInCountry) {
  models::agglomerations::Tree tree(GetBrGeoNodesResponse());
  const auto node = tree.GetByName("br_russia");
  std::set<std::string> descendant_names;

  for (const auto& descendant : node->GetDescendants()) {
    descendant_names.insert(std::string(descendant->GetName()));
  }
  std::set<std::string> expected_descendant_names{
      "br_tsentralnyj_fo", "br_moskovskaja_obl",      "br_moscow",
      "br_moscow_adm",     "br_moscow_middle_region",
  };

  ASSERT_EQ(descendant_names, expected_descendant_names);
}

TEST(GeoNode, GetDescendantsInRoot) {
  models::agglomerations::Tree tree(GetBrGeoNodesResponse());
  const auto node = tree.GetByName("br_root");
  std::set<std::string> descendant_names;

  for (const auto& descendant : node->GetDescendants()) {
    descendant_names.insert(std::string(descendant->GetName()));
  }
  std::set<std::string> expected_descendant_names{
      "br_russia",     "br_tsentralnyj_fo", "br_moskovskaja_obl",
      "br_moscow",     "br_moscow_adm",     "br_moscow_middle_region",
      "br_kazakhstan",
  };

  ASSERT_EQ(descendant_names, expected_descendant_names);
}

TEST(GeoNode, GetDescendantsInLeaf) {
  models::agglomerations::Tree tree(GetBrGeoNodesResponse());
  const auto node = tree.GetByName("br_moscow_middle_region");
  std::vector<std::string> descendant_names;

  for (const auto& descendant : node->GetDescendants()) {
    descendant_names.push_back(std::string(descendant->GetName()));
  }
  std::vector<std::string> expected_descendant_names{};
  ASSERT_EQ(descendant_names, expected_descendant_names);
}
