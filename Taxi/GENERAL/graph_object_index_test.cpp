#include <gtest/gtest.h>
#include <graph/graph_object_index.hpp>
#include <graph/tests/graph_fixture.hpp>
#include <graph/tests/print_to.hpp>
#include <graph/types.hpp>
#include <iostream>
#include <random>

namespace graph::test {

namespace {

template <typename V>
void CompareValueAndPosition(const V& val, const PositionOnEdge& pos,
                             const V& cmp_val, const PositionOnEdge& cmp_pos) {
  ASSERT_EQ(cmp_pos.edge_id, pos.edge_id);
  ASSERT_DOUBLE_EQ(cmp_pos.position, pos.position);
  ASSERT_EQ(cmp_val, val);
}

template <typename K, typename V>
struct GraphObjectIndexNoCopy : public GraphObjectIndex<K, V> {
  using GraphObjectIndex<K, V>::GraphObjectIndex;

  GraphObjectIndexNoCopy(const GraphObjectIndexNoCopy&) = delete;
  GraphObjectIndexNoCopy& operator=(const GraphObjectIndexNoCopy&) = delete;
  GraphObjectIndexNoCopy(GraphObjectIndexNoCopy&&) = default;
  GraphObjectIndexNoCopy& operator=(GraphObjectIndexNoCopy&&) = default;
};

static_assert(std::is_move_constructible<
                  GraphObjectIndexNoCopy<std::string, std::string>>::value,
              "GraphObjectIndex must be moveable");
static_assert(std::is_move_assignable<
                  GraphObjectIndexNoCopy<std::string, std::string>>::value,
              "GraphObjectIndex must be moveable");

}  // namespace

struct GraphObjectIndexTester {
  template <class K, class V, class Hash, class KeyEqual>
  static auto GetGraphUuids(const GraphObjectIndex<K, V, Hash, KeyEqual>& index,
                            const K& key) {
    return index.GetGraphUuids(key);
  }

