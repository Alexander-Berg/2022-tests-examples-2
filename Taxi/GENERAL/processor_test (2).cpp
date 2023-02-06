#include <userver/engine/run_in_coro.hpp>
#include <userver/utest/utest.hpp>

#include <models/candidates/waybill/processor.hpp>

namespace {

using models::candidates::waybill::Candidate;
using models::candidates::waybill::Filter;
using models::candidates::waybill::Processor;
using models::geometry::Point;

class DummyFilter : public Filter {
 public:
  explicit DummyFilter(const uint32_t max_score) : max_score_(max_score) {}

  Result Process(const Candidate&, const uint32_t score) const override {
    return score < max_score_ ? Result::kAllow : Result::kDisallow;
  }

 private:
  const uint32_t max_score_;
};

auto MakeMember(const std::string& waybill_id,
                const std::string& candidate_id) {
  auto waybill = std::make_shared<united_dispatch::models::WaybillProposal>();
  waybill->external_ref = waybill_id;

  united_dispatch::models::WaybillCandidate candidate_doc{};
  candidate_doc.info.id = candidate_id;
  waybill->candidate_doc = std::move(candidate_doc);

  return Candidate{Point(1, 1), waybill};
}

auto MakeMember(const std::string& id) { return MakeMember(id, id); }

auto MakeMemberWithPerformer(const std::string& id) {
  auto waybill = std::make_shared<united_dispatch::models::WaybillProposal>();
  waybill->external_ref = id;
  waybill->performer.emplace();
  waybill->performer->id = id;
  return Candidate{Point(1, 1), waybill};
}

auto MakeProcessor(const uint32_t limit, const Filter& filter) {
  Processor::Params params;
  params.limit = limit;
  return Processor(params, filter);
}

}  // namespace

UTEST(WaybillProcessorTest, ZeroLimit) {
  DummyFilter filter(100);

  auto processor = MakeProcessor(0, filter);
  EXPECT_EQ(processor.size(), 0);
  EXPECT_EQ(processor.full(), true);

  processor.Process(MakeMember("1"), 1);
  EXPECT_EQ(processor.size(), 0);
  EXPECT_EQ(processor.full(), true);

  auto results = processor.ExtractResults();
  EXPECT_EQ(results.size(), 0);
}

UTEST(WaybillProcessorTest, Limit) {
  DummyFilter filter(100);

  auto processor = MakeProcessor(3, filter);
  EXPECT_EQ(processor.size(), 0);
  EXPECT_EQ(processor.full(), false);

  processor.Process(MakeMember("1"), 1);
  EXPECT_EQ(processor.size(), 1);
  EXPECT_EQ(processor.full(), false);

  processor.Process(MakeMember("2"), 2);
  EXPECT_EQ(processor.size(), 2);
  EXPECT_EQ(processor.full(), false);

  processor.Process(MakeMember("3"), 3);
  EXPECT_EQ(processor.size(), 3);
  EXPECT_EQ(processor.full(), true);

  processor.Process(MakeMember("4"), 4);
  EXPECT_EQ(processor.size(), 3);
  EXPECT_EQ(processor.full(), true);

  auto results = processor.ExtractResults();
  ASSERT_EQ(results.size(), 3);
  EXPECT_EQ(results[0].waybill->external_ref, "1");
  EXPECT_EQ(results[1].waybill->external_ref, "2");
  EXPECT_EQ(results[2].waybill->external_ref, "3");
}

UTEST(WaybillProcessorTest, Ordering) {
  DummyFilter filter(100);

  auto processor = MakeProcessor(3, filter);

  processor.Process(MakeMember("4"), 4);
  processor.Process(MakeMember("3"), 3);
  processor.Process(MakeMember("2"), 2);
  processor.Process(MakeMember("1"), 1);

  auto results = processor.ExtractResults();
  ASSERT_EQ(results.size(), 3);
  EXPECT_EQ(results[0].waybill->external_ref, "1");
  EXPECT_EQ(results[1].waybill->external_ref, "2");
  EXPECT_EQ(results[2].waybill->external_ref, "3");
}

UTEST(WaybillProcessorTest, Filtering) {
  DummyFilter filter(100);

  auto processor = MakeProcessor(3, filter);

  processor.Process(MakeMember("4"), 4);
  processor.Process(MakeMember("200"), 200);
  processor.Process(MakeMember("2"), 2);

  auto results = processor.ExtractResults();
  ASSERT_EQ(results.size(), 2);
  EXPECT_EQ(results[0].waybill->external_ref, "2");
  EXPECT_EQ(results[1].waybill->external_ref, "4");
}

UTEST(WaybillProcessorTest, Dublicates) {
  DummyFilter filter(100);

  auto processor = MakeProcessor(3, filter);

  processor.Process(MakeMember("4"), 4);
  processor.Process(MakeMember("3"), 3);
  processor.Process(MakeMember("2"), 2);
  processor.Process(MakeMember("1"), 1);
  processor.Process(MakeMember("1"), 1);

  auto results = processor.ExtractResults();
  ASSERT_EQ(results.size(), 3);
  EXPECT_EQ(results[0].waybill->external_ref, "1");
  EXPECT_EQ(results[1].waybill->external_ref, "2");
  EXPECT_EQ(results[2].waybill->external_ref, "3");
}

UTEST(WaybillProcessorTest, PerformersAndCandidates) {
  DummyFilter filter(100);

  auto processor = MakeProcessor(3, filter);

  processor.Process(MakeMemberWithPerformer("1"), 1);
  processor.Process(MakeMember("2"), 2);

  auto results = processor.ExtractResults();

  ASSERT_EQ(results.size(), 2);
  EXPECT_EQ(results[0].waybill->external_ref, "1");
  EXPECT_EQ(results[1].waybill->external_ref, "2");
}

UTEST(WaybillProcessorTest, MultipleWaybillsPerCandidate) {
  DummyFilter filter(100);

  auto processor = MakeProcessor(3, filter);

  processor.Process(MakeMember("4b", "d"), 8);
  processor.Process(MakeMember("4a", "d"), 7);
  processor.Process(MakeMember("3b", "c"), 5);
  processor.Process(MakeMember("3a", "c"), 9);
  processor.Process(MakeMember("2b", "b"), 4);
  processor.Process(MakeMember("2a", "b"), 3);
  processor.Process(MakeMember("1b", "a"), 2);
  processor.Process(MakeMember("1a", "a"), 1);

  auto results = processor.ExtractResults();
  ASSERT_EQ(results.size(), 6);
  EXPECT_EQ(results[0].waybill->external_ref[0], '1');
  EXPECT_EQ(results[1].waybill->external_ref[0], '1');
  EXPECT_EQ(results[2].waybill->external_ref[0], '2');
  EXPECT_EQ(results[3].waybill->external_ref[0], '2');
  EXPECT_EQ(results[4].waybill->external_ref[0], '3');
  EXPECT_EQ(results[5].waybill->external_ref[0], '3');
}
