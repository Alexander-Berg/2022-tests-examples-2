#include <clients/blocklist/client_mock_base.hpp>

#include "common.hpp"

#include <userver/cache/statistics_mock.hpp>

namespace {
class MockBlocklistClient : public clients::blocklist::ClientMockBase {
 public:
  std::vector<clients::blocklist::IndexableBlocksItem> blocks;

  clients::blocklist::v1_blocks_updates::get::Response V1BlocksUpdatesGet(
      const clients::blocklist::v1_blocks_updates::get::Request& request,
      const clients::blocklist::CommandControl& /*command_control*/ = {})
      const override {
    int from = 0;
    if (request.last_known_revision)
      from = std::stoi(*request.last_known_revision);
    clients::blocklist::v1_blocks_updates::get::Response res;
    res.blocks = std::vector<clients::blocklist::IndexableBlocksItem>{};
    res.blocks->insert(res.blocks->begin(), blocks.begin() + from,
                       blocks.end());
    res.last_revision = std::to_string(blocks.size());
    return res;
  }

  clients::blocklist::internal_blocklist_v1_predicates::get::Response
  BlocklistV1ApiPredicates(
      const clients::blocklist::CommandControl& /*command_control*/ = {})
      const override {
    clients::blocklist::internal_blocklist_v1_predicates::get::Response res;

    const formats::json::Value condition_1 =
        formats::json::FromString(R"=({"type":"eq","value":"car_number"})=");

    const formats::json::Value condition_2 = formats::json::FromString(
        R"=({"type":"and","value":[{"type":"eq","value":"park_id"},{"type":"eq","value":"car_number"}]})=");

    res.predicates = std::vector<clients::blocklist::PredicateValueInfo>{
        {{kCarNumberPredicate}, {std::move(condition_1)}}};
    res.predicates = std::vector<clients::blocklist::PredicateValueInfo>{
        {{kParkIdAndCarNumberPredicate}, {std::move(condition_2)}}};
    return res;
  }
};

}  // namespace

UTEST(BlocklistClientCacheUpdateTest, Sample) {
  MockBlocklistClient client;
  client.blocks = {CreateItem("block_1", {kCarNumber}, {kNumber_1}, {true},
                              kCarNumberPredicate),
                   CreateItem("block_2", {kCarNumber}, {kNumber_2}, {true},
                              kCarNumberPredicate)};

  blocklist_client::models::BlocklistCache cache;
  cache::UpdateStatisticsScopeMock stats_scope(cache::UpdateType::kFull);
  // ???????????????? 2 ????????????????????, ??????????????????, ?????? ???????????? ??????????
  cache.Update(client, stats_scope.GetScope());
  EXPECT_EQ(cache.cursor(), "2");

  // ???????????????? ?? ???????? ???? ??????????????, ??????????????????, ?????? ???????????? ?????????????? ???? ??????????
  cache.Update(client, stats_scope.GetScope());
  EXPECT_EQ(cache.cursor(), "2");

  client.blocks.push_back(CreateItem("block_3", {kCarNumber}, {kNumber_3},
                                     {true}, kCarNumberPredicate));

  // ???????????????? ?????? ????????????????????, ??????????????????, ?????? ???????????? ??????????????????
  // ??????????????????, ?????? ?????? 3 ???????????????????? ?????????????? ?? ??????
  cache.Update(client, stats_scope.GetScope());
  EXPECT_EQ(cache.cursor(), "3");
  EXPECT_EQ(cache.blocks_size(), 3);

  client.blocks.push_back(CreateItem("block_1", {kCarNumber}, {kNumber_1},
                                     {true}, kCarNumberPredicate, false));

  // ???????????? ????????????????????. ?????????????????? ????????????, ?? ?????? ???? ???????? ???????? 1 ????????????????????
  cache.Update(client, stats_scope.GetScope());
  EXPECT_EQ(cache.cursor(), "4");
  EXPECT_EQ(cache.blocks_size(), 2);

  client.blocks.push_back(CreateItem("block_1", {kCarNumber}, {kNumber_1},
                                     {true}, kCarNumberPredicate));

  client.blocks.push_back(CreateItem("block_1", {kCarNumber}, {kNumber_1},
                                     {true}, kCarNumberPredicate));

  // ???????????????? ???????????????????? ?? ?????????? ?????????????????????????????? ??????????????
  // ?????????????? ???? ?????????? ?????????????? ?? ??????
  cache.Update(client, stats_scope.GetScope());
  EXPECT_EQ(cache.blocks_size(), 3);

  client.blocks.push_back(CreateItem("block_4", {kCarNumber, kParkId},
                                     {kNumber_1, kPark_1}, {true, false},
                                     kParkIdAndCarNumberPredicate));

  cache.Update(client, stats_scope.GetScope());
  // ??????????????????, ?????? ???????????????????? ????????????????????, ???? ?????????????????????????????? ?????????? ???? ??????
  // ????????????????
  EXPECT_EQ(cache.blocks_index().count(
                predicate_evaluator::KwargWrapper::Parse(kParkId)),
            0);
  EXPECT_EQ(cache.blocks_size(), 4);
}