  template <class K, class V, class Hash, class KeyEqual>
  static void CheckConsistency(
      const GraphObjectIndex<K, V, Hash, KeyEqual>& index) {
    // For every record in key->uuids multimap there should be record
    // in graph_object_index_ and record in uuid_key_value_map_
    for (const auto& key_uuid : index.key_uuids_map_) {
      const auto uuid = key_uuid.second;
      const auto& pos = index.graph_object_index_.GetPosition(uuid);
      EXPECT_FALSE(pos.IsUndefined()) << "pos not present for key: \""
                                      << key_uuid.first << "\" uuid: " << uuid;

      auto key_value_it = index.uuid_key_value_map_.find(uuid);
      ASSERT_NE(index.uuid_key_value_map_.end(), key_value_it);
      // check that keys match
      ASSERT_EQ(key_uuid.first, key_value_it->second.key);
    }

    // For every record in uuid->key,value map there should be record
    // in graph_object_index and record in key->uuids map
    for (const auto& uuid_key_value : index.uuid_key_value_map_) {
      const auto uuid = uuid_key_value.first;
      const auto& key = uuid_key_value.second.key;

      // all elements with this key
      auto range = index.key_uuids_map_.equal_range(key);

      // look for one with our uuid
      EXPECT_TRUE(
          std::any_of(range.first, range.second,
                      [uuid](const auto& val) { return val.second == uuid; }))
          << "can't find record for uuid " << uuid
          << " in key->uuid table for key: \"" << key << "\"";
    }
  }
};

using GraphObjectIndexFixture = graph::test::GraphTestFixtureLegacy;

TEST_F(GraphObjectIndexFixture, TestObjectIndexAddEdge) {
  auto graph = Graph();

  ASSERT_NE(nullptr, graph);

  graph::GraphObjectIndex<std::string, std::string> obj_index(*graph);
  GraphObjectIndexTester::CheckConsistency(obj_index);

  // throw, because doesn't allow to set undefined position.
  ASSERT_ANY_THROW(obj_index.Insert("uuid", "test", PositionOnEdge{}));

  const EdgeId kEdgeId{23};
  const PositionOnEdge kPos{kEdgeId, 0.4};

  const std::string kValue{"test"};
  obj_index.Insert("uuid", kValue, kPos);
  GraphObjectIndexTester::CheckConsistency(obj_index);

  const auto& objs = obj_index.GetObjects("uuid");
  ASSERT_EQ(objs.size(), 1ull);

  const auto& pos = objs[0].position;
  const auto& val = objs[0].value;
  CompareValueAndPosition(val, pos, kValue, kPos);
}

TEST_F(GraphObjectIndexFixture, TestObjectIndexAddDriversToEdge) {
  auto graph = Graph();

  ASSERT_NE(nullptr, graph);

  graph::GraphObjectIndex<std::string, std::string> obj_index(*graph);
  GraphObjectIndexTester::CheckConsistency(obj_index);

  const EdgeId kEdgeId{23};
  const PositionOnEdge kPos1{kEdgeId, 0.4};
  const PositionOnEdge kPos2{kEdgeId, 0.6};

  const std::string kValue1{"test1"};
  const std::string kValue2{"test2"};
  obj_index.Insert("uuid", kValue1, {kPos1, kPos2});
  obj_index.Insert("uuid2", kValue2, kPos2);
  GraphObjectIndexTester::CheckConsistency(obj_index);

  const auto& objs = obj_index.GetObjects("uuid");
  ASSERT_EQ(objs.size(), 2ull);

  if (objs[0].position.position == kPos1.position) {
    CompareValueAndPosition(kValue1, kPos1, objs[0].value, objs[0].position);
    CompareValueAndPosition(kValue1, kPos2, objs[1].value, objs[1].position);
  } else {
    CompareValueAndPosition(kValue1, kPos1, objs[1].value, objs[1].position);
    CompareValueAndPosition(kValue1, kPos2, objs[0].value, objs[0].position);
  }

  const auto& objs2 = obj_index.GetObjects("uuid2");
  ASSERT_EQ(objs2.size(), 1ull);
  CompareValueAndPosition(kValue2, kPos2, objs2[0].value, objs2[0].position);

  const auto& objs_on_edge = obj_index.GetObjectsOnEdge(kEdgeId);
  ASSERT_EQ(objs_on_edge.size(), 2ull);
  ASSERT_EQ(objs_on_edge.at("uuid").size(), 2ull);
  ASSERT_EQ(objs_on_edge.at("uuid2").size(), 1ull);
}

TEST_F(GraphObjectIndexFixture, TestObjectIndexAddFromPoint) {
  using ::geometry::lat;
  using ::geometry::lon;
  using ::geometry::Position;
  auto graph = Graph();

  ASSERT_NE(nullptr, graph);

  graph::GraphObjectIndex<std::string, std::string> obj_index(*graph);

  Position target_pos{37.642418 * lon, 55.734999 * lat};
  static const double nearest_max_distance = 100.0;
  // Collect possible edges:
  auto possible_positions =
      graph->NearestEdges(target_pos, ::graph::EdgeAccess::kUnknown,
                          ::graph::EdgeCategory::kFieldRoads,
                          nearest_max_distance * ::geometry::meter,
                          2 /*min count*/, 100 /*max count*/
      );

  std::vector<EdgeId> possible_edges;
  for (const auto& pos : possible_positions) {
    possible_edges.push_back(pos.edge_id);
  }

  const std::string kValue{"test"};
  obj_index.Insert("uuid", kValue, target_pos, nearest_max_distance);
  GraphObjectIndexTester::CheckConsistency(obj_index);

  const auto& objs = obj_index.GetObjects("uuid");
  ASSERT_EQ(objs.size(), 1ull);
  ASSERT_NE(std::find(possible_edges.begin(), possible_edges.end(),
                      objs[0].position.edge_id),
            possible_edges.end());

  // CompareValueAndPosition(kValue, kExpPos, objs[0].value, objs[0].position);
}

TEST_F(GraphObjectIndexFixture, TestObjectIndexAddFromPointsWithReverseEdges) {
  using ::geometry::lat;
  using ::geometry::lon;
  using ::geometry::Position;
  auto graph = Graph();

  ASSERT_NE(nullptr, graph);

  Position target_pos{55.733626 * lat, 37.637036 * lon};
  constexpr double nearest_max_distance = 100.0;
  // Collect possible edges:
  auto possible_positions = graph->NearestEdges(
      target_pos, graph::EdgeAccess::kUnknown, graph::EdgeCategory::kFieldRoads,
      nearest_max_distance * ::geometry::meter, 2u, 2u);
  ASSERT_EQ(2u, possible_positions.size());
  const auto& forward_edge_id = possible_positions.front().edge_id;
  const auto& reverse_edge_id = possible_positions.back().edge_id;
  const auto& optional_reverse_reverse_edge_id =
      graph->GetReverseEdgeId(reverse_edge_id);
  ASSERT_TRUE(optional_reverse_reverse_edge_id);
  const auto& reverse_reverse_edge_id = *optional_reverse_reverse_edge_id;
  ASSERT_EQ(forward_edge_id, reverse_reverse_edge_id);

  ASSERT_EQ(graph::EdgeCategory::kRoads, graph->GetCategory(forward_edge_id));
  ASSERT_EQ(graph::EdgeCategory::kRoads, graph->GetCategory(reverse_edge_id));

  graph::GraphObjectIndex<std::string, std::string> obj_index(*graph);
  const std::string kKey{"uuid"};
  const std::string kValue{"test"};
  const size_t inserted_points_both =
      obj_index.InsertPoints(kKey, kValue, target_pos, nearest_max_distance,
                             {graph::EdgeCategory::kRoads});
  GraphObjectIndexTester::CheckConsistency(obj_index);
  ASSERT_EQ(2ull, inserted_points_both);
  const auto& objs = obj_index.GetObjects(kKey);

  ASSERT_EQ(2ull, objs.size());
  ASSERT_EQ(kValue, objs[0].value);
  ASSERT_EQ(kValue, objs[1].value);
  const std::unordered_set<graph::EdgeId> expected_edges{forward_edge_id,
                                                         reverse_edge_id};
  const std::unordered_set<graph::EdgeId> actual_edges{
      objs[0].position.edge_id, objs[1].position.edge_id};
  ASSERT_EQ(expected_edges, actual_edges);
  ASSERT_NEAR(objs[0].position.position, 1.0 - objs[1].position.position,
              0.001);

  const size_t inserted_points_only_forward =
      obj_index.InsertPoints(kKey, kValue, target_pos, nearest_max_distance,
                             {graph::EdgeCategory::kHighways});
  GraphObjectIndexTester::CheckConsistency(obj_index);
  ASSERT_EQ(1ull, inserted_points_only_forward);

  const size_t inserted_points_none = obj_index.InsertPoints(
      kKey, kValue, {0. * lat, 0. * lon}, nearest_max_distance, {});
  GraphObjectIndexTester::CheckConsistency(obj_index);
  ASSERT_EQ(0ull, inserted_points_none);
}

TEST_F(GraphObjectIndexFixture, TestObjectIndexRemove) {
  auto graph = Graph();

  ASSERT_NE(nullptr, graph);

  graph::GraphObjectIndex<std::string, std::string> obj_index(*graph);

  const unsigned int kEdgeIdVal = 23;
  const EdgeId kEdgeId{kEdgeIdVal};
  const PositionOnEdge kPos1{kEdgeId, 0.4};
  const PositionOnEdge kPos2{kEdgeId, 0.6};
  const PositionOnEdge kPos3{EdgeId{kEdgeIdVal + 1}, 0.6};

  const std::string kValue{"test"};
  obj_index.Insert("uuid", kValue, {kPos1, kPos2});
  obj_index.Insert("uuid", kValue, kPos3);
  GraphObjectIndexTester::CheckConsistency(obj_index);

  const auto& graph_uuids =
      GraphObjectIndexTester::GetGraphUuids(obj_index, std::string{"uuid"});
  auto objs = obj_index.GetObjects("uuid");
  ASSERT_EQ(objs.size(), 3ull);
  ASSERT_EQ(graph_uuids.size(), 3ull);

  obj_index.Remove("uuid");
  GraphObjectIndexTester::CheckConsistency(obj_index);
  objs = obj_index.GetObjects("uuid");
  ASSERT_EQ(objs.size(), 0ull);

  // Check that all objects are also deleted from graph internal index.
  const auto& graph_obj_index = obj_index.GetGraphObjIndex();
  for (const auto& uuid : graph_uuids) {
    ASSERT_EQ(graph_obj_index.GetPosition(uuid).IsUndefined(), true);
  }
}

TEST_F(GraphObjectIndexFixture, TestObjectIndexRemove2) {
  auto graph = Graph();

  ASSERT_NE(nullptr, graph);

  graph::GraphObjectIndex<std::string, std::string> obj_index(*graph);

  const unsigned int kEdgeIdVal = 23;
  const EdgeId kEdgeId{kEdgeIdVal};
  const EdgeId kEdgeId2{kEdgeIdVal + 1};
  const PositionOnEdge kPos1{kEdgeId, 0.4};
  const PositionOnEdge kPos2{kEdgeId, 0.6};
  const PositionOnEdge kPos3{kEdgeId2, 0.6};

  const std::string kValue{"test"};
  obj_index.Insert("uuid", kValue, {kPos1, kPos2});
  obj_index.Insert("uuid", kValue, kPos3);
  GraphObjectIndexTester::CheckConsistency(obj_index);

  const auto& graph_obj_index = obj_index.GetGraphObjIndex();
  const auto& graph_uuids =
      GraphObjectIndexTester::GetGraphUuids(obj_index, std::string{"uuid"});
  auto objs = obj_index.GetObjects("uuid");
  ASSERT_EQ(objs.size(), 3ull);
  ASSERT_EQ(graph_uuids.size(), 3ull);
  ASSERT_EQ(graph_obj_index.GetObjectNum(), 3ull);

  obj_index.Remove("uuid", {kEdgeId});
  GraphObjectIndexTester::CheckConsistency(obj_index);
  objs = obj_index.GetObjects("uuid");
  ASSERT_EQ(objs.size(), 1ull);
  ASSERT_EQ(objs.front().position.edge_id, EdgeId{kEdgeIdVal + 1});

  {
    const auto& graph_uuids =
        GraphObjectIndexTester::GetGraphUuids(obj_index, std::string{"uuid"});
    ASSERT_EQ(graph_obj_index.GetObjectNum(), 1ull);
    ASSERT_EQ(1ull, graph_uuids.size());
    const auto& uuid = graph_uuids.front();
    ASSERT_EQ(kEdgeId2.GetUnderlying(),
              graph_obj_index.GetPosition(uuid).EdgeId);
  }
}

TEST_F(GraphObjectIndexFixture, TestInsertUnique) {
  auto graph = Graph();

  ASSERT_NE(nullptr, graph);

  graph::GraphObjectIndex<std::string, std::string> obj_index(*graph);
  const auto& graph_obj_index = obj_index.GetGraphObjIndex();

  const unsigned int kEdgeIdVal = 23;
  const EdgeId kEdgeId{kEdgeIdVal};
  const PositionOnEdge kPos1{kEdgeId, 0.4};
  const PositionOnEdge kPos2{kEdgeId, 0.6};
  const PositionOnEdge kPos3{EdgeId{kEdgeIdVal + 1}, 0.6};
  const EdgeId kEdgeId3{kEdgeIdVal + 2};
  const PositionOnEdge kPos4{kEdgeId3, 0.6};

  const std::string kValue{"test"};
  obj_index.Insert("uuid", kValue, {kPos1, kPos2});
  obj_index.Insert("uuid", kValue, kPos3);
  GraphObjectIndexTester::CheckConsistency(obj_index);

  EXPECT_EQ(graph_obj_index.GetObjectNum(), 3ull);

  auto objs = obj_index.GetObjects("uuid");
  EXPECT_EQ(objs.size(), 3ull);
  EXPECT_EQ(1, obj_index.GetObjectsOnEdge(kEdgeId).size());
  // one array for key "uuid", 2 elements in this array
  EXPECT_EQ(1, obj_index.GetObjectsOnEdge(kEdgeId).size());
  EXPECT_EQ(2, obj_index.GetObjectsOnEdge(kEdgeId).begin()->second.size());

  obj_index.InsertUnique("uuid", kValue, kPos4);
  GraphObjectIndexTester::CheckConsistency(obj_index);
  EXPECT_EQ(0, obj_index.GetObjectsOnEdge(kEdgeId).size());
  EXPECT_EQ(1, obj_index.GetObjectsOnEdge(kEdgeId3).size());
  EXPECT_EQ(graph_obj_index.GetObjectNum(), 1ull);

  objs = obj_index.GetObjects("uuid");
  ASSERT_EQ(objs.size(), 1ull);
}

class InsertUniqueVector
    : public graph::test::GraphFixturePluginLegacy,
      public ::testing::TestWithParam<std::tuple<int, int>> {
 public:
  static constexpr int kBaseKey = 13;
  static constexpr uint32_t kBaseEdgeId = 23;

  using Index = graph::GraphObjectIndex<int, int>;
  static Index::ObjectPositions Generate(int count) {
    Index::ObjectPositions res;
    for (int i = 0; i < count; ++i) {
      res.push_back(
          {PositionOnEdge{graph::EdgeId(kBaseEdgeId + i), 1.0 / (i + 1)}, i});
    }
    return res;
  }

  static void SetUpTestSuite() {
    graph::test::GraphFixturePluginLegacy::PluginSetUpTestSuite();
  }
  static void TearDownTestSuite() {
    graph::test::GraphFixturePluginLegacy::PluginTearDownTestSuite();
  }
};

TEST_P(InsertUniqueVector, One) {
  const auto [old_count, new_count] = GetParam();

  auto graph = Graph();
  ASSERT_NE(nullptr, graph);

  Index obj_index(*graph);
  const auto& graph_obj_index = obj_index.GetGraphObjIndex();

  for (auto count : {old_count, new_count}) {
    obj_index.InsertUnique(kBaseKey, Generate(count));

    GraphObjectIndexTester::CheckConsistency(obj_index);
    EXPECT_EQ(count, graph_obj_index.GetObjectNum());

    const auto& objs = obj_index.GetObjects(kBaseKey);
    EXPECT_EQ(count, objs.size());

    const auto& edge_objs =
        obj_index.GetObjectsOnEdge(graph::EdgeId(kBaseEdgeId));
    if (count == 0)
      EXPECT_EQ(0, edge_objs.size());
    else
      EXPECT_EQ(1, edge_objs.size());
  }
}

INSTANTIATE_TEST_SUITE_P(GraphObjectIndexFixtureP, InsertUniqueVector,
                         ::testing::Combine(::testing::Values(0, 1, 2, 3, 4),
                                            ::testing::Values(0, 1, 2, 3, 4)));

TEST_F(GraphObjectIndexFixture, AddMultiple) {
  auto graph = Graph();

  ASSERT_NE(nullptr, graph);

  graph::GraphObjectIndex<std::string, std::string> obj_index(*graph);

  const unsigned int kEdgeIdVal = 23;
  const EdgeId kEdgeId{kEdgeIdVal};
  const PositionOnEdge kPos1{kEdgeId, 0.4};
  const PositionOnEdge kPos2{kEdgeId, 0.6};
  const PositionOnEdge kPos3{EdgeId{kEdgeIdVal + 1}, 0.6};
  const PositionOnEdge kPos4{EdgeId{kEdgeIdVal + 2}, 0.6};

  const std::string kValue{"test"};
  obj_index.Insert("uuid", kValue, {kPos1, kPos2, kPos3, kPos4});
  GraphObjectIndexTester::CheckConsistency(obj_index);

  // One container for key "uuid", 2 elements in it
  ASSERT_EQ(1, obj_index.GetObjectsOnEdge(kEdgeId).size());
  EXPECT_EQ(2, obj_index.GetObjectsOnEdge(kEdgeId).begin()->second.size());

  EXPECT_EQ(4, obj_index.GetObjects("uuid").size());
}

TEST_F(GraphObjectIndexFixture, TestObjectIndexRemoveNotAllEdges) {
  auto graph = Graph();

  ASSERT_NE(nullptr, graph);

  graph::GraphObjectIndex<std::string, std::string> obj_index(*graph);
  const auto& graph_obj_index = obj_index.GetGraphObjIndex();

  const unsigned int kEdgeIdVal = 23;
  const EdgeId kEdgeId{kEdgeIdVal};
  const PositionOnEdge kPos1{kEdgeId, 0.4};                 // uuid 0
  const PositionOnEdge kPos2{kEdgeId, 0.6};                 // uuid 1
  const PositionOnEdge kPos3{EdgeId{kEdgeIdVal + 1}, 0.6};  // uuid 2
  const PositionOnEdge kPos4{EdgeId{kEdgeIdVal + 2}, 0.6};  // uuid 3

  const std::string kValue{"test"};
  obj_index.Insert("uuid", kValue, {kPos1, kPos2, kPos3, kPos4});
  GraphObjectIndexTester::CheckConsistency(obj_index);
  ASSERT_EQ(graph_obj_index.GetObjectNum(), 4ull);

  auto objs = obj_index.GetObjects("uuid");
  ASSERT_EQ(objs.size(), 4ull);

  obj_index.Remove("uuid", {kEdgeId, EdgeId{kEdgeIdVal + 2}});
  GraphObjectIndexTester::CheckConsistency(obj_index);
  ASSERT_EQ(graph_obj_index.GetObjectNum(), 1ull);

  objs = obj_index.GetObjects("uuid");
  ASSERT_EQ(1ull, objs.size());
  CompareValueAndPosition(kValue, kPos3, objs[0].value, objs[0].position);
}

TEST_F(GraphObjectIndexFixture, TestCopy) {
  auto graph = Graph();

  ASSERT_NE(nullptr, graph);

  graph::GraphObjectIndex<std::string, std::string> obj_index(*graph);
  const auto& graph_obj_index = obj_index.GetGraphObjIndex();

  const unsigned int kEdgeIdVal = 23;
  const EdgeId kEdgeId{kEdgeIdVal};
  const PositionOnEdge kPos1{kEdgeId, 0.4};                 // uuid 0
  const PositionOnEdge kPos2{kEdgeId, 0.6};                 // uuid 1
  const PositionOnEdge kPos3{EdgeId{kEdgeIdVal + 1}, 0.6};  // uuid 2
  const PositionOnEdge kPos4{EdgeId{kEdgeIdVal + 2}, 0.6};  // uuid 3

  const std::string kValue{"test"};
  obj_index.Insert("uuid", kValue, {kPos1, kPos2, kPos3, kPos4});
  GraphObjectIndexTester::CheckConsistency(obj_index);
  ASSERT_EQ(graph_obj_index.GetObjectNum(), 4ull);

  // make a copy
  auto copy_index{obj_index};
  GraphObjectIndexTester::CheckConsistency(copy_index);
  ASSERT_EQ(graph_obj_index.GetObjectNum(), 4ull);

  EXPECT_EQ(obj_index.ObjectsCount(), copy_index.ObjectsCount());
  EXPECT_EQ(obj_index.PositionsCount(), copy_index.PositionsCount());
}

namespace {
uint32_t Random(uint32_t min, uint32_t max) {
  static std::mt19937_64 rnd_generator{static_cast<unsigned long>(
      std::chrono::system_clock::now().time_since_epoch().count())};
  std::uniform_int_distribution<uint32_t> rnd_distribution(min, max);
  return rnd_distribution(rnd_generator);
}

std::vector<std::string> MakeDrivers(size_t count) {
  std::vector<std::string> ret(count);
  std::generate(ret.begin(), ret.end(),
                [n = 0]() mutable { return "uuid" + std::to_string(n++); });
  return ret;
}

PositionOnEdge MakeRandomPosition(size_t edges_count) {
  auto random =
      Random(0, edges_count - 1);  // closed interval [0, edges_count - 1]
  PositionOnEdge ret;
  ret.edge_id = EdgeId{random};
  ret.position = 0.5;
  return ret;
}

}  // namespace

TEST_F(GraphObjectIndexFixture, TestInsertUnique2) {
  auto graph = Graph();
  ASSERT_NE(nullptr, graph);

  graph::GraphObjectIndex<std::string, std::string> obj_index(*graph);
  const auto& graph_obj_index = obj_index.GetGraphObjIndex();

  const size_t kDriverCount = 100;
  auto driver_uuids = MakeDrivers(kDriverCount);
  for (size_t epoch_count = 0; epoch_count < 10; ++epoch_count) {
    for (const auto& uuid : driver_uuids) {
      obj_index.InsertUnique(uuid, uuid,
                             MakeRandomPosition(graph->GetEdgesCount()));
    }
  }
  ASSERT_EQ(graph_obj_index.GetObjectNum(), kDriverCount);
}

}  // namespace graph::test
