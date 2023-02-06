#include "graph_traversal_test.hpp"

#include <initializer_list>
#include <memory>
#include <string>
#include <unordered_map>
#include <utility>

#include <models/wms/categories.hpp>
#include <models/wms/depot_menu.hpp>
#include <models/wms/products.hpp>

namespace overlord_catalog::models::wms {

Product MakeProduct(const std::string& id) {
  // TODO de-uglify initializer LAVKABACKEND-1384
  return Product{ProductId{id},
                 {},
                 {},
                 {},
                 {},
                 {},
                 {},
                 {},
                 {},
                 {},
                 {},
                 {},
                 {},
                 {},
                 {},
                 {},
                 {},
                 {},
                 {},
                 {},
                 {},
                 {},
                 {},
                 {},
                 {},
                 {},
                 {},
                 {},
                 {},
                 {},
                 {},
                 {},
                 {},
                 {},
                 {},
                 {},
                 {},
                 {},
                 {},
                 {}};
}

Category MakeCategoryWithPath(const std::string& id) {
  using Interval = datetime::TimeOfDayInterval;
  using Time = Interval::Time;
  using Vector = std::vector<Interval>;
  static const datetime::Timetable kTestTimetable{
      Vector{{Interval::DayType::kEveryday, {Time{"00:00"}, Time{"24:00"}}}}};
  return Category{
      CategoryId{id},  {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {},
      {kTestTimetable}};
}

/// @~english
///   @param root
///     The root category of the resulting graph.
///   @param product_edges
///     The edges from categories to products.
///   @param category_edges
///     The edges between categories.
///
/// @~russian
///   @param root
///     Корневая категория получаемого графа.
///   @param product_edges
///     Рёбра между категориями и продуктами.
///   @param category_edges
///     Рёбра между категориями.
std::unique_ptr<FakeDepotMenu> CreateFakeDepotMenu(
    std::string root,
    std::initializer_list<std::pair<std::string, std::string>> product_edges,
    std::initializer_list<std::pair<std::string, std::string>> category_edges) {
  auto fake_depot_menu = std::make_unique<FakeDepotMenu>();

  fake_depot_menu->categories.emplace(root, MakeCategoryWithPath(root));

  for (const auto& [head, tail] : product_edges) {
    auto raw_product =
        fake_depot_menu->raw_products.emplace(tail, MakeProduct(tail));
    fake_depot_menu->products.emplace(
        tail, DepotMenu::Product(std::addressof(raw_product.first->second), {},
                                 {}, {}, {}, {}));

    fake_depot_menu->categories.emplace(head, MakeCategoryWithPath(head));
  }

  for (const auto& [head, tail] : category_edges) {
    fake_depot_menu->categories.emplace(head, MakeCategoryWithPath(head));
    fake_depot_menu->categories.emplace(tail, MakeCategoryWithPath(tail));
  }

  for (const auto& [head, tail] : product_edges) {
    fake_depot_menu->products_by_category[CategoryId{head}].push_back(
        std::addressof(fake_depot_menu->products.at(tail)));
  }

  for (const auto& [head, tail] : category_edges) {
    fake_depot_menu->categories_by_parent[CategoryId{head}].emplace_back(
        std::addressof(fake_depot_menu->categories.at(tail)));
  }
  for (auto& [id, categories] : fake_depot_menu->categories_by_parent)
    std::sort(
        categories.begin(), categories.end(),
        [](const auto* lhs, const auto* rhs) { return lhs->rank < rhs->rank; });

  fake_depot_menu->root = std::addressof(fake_depot_menu->categories.at(root));

  return fake_depot_menu;
}

}  // namespace overlord_catalog::models::wms
