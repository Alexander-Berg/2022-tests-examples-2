#include <gtest/gtest.h>

#include <candidates/filters/test/dummy.hpp>

#include "satisfy.hpp"

namespace cf = candidates::filters;
using candidates::processors::FilterChain;
using candidates::satisfy_storages::FilterResult;
using candidates::satisfy_storages::FiltersResults;
using candidates::satisfy_storages::Satisfy;

using ReasonsMap = std::unordered_map<std::string, std::vector<std::string>>;

TEST(SatisfyStorage, DisallowReasons) {
  cf::FilterInfo f1{"f1", {}, {}, false, {}};
  cf::FilterInfo f2{"f2", {}, {}, false, {}};
  cf::FilterInfo f3{"f3", {}, {}, false, {}};
  std::vector<std::unique_ptr<cf::Filter>> filters;
  filters.push_back(std::make_unique<cf::test::AllowAll>(f1));
  filters.push_back(std::make_unique<cf::test::AllowAll>(f2));
  filters.push_back(std::make_unique<cf::test::AllowAll>(f3));
  FilterChain chain(std::move(filters));
  Satisfy storage(chain);
  {
    FiltersResults results;
    results.push_back(
        FilterResult{FilterResult::State::kOk, cf::Result::kDisallow});
    results.push_back(
        FilterResult{FilterResult::State::kOk, cf::Result::kAllow});
    results.push_back(
        FilterResult{FilterResult::State::kOk, cf::Result::kAllow});
    storage.Add({{}, "id1"}, cf::Context{}, results);
  }
  {
    FiltersResults results;
    results.push_back(
        FilterResult{FilterResult::State::kOk, cf::Result::kDisallow});
    results.push_back(
        FilterResult{FilterResult::State::kOk, cf::Result::kAllow});
    results.push_back(
        FilterResult{FilterResult::State::kOk, cf::Result::kDisallow});
    cf::Context context;
    context.need_details = true;
    context.AddDetail("f3", "id2");
    storage.Add({{}, "id2"}, std::move(context), results);
  }
  {
    FiltersResults results;
    results.push_back(
        FilterResult{FilterResult::State::kOk, cf::Result::kDisallow});
    results.push_back(
        FilterResult{FilterResult::State::kOk, cf::Result::kAllow});
    results.push_back(
        FilterResult{FilterResult::State::kOk, cf::Result::kDisallow});
    cf::Context context;
    context.need_details = true;
    context.AddDetail("f1", "id3_1");
    context.AddDetail("f1", "id3_2");
    context.AddDetail("f3", "id3_3");
    storage.Add({{}, "id3"}, std::move(context), results);
  }

  auto results = storage.Extract();
  ASSERT_EQ(results.size(), 3);

  auto& result1 = results[0];
  EXPECT_EQ(result1.member.id, "id1");
  EXPECT_EQ(result1.reasons, ReasonsMap({{"f1", {}}}));
  EXPECT_EQ(result1.ExtractDetails(), ReasonsMap());

  auto& result2 = results[1];
  EXPECT_EQ(result2.member.id, "id2");
  EXPECT_EQ(result2.reasons, ReasonsMap({{"f1", {}}, {"f3", {}}}));
  EXPECT_EQ(result2.ExtractDetails(), ReasonsMap({{"f3", {"id2"}}}));

  auto& result3 = results[2];
  EXPECT_EQ(result3.member.id, "id3");
  EXPECT_EQ(result3.reasons, ReasonsMap({{"f1", {}}, {"f3", {}}}));
  EXPECT_EQ(result3.ExtractDetails(),
            ReasonsMap({{"f1", {"id3_1", "id3_2"}}, {"f3", {"id3_3"}}}));
}
