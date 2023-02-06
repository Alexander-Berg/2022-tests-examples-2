#include "breadth_first_search.hpp"

#include <userver/utest/utest.hpp>

#include <models/wms/graph/graph_traversal_test.hpp>

#include <initializer_list>
#include <set>
#include <string>
#include <unordered_map>
#include <utility>

namespace overlord_catalog::models::wms {

// Каждая вершина менее глубокого слоя посещается раньше каждой вершины более
// глубокого
TEST(Graph_BreadthFirstSearch, is_really_breadth_first_search) {
  const auto fake_depot_menu = CreateFakeDepotMenu("c0", {{}},
                                                   {{"c3", "c7"},
                                                    {"c1", "c3"},
                                                    {"c3", "c8"},
                                                    {"c2", "c4"},
                                                    {"c2", "c5"},
                                                    {"c0", "c1"},
                                                    {"c0", "c2"},
                                                    {"c1", "c4"}});
  const auto graph = DepotMenuSubgraph(fake_depot_menu->root,
                                       fake_depot_menu->products_by_category,
                                       fake_depot_menu->categories_by_parent);

  const auto discovered = BreadthFirstSearch(graph, VertexDiscoverer{});

  const auto position_of = [&discovered](auto x) {
    return std::find(discovered.ids.begin(), discovered.ids.end(), x);
  };

  ASSERT_TRUE(position_of("c0") < position_of("c1"));
  ASSERT_TRUE(position_of("c0") < position_of("c2"));
  ASSERT_TRUE(position_of("c0") < position_of("c3"));
  ASSERT_TRUE(position_of("c0") < position_of("c4"));
  ASSERT_TRUE(position_of("c0") < position_of("c5"));
  ASSERT_TRUE(position_of("c0") < position_of("c7"));
  ASSERT_TRUE(position_of("c0") < position_of("c8"));

  ASSERT_TRUE(position_of("c1") < position_of("c3"));
  ASSERT_TRUE(position_of("c1") < position_of("c4"));
  ASSERT_TRUE(position_of("c1") < position_of("c5"));
  ASSERT_TRUE(position_of("c1") < position_of("c7"));
  ASSERT_TRUE(position_of("c1") < position_of("c8"));

  ASSERT_TRUE(position_of("c2") < position_of("c3"));
  ASSERT_TRUE(position_of("c2") < position_of("c4"));
  ASSERT_TRUE(position_of("c2") < position_of("c5"));
  ASSERT_TRUE(position_of("c2") < position_of("c7"));
  ASSERT_TRUE(position_of("c2") < position_of("c8"));

  ASSERT_TRUE(position_of("c3") < position_of("c7"));
  ASSERT_TRUE(position_of("c3") < position_of("c8"));

  ASSERT_TRUE(position_of("c4") < position_of("c7"));
  ASSERT_TRUE(position_of("c4") < position_of("c8"));

  ASSERT_TRUE(position_of("c5") < position_of("c7"));
  ASSERT_TRUE(position_of("c5") < position_of("c8"));
}

}  // namespace overlord_catalog::models::wms
