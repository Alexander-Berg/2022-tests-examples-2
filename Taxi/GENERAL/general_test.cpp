#include <userver/utest/utest.hpp>

#include <userver/engine/sleep.hpp>
#include <userver/utils/async.hpp>

#include <candidates/filters/statistics.hpp>
#include <candidates/filters/test/dummy.hpp>
#include <candidates/filters/test/sleep.hpp>
#include <candidates/filters/test/sleep_info.hpp>
#include <candidates/processors/general/general.hpp>
#include <candidates/result_storages/dummy/dummy.hpp>

using GeneralProcessor = candidates::processors::General;
using DummyStorage = candidates::result_storages::Dummy;
using candidates::processors::FilterChain;
using models::geometry::Point;

namespace cf = candidates::filters;
namespace cft = candidates::filters::test;

static const cf::FilterInfo kEmptyInfo;

UTEST_MT(GeneralProcessor, SimpleChain, 2) {
  cf::Statistics stats;
  // Allow all
  {
    std::vector<std::unique_ptr<cf::Filter>> filters;
    filters.push_back(std::make_unique<cft::AllowAll>(kEmptyInfo));
    const FilterChain& filter_chain(std::move(filters));
    DummyStorage storage;
    GeneralProcessor processor(filter_chain, storage, stats);

    processor.SearchCallback({Point(), "id1"}, cf::Context(1));
    processor.Finish();

    const auto& result = storage.Get();
    ASSERT_EQ(result.size(), 1);
  }
  // Disallow all
  {
    std::vector<std::unique_ptr<cf::Filter>> filters;
    filters.push_back(std::make_unique<cft::AllowAll>(kEmptyInfo));
    filters.push_back(std::make_unique<cft::DisallowAll>(kEmptyInfo));
    const FilterChain& filter_chain(std::move(filters));
    DummyStorage storage;
    GeneralProcessor processor(filter_chain, storage, stats);

    processor.SearchCallback({Point(), "id1"}, cf::Context(1));
    processor.Finish();

    const auto& result = storage.Get();
    ASSERT_EQ(result.size(), 0);
  }
}

UTEST_MT(GeneralProcessor, MemberOrder, 2) {
  std::vector<std::unique_ptr<cf::Filter>> filters;
  filters.push_back(std::make_unique<cft::AllowAll>(kEmptyInfo));
  const FilterChain& filter_chain(std::move(filters));
  cf::Statistics stats;
  DummyStorage storage;
  GeneralProcessor processor(filter_chain, storage, stats);
  const std::vector<std::pair<candidates::GeoMember, uint32_t>> members = {
      {{Point(), "id1"}, 10}, {{Point(), "id2"}, 4}, {{Point(), "id3"}, 5},
      {{Point(), "id4"}, 11}, {{Point(), "id5"}, 6},
  };
  for (const auto& p : members) {
    processor.SearchCallback(p.first, cf::Context(p.second));
  }
  processor.Finish();

  const auto& result = storage.Get();
  ASSERT_EQ(result.size(), members.size());
  for (size_t i = 0; i < result.size(); ++i) {
    EXPECT_EQ(result[i].context.score, members[i].second);
    EXPECT_EQ(result[i].member.id, members[i].first.id);
  }
}

namespace candidates::filters::test {

class SleepCheck : public Filter {
 public:
  static constexpr const char* kName = "test/sleep-check";

  using Filter::Filter;

  Result Process(const GeoMember&, Context& context) const override {
    return Sleep::IsFinished(context) ? Result::kAllow : Result::kDisallow;
  }
};

const FilterInfo kLocalSleepInfo = {
    cft::info::kSleep.name, {SleepCheck::kName}, {}, false, {}};

const FilterInfo kLocalSleepCheckInfo = {
    SleepCheck::kName, {cft::info::kSleep.name}, {}, false, {}};

}  // namespace candidates::filters::test

UTEST_MT(GeneralProcessor, FilterDependencies, 2) {
  std::vector<std::unique_ptr<cf::Filter>> filters;
  filters.push_back(std::make_unique<cft::Sleep>(
      cft::kLocalSleepInfo, std::chrono::milliseconds{100}));
  filters.push_back(
      std::make_unique<cft::SleepCheck>(cft::kLocalSleepCheckInfo));
  const FilterChain& filter_chain(std::move(filters));
  cf::Statistics stats;
  DummyStorage storage;
  GeneralProcessor processor(filter_chain, storage, stats);

  processor.SearchCallback({Point(), "id1"}, cf::Context(1));
  processor.Finish();

  const auto& result = storage.Get();
  ASSERT_EQ(result.size(), 1);
  EXPECT_EQ(result[0].member.id, std::string("id1"));
}
