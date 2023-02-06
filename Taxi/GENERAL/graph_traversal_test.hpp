#pragma once

#include <cstddef>
#include <initializer_list>
#include <memory>
#include <set>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

#include <models/wms/depot_menu.hpp>
#include <models/wms/graph/graph_visitor.hpp>

namespace overlord_catalog::models::wms {

struct Category;
struct Product;

/// @~english
///   @brief
///     DepotMenu is hard to create, so just mock it.
///
/// @~russian
///   @brief
///     DepotMenu слишком сложно конструировать, поэтому имитируем.
struct FakeDepotMenu {
  std::unordered_map<std::string, Product> raw_products;
  std::unordered_map<std::string, DepotMenu::Product> products;
  std::unordered_map<std::string, Category> categories;

  DepotMenu::Category root;
  DepotMenu::ProductIndexByCategoryId products_by_category;
  DepotMenu::CategoryIndexByParentId categories_by_parent;
};

Product MakeProduct(const std::string& id);
Category MakeCategoryWithPath(const std::string& id);

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
    std::initializer_list<std::pair<std::string, std::string>> category_edges);

struct VertexDiscoverer : GraphVisitor {
  TraverseAction Vertex(const DepotMenu::ProductReference& product) {
    ids.emplace_back(product->GetProduct().product_id.GetUnderlying());
    return TraverseAction::kProceed;
  }
  TraverseAction Vertex(const DepotMenu::Category& category) {
    ids.emplace_back(category->category_id.GetUnderlying());
    return TraverseAction::kProceed;
  }

  std::vector<std::string> ids;
};

struct EdgeDiscoverer : GraphVisitor {
  TraverseAction Edge(const DepotMenu::Category& head,
                      const DepotMenu::ProductReference& tail) {
    ids.emplace(head->category_id.GetUnderlying(),
                tail->GetProduct().product_id.GetUnderlying());
    return TraverseAction::kProceed;
  }
  TraverseAction Edge(const DepotMenu::Category& head,
                      const DepotMenu::Category& tail) {
    ids.emplace(head->category_id.GetUnderlying(),
                tail->category_id.GetUnderlying());
    return TraverseAction::kProceed;
  }

  std::multiset<std::pair<std::string, std::string>> ids;
};

struct ExitAfterFirstProductMet : GraphVisitor {
  TraverseAction Vertex(const DepotMenu::ProductReference& product) {
    ids.emplace(product->GetProduct().product_id.GetUnderlying());
    return TraverseAction::kStop;
  }
  TraverseAction Vertex(const DepotMenu::Category& category) {
    ids.emplace(category->category_id.GetUnderlying());
    return TraverseAction::kProceed;
  }

  std::multiset<std::string> ids;
};

struct ExitAfterThreeCategoriesMet : GraphVisitor {
  TraverseAction Vertex(const DepotMenu::ProductReference& product) {
    ids.emplace(product->GetProduct().product_id.GetUnderlying());
    return TraverseAction::kProceed;
  }
  TraverseAction Vertex(const DepotMenu::Category& category) {
    ids.emplace(category->category_id.GetUnderlying());
    if (++categories_met >= 3) return TraverseAction::kStop;
    return TraverseAction::kProceed;
  }

  std::multiset<std::string> ids;
  std::size_t categories_met = 0;
};

struct VertexDisabler : GraphVisitor {
  VertexDisabler(std::initializer_list<std::string> disabled_vertices)
      : disabled_vertices(disabled_vertices) {}

  TraverseAction Vertex(const DepotMenu::ProductReference& product) {
    const auto product_id = product->GetProduct().product_id.GetUnderlying();

    if (disabled_vertices.count(product_id) != 0) {
      return TraverseAction::kSkip;
    } else {
      ids.emplace(product_id);
      return TraverseAction::kProceed;
    }
  }

  TraverseAction Vertex(const DepotMenu::Category& category) {
    const auto category_id = category->category_id.GetUnderlying();
    if (disabled_vertices.count(category_id) != 0) {
      return TraverseAction::kSkip;
    } else {
      ids.emplace(category_id);
      return TraverseAction::kProceed;
    }
  }

  std::set<std::string> disabled_vertices;
  std::multiset<std::string> ids;
};

}  // namespace overlord_catalog::models::wms
