#include "depth_first_search.hpp"

#include <userver/utest/utest.hpp>

#include <models/wms/graph/graph_traversal_test.hpp>

#include <algorithm>
#include <memory>
#include <set>
#include <string>
#include <utility>

namespace overlord_catalog::models::wms {

// Заходит в каждую вершину графа ровно один раз.
TEST(Graph_DepthFirstSearch, visits_every_vertex_exactly_once) {
  // Корень: c0
  // c0 -> c1
  // c0 -> p1, c0 -> p2
  // c1 -> p1, c1 -> p2
  const auto fake_depot_menu = CreateFakeDepotMenu(
      "c0", {{"c0", "p1"}, {"c0", "p2"}, {"c1", "p1"}, {"c1", "p2"}},
      {{"c0", "c1"}});
  const auto graph = DepotMenuSubgraph(fake_depot_menu->root,
                                       fake_depot_menu->products_by_category,
                                       fake_depot_menu->categories_by_parent);

  const auto discovered = DepthFirstSearch(graph, VertexDiscoverer{});

  ASSERT_TRUE((std::multiset<std::string>(discovered.ids.begin(),
                                          discovered.ids.end()) ==
               std::multiset<std::string>{"c0", "c1", "p1", "p2"}));
}

// Проходит по каждому ребру графа ровно один раз.
TEST(Graph_DepthFirstSearch, visits_every_edge_exactly_once) {
  // Корень: c0
  // c0 -> c1
  // c0 -> p1, c0 -> p2
  // c1 -> p1, c1 -> p2
  const auto fake_depot_menu = CreateFakeDepotMenu(
      "c0", {{"c0", "p1"}, {"c0", "p2"}, {"c1", "p1"}, {"c1", "p2"}},
      {{"c0", "c1"}});
  const auto graph = DepotMenuSubgraph(fake_depot_menu->root,
                                       fake_depot_menu->products_by_category,
                                       fake_depot_menu->categories_by_parent);

  const auto discovered = DepthFirstSearch(graph, EdgeDiscoverer{});

  ASSERT_TRUE(
      (discovered.ids ==
       std::multiset<std::pair<std::string, std::string>>{{"c0", "c1"},
                                                          {"c0", "p1"},
                                                          {"c0", "p2"},
                                                          {"c1", "p1"},
                                                          {"c1", "p2"}}));
}

// Возможен ранний выход из поиска
TEST(Graph_DepthFirstSearch, early_exit_is_possible) {
  const auto fake_depot_menu =
      CreateFakeDepotMenu("c0",
                          {{"c0", "p1"},
                           {"c0", "p2"},
                           {"c1", "p1"},
                           {"c1", "p2"},
                           {"c2", "p3"},
                           {"c2", "p4"},
                           {"c3", "p5"}},
                          {{"c0", "c1"}, {"c1", "c2"}, {"c2", "c3"}});
  const auto graph = DepotMenuSubgraph(fake_depot_menu->root,
                                       fake_depot_menu->products_by_category,
                                       fake_depot_menu->categories_by_parent);

  const auto discovered1 = DepthFirstSearch(graph, ExitAfterFirstProductMet{});
  ASSERT_TRUE((discovered1.ids == std::multiset<std::string>{"c0", "p1"}));

  const auto discovered2 =
      DepthFirstSearch(graph, ExitAfterThreeCategoriesMet{});
  ASSERT_TRUE((discovered2.ids ==
               std::multiset<std::string>{"c0", "c1", "c2", "p1", "p2"}));
}

// Максимальную глубину поиска можно ограничить.
TEST(Graph_DepthFirstSearch, search_depth_may_be_limited) {
  const auto fake_depot_menu = CreateFakeDepotMenu(
      "c0",
      {{"c0", "p1"}, {"c1", "p1"}, {"c2", "p2"}, {"c3", "p3"}, {"c4", "p4"}},
      {{"c0", "c1"}, {"c1", "c2"}, {"c2", "c3"}, {"c3", "c4"}});
  const auto graph = DepotMenuSubgraph(fake_depot_menu->root,
                                       fake_depot_menu->products_by_category,
                                       fake_depot_menu->categories_by_parent);

  const auto discovered1 = DepthFirstSearch(graph, VertexDiscoverer{}, 3);
  ASSERT_TRUE((std::multiset<std::string>(discovered1.ids.begin(),
                                          discovered1.ids.end()) ==
               std::multiset<std::string>{"c0", "c1", "p1", "c2"}));
}

// Нулевая максимальная глубина — это отсутствие поиска.
TEST(Graph_DepthFirstSearch, zero_depth_search_traverses_nothing) {
  const auto fake_depot_menu = CreateFakeDepotMenu(
      "c0",
      {{"c0", "p1"}, {"c1", "p1"}, {"c2", "p2"}, {"c3", "p3"}, {"c4", "p4"}},
      {{"c0", "c1"}, {"c1", "c2"}, {"c2", "c3"}, {"c3", "c4"}});
  const auto graph = DepotMenuSubgraph(fake_depot_menu->root,
                                       fake_depot_menu->products_by_category,
                                       fake_depot_menu->categories_by_parent);

  const auto discovered1 = DepthFirstSearch(graph, VertexDiscoverer{}, 0);
  ASSERT_TRUE(discovered1.ids.empty());
}

// При ограничении глубины все ветви будут пройдены.
TEST(Graph_DepthFirstSearch, all_branches_are_traversed_if_depth_is_limited) {
  const auto fake_depot_menu = CreateFakeDepotMenu("c0", {},
                                                   {{"c0", "c1"},
                                                    {"c0", "c2"},
                                                    {"c1", "c3"},
                                                    {"c1", "c4"},
                                                    {"c2", "c5"},
                                                    {"c2", "c6"},
                                                    {"c3", "c7"},
                                                    {"c3", "c8"},
                                                    {"c4", "c9"},
                                                    {"c4", "c10"},
                                                    {"c5", "c11"},
                                                    {"c5", "c12"},
                                                    {"c6", "c13"},
                                                    {"c6", "c14"}});
  const auto graph = DepotMenuSubgraph(fake_depot_menu->root,
                                       fake_depot_menu->products_by_category,
                                       fake_depot_menu->categories_by_parent);

  const auto discovered1 = DepthFirstSearch(graph, VertexDiscoverer{}, 3);
  ASSERT_TRUE(
      (std::multiset<std::string>(discovered1.ids.begin(),
                                  discovered1.ids.end()) ==
       std::multiset<std::string>{"c0", "c1", "c2", "c3", "c4", "c5", "c6"}));
}

// Можно начинать поиск с любой заданной вершины.
TEST(Graph_DepthFirstSearch, can_search_starting_from_an_arbitrary_vertex) {
  const auto fake_depot_menu = CreateFakeDepotMenu(
      "c0",
      {{"c0", "p0"}, {"c1", "p1"}, {"c2", "p2"}, {"c3", "p3"}, {"c4", "p4"}},
      {{"c0", "c1"}, {"c0", "c2"}, {"c1", "c3"}, {"c1", "c4"}});
  const auto graph = DepotMenuSubgraph(fake_depot_menu->root,
                                       fake_depot_menu->products_by_category,
                                       fake_depot_menu->categories_by_parent);
  const auto search_root = MakeCategoryWithPath("c1");

  const auto discovered1 =
      DepthFirstSearch(graph, std::addressof(search_root), VertexDiscoverer{});
  ASSERT_TRUE((std::multiset<std::string>(discovered1.ids.begin(),
                                          discovered1.ids.end()) ==
               std::multiset<std::string>{"c1", "p1", "c3", "p3", "c4", "p4"}));
}

// Выключенная вершина выключает весь подграф, растущий из неё.
TEST(Graph_DepthFirstSearch, vertices_can_be_filtered_out) {
  const auto fake_depot_menu = CreateFakeDepotMenu("c0",
                                                   {{"c0", "p0"},
                                                    {"c1", "p1"},
                                                    {"c2", "p2"},
                                                    {"c3", "p3"},
                                                    {"c4", "p4"},
                                                    {"c5", "p5"},
                                                    {"c6", "p6"},
                                                    {"c7", "p7"},
                                                    {"c8", "p8"},
                                                    {"c9", "p9"},
                                                    {"c10", "p10"},
                                                    {"c11", "p11"},
                                                    {"c12", "p12"},
                                                    {"c13", "p13"},
                                                    {"c14", "p14"}},
                                                   {{"c0", "c1"},
                                                    {"c0", "c2"},
                                                    {"c1", "c3"},
                                                    {"c1", "c4"},
                                                    {"c2", "c5"},
                                                    {"c2", "c6"},
                                                    {"c3", "c7"},
                                                    {"c3", "c8"},
                                                    {"c4", "c9"},
                                                    {"c4", "c10"},
                                                    {"c5", "c11"},
                                                    {"c5", "c12"},
                                                    {"c6", "c13"},
                                                    {"c6", "c14"}});
  const auto graph = DepotMenuSubgraph(fake_depot_menu->root,
                                       fake_depot_menu->products_by_category,
                                       fake_depot_menu->categories_by_parent);

  const auto discovered =
      DepthFirstSearch(graph, VertexDisabler{"c1", "c5", "p13"});
  ASSERT_TRUE((discovered.ids ==
               std::multiset<std::string>{"c0", "p0", "c2", "p2", "c6", "p6",
                                          "c13", "c14", "p14"}));
}

// Если вершина U посещена раньше V, то любой потомок U будет посещён раньше
// любого потомка V.
TEST(Graph_DepthFirstSearch, is_really_depth_first_search) {
  const auto fake_depot_menu = CreateFakeDepotMenu("c0", {{}},
                                                   {{"c3", "c7"},
                                                    {"c1", "c3"},
                                                    {"c3", "c8"},
                                                    {"c2", "c4"},
                                                    {"c2", "c5"},
                                                    {"c0", "c1"},
                                                    {"c0", "c2"},
                                                    {"c1", "c4"},
                                                    {"c2", "c6"},
                                                    {"c6", "c9"}});
  const auto graph = DepotMenuSubgraph(fake_depot_menu->root,
                                       fake_depot_menu->products_by_category,
                                       fake_depot_menu->categories_by_parent);

  const auto discovered = DepthFirstSearch(graph, VertexDiscoverer{});

  const auto position_of = [&discovered](std::string x) {
    return std::find(discovered.ids.begin(), discovered.ids.end(), x) -
           discovered.ids.begin();
  };

  const auto c1_is_less_than_c2 = position_of("c1") < position_of("c2");

  ASSERT_TRUE((position_of("c3") < position_of("c2")) == c1_is_less_than_c2);
  ASSERT_TRUE((position_of("c4") < position_of("c2")) == c1_is_less_than_c2);
  ASSERT_TRUE((position_of("c7") < position_of("c2")) == c1_is_less_than_c2);
  ASSERT_TRUE((position_of("c8") < position_of("c2")) == c1_is_less_than_c2);

  ASSERT_TRUE((position_of("c3") < position_of("c5")) == c1_is_less_than_c2);
  ASSERT_TRUE((position_of("c4") < position_of("c5")) == c1_is_less_than_c2);
  ASSERT_TRUE((position_of("c7") < position_of("c5")) == c1_is_less_than_c2);
  ASSERT_TRUE((position_of("c8") < position_of("c5")) == c1_is_less_than_c2);
}

}  // namespace overlord_catalog::models::wms
