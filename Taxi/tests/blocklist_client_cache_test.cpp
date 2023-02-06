
#include <clients/blocklist/client_mock_base.hpp>

#include "common.hpp"

UTEST(BlocklistClientCacheTest, Sample) {
  blocklist_client::models::BlocklistCache cache;
  cache.UpdatePredicateEvaluator(raw_predicates_map);

  auto block = CreateItem("id_1", {kCarNumber}, {kNumber_1}, {true},
                          kCarNumberPredicate);

  cache.ProcessNewBlocks({block});
  auto blocked_entity =
      BuildKwargsMap(kNumber_1, kCar_1, kPark_1, kUuid_1, kLicense_1);
  auto another_entity =
      BuildKwargsMap(kNumber_2, kCar_1, kPark_1, kUuid_1, kLicense_1);
  EXPECT_EQ(cache.Check(blocked_entity), true);
  EXPECT_EQ(cache.Check(another_entity), false);

  // unblock blocked_entity and check again
  block.data->is_active = false;
  cache.ProcessNewBlocks({block});
  EXPECT_EQ(cache.Check(blocked_entity), false);
  EXPECT_EQ(cache.blocks_size(), 0);
  for (const auto& key_to_blocks : cache.blocks_index())
    EXPECT_EQ(key_to_blocks.second->size(), 0);
}

UTEST(BlocklistClientCacheTest, NotEnoughKwargs) {
  blocklist_client::models::BlocklistCache cache;
  cache.UpdatePredicateEvaluator(raw_predicates_map);

  auto block = CreateItem("id_1", {kCarNumber, kParkId}, {kNumber_1, kPark_1},
                          {true, false}, kParkIdAndCarNumberPredicate);
  cache.ProcessNewBlocks({block});
  auto a_entity =
      BuildKwargsMap(kNumber_1, kCar_1, kPark_2, kUuid_1, kLicense_1);
  auto b_entity =
      BuildKwargsMap(kNumber_2, kCar_1, kPark_1, kUuid_1, kLicense_1);
  auto c_entity =
      BuildKwargsMap(kNumber_1, kCar_1, kPark_1, kUuid_1, kLicense_1);
  // same number but different park - no blocking
  EXPECT_EQ(cache.Check(a_entity), false);
  // different number - no blocking
  EXPECT_EQ(cache.Check(b_entity), false);
  // same number, same park - blocking
  EXPECT_EQ(cache.Check(c_entity), true);
}

UTEST(BlocklistClientCacheTest, FewBlocks) {
  blocklist_client::models::BlocklistCache cache;
  cache.UpdatePredicateEvaluator(raw_predicates_map);

  cache.ProcessNewBlocks(
      {CreateItem("id_2", {kCarNumber}, {kNumber_2}, {true},
                  kCarNumberPredicate),
       CreateItem("id_3", {kCarNumber, kParkId}, {kNumber_2, kPark_1},
                  {true, false}, kParkIdAndCarNumberPredicate),
       CreateItem("id_4", {kCarNumber, kParkId}, {kNumber_1, kPark_1},
                  {true, false}, kParkIdAndCarNumberPredicate)});
  auto same_car_1 =
      BuildKwargsMap(kNumber_2, kCar_1, kEmptyPark, kUuid_1, kLicense_1);
  auto same_car_2 =
      BuildKwargsMap(kNumber_2, kCar_1, kPark_1, kUuid_1, kLicense_1);
  auto same_car_3 =
      BuildKwargsMap(kNumber_2, kCar_1, kPark_2, kUuid_1, kLicense_1);
  EXPECT_EQ(cache.Check(same_car_1), true);
  EXPECT_EQ(cache.Check(same_car_2), true);
  EXPECT_EQ(cache.Check(same_car_3), true);

  auto another_car =
      BuildKwargsMap(kNumber_1, kCar_1, kPark_1, kUuid_1, kLicense_1);
  EXPECT_EQ(cache.Check(another_car), true);
}

TEST(BlocklistClientCacheTest, GetBlockIds) {
  blocklist_client::models::BlocklistCache cache;
  cache.UpdatePredicateEvaluator(raw_predicates_map);
  cache.ProcessNewBlocks(
      {CreateItem("id_1", {kCarNumber}, {kNumber_2}, {true},
                  kCarNumberPredicate),
       CreateItem("id_2", {kCarNumber, kParkId}, {kNumber_2, kPark_1},
                  {true, false}, kParkIdAndCarNumberPredicate),
       CreateItem("id_3", {kCarNumber, kParkId}, {kNumber_1, kPark_1},
                  {true, false}, kParkIdAndCarNumberPredicate)});

  std::vector<std::string> block_ids;
  auto blocked =
      BuildKwargsMap(kNumber_2, kCar_1, kPark_1, kUuid_1, kLicense_1);
  cache.Check(blocked, {}, &block_ids);
  EXPECT_EQ(block_ids.size(), 2);
}

TEST(BlocklistClientCacheTest, DesabledMechanics) {
  blocklist_client::models::BlocklistCache cache;
  cache.UpdatePredicateEvaluator(raw_predicates_map);

  const auto block_1 = CreateItem("id_1", {kCarNumber}, {kNumber_1}, {true},
                                  kCarNumberPredicate);

  auto block_2 = block_1;
  block_2.block_id = "id_2";
  block_2.data->mechanics = "mechanics_disabled_1";
  auto block_3 = block_1;
  block_3.block_id = "id_3";
  auto block_4 = block_1;
  block_4.block_id = "id_4";
  block_4.data->mechanics = "mechanics_disabled_2";
  // add 4 equal blocks, but two with disabled mechanics
  cache.ProcessNewBlocks(
      {block_1, std::move(block_2), std::move(block_3), std::move(block_4)});

  std::vector<std::string> block_ids;
  const auto blocked =
      BuildKwargsMap(kNumber_1, kCar_1, kPark_1, kUuid_1, kLicense_1);
  cache.Check(blocked, {"mechanics_disabled_1", "mechanics_disabled_2"},
              &block_ids);

  // blocks with disabled mechanics must not be
  // denied by filter
  EXPECT_EQ(block_ids.size(), 2);
  std::sort(block_ids.begin(), block_ids.end());
  EXPECT_EQ(block_ids[0], "id_1");
  EXPECT_EQ(block_ids[1], "id_3");
}
