#include <userver/utest/utest.hpp>

#include <userver/formats/json/serialize_container.hpp>
#include <userver/formats/json/value_builder.hpp>

#include <lookup-ordering/processors/processor.hpp>

#include <lookup-ordering/assessors/infrastructure/approximate.hpp>
#include <lookup-ordering/assessors/test/bonus.hpp>
#include <lookup-ordering/assessors/test/fetch_bonus.hpp>
#include <lookup-ordering/assessors/test/fetch_penalty.hpp>
#include <lookup-ordering/assessors/test/penalty.hpp>
#include <lookup-ordering/factories/meta_factory.hpp>
#include <lookup-ordering/models/serialize.hpp>

namespace oatest = lookup_ordering::assessors::test;  // only for test assessors
namespace oainfra =
    lookup_ordering::assessors::infrastructure;  // infra factory
namespace oainfo = lookup_ordering::assessors::info;
using lookup_ordering::models::Candidate;
using lookup_ordering::models::ScoredCandidate;
using std::chrono::seconds;

namespace lookup_ordering::models {
bool operator==(const ScoredCandidate& c1, const ScoredCandidate& c2) {
  return (c1.id == c2.id) && (c1.score == c2.score) &&
         (c1.penalty == c2.penalty);
}

bool operator!=(const ScoredCandidate& c1, const ScoredCandidate& c2) {
  return !(c1 == c2);
}
}  // namespace lookup_ordering::models

TEST(ProcessorTest, UnscoredComparision) {
  const ScoredCandidate c1{"c1"};
  const ScoredCandidate c2{"c2"};
  const ScoredCandidate c3{"c2"};

  ASSERT_NE(c1, c2);
  ASSERT_EQ(c2, c3);
}

TEST(ProcessorTest, ScoredComparision) {
  const ScoredCandidate c1_100{"c1", 100, 0};
  const ScoredCandidate c1_200{"c1", 200, 0};
  const ScoredCandidate c2_100{"c2", 100, 0};
  const ScoredCandidate c2_200{"c2", 100, 0};

  ASSERT_EQ(c1_100, c1_100);
  ASSERT_NE(c1_100, c1_200);
  ASSERT_NE(c1_100, c2_100);
  ASSERT_NE(c1_200, c2_200);
  ASSERT_EQ(c2_200, c2_200);
}

struct ProcessorTestParams {
  std::vector<Candidate> candidates;
  std::vector<ScoredCandidate> result;
};

class ProcessorTest : public ::testing::TestWithParam<ProcessorTestParams> {};

const std::string cid_1 = "candidate_1";
const std::string cid_2 = "candidate_2";
const std::string cid_3 = "candidate_3";
const std::string cid_4 = "candidate_4";

UTEST_P_MT(ProcessorTest, Values, 2) {
  const ProcessorTestParams& values = GetParam();
  lookup_ordering::factories::MetaFactory factory({
      std::make_shared<oatest::FetchBonusFactory>(),
      std::make_shared<oatest::FetchPenaltyFactory>(),
      std::make_shared<oatest::BonusFactory>(),
      std::make_shared<oatest::PenaltyFactory>(),
      std::make_shared<oainfra::ApproximateFactory>(),
  });

  formats::json::ValueBuilder params(formats::json::Type::kObject);
  params["id"] = "order-id";
  params["allowed_classes"] = std::vector<std::string>{"econom"};
  params["request"]["source"]["geopoint"] = std::vector<double>{39.602, 52.569};

  lookup_ordering::processors::Processor processor(
      factory.Create({oainfo::kInfraApproximate.name}, params.ExtractValue()));

  std::vector<ScoredCandidate> result;
  EXPECT_NO_THROW(result = processor.SortCandidates(values.candidates));
  EXPECT_EQ(result.size(), values.candidates.size());
  EXPECT_EQ(result.size(), values.result.size());
  EXPECT_EQ(result, values.result);
}

INSTANTIATE_UTEST_SUITE_P(
    prefix, ProcessorTest,
    ::testing::Values(
        ProcessorTestParams{std::vector<Candidate>{},
                            std::vector<ScoredCandidate>{}},
        ProcessorTestParams{
            std::vector<Candidate>{
                {cid_1, {seconds(400), 1000}, {}},
                {cid_2, {seconds(200), 600}, {}},
            },
            std::vector<ScoredCandidate>{{cid_2, 200, 0}, {cid_1, 400, 0}}},
        ProcessorTestParams{std::vector<Candidate>{
                                {cid_1, {seconds(400), 1000}, {}},
                                {cid_2, {seconds(100), 400, true}, {}},
                                {cid_3, {seconds(200), 600}, {}},
                                {cid_4, {seconds(300), 800}, {}},
                            },
                            std::vector<ScoredCandidate>{{cid_3, 200, 0},
                                                         {cid_4, 300, 0},
                                                         {cid_1, 400, 0},
                                                         {cid_2, 100, 100}}}));
