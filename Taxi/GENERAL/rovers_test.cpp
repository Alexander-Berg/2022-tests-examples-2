#include <userver/utest/utest.hpp>

#include <filters/efficiency/fetch_tags/fetch_tags.hpp>
#include <filters/infrastructure/fetch_transport_type/fetch_transport_type.hpp>

#include <filters/logistic/rovers/rovers.hpp>

using namespace candidates::filters;
using namespace candidates::filters::efficiency;
using namespace candidates::filters::infrastructure;
using namespace candidates::filters::logistic;
using contractor_transport::models::TransportType;
using tags::models::IdsVec;

const candidates::filters::FilterInfo kEmptyInfo;
const TagId kRoverTagId = 0;

struct TestCase {
  TransportType transport;
  bool use_tag;
  bool has_tag;
  bool allow;
};

class RoversParametric : public ::testing::TestWithParam<TestCase> {};

TEST_P(RoversParametric, TestRovers) {
  auto params = GetParam();

  logistic::Rovers filter(
      kEmptyInfo,
      params.use_tag ? std::make_optional<TagId>(kRoverTagId) : std::nullopt);

  Context context;
  FetchTransportType::Set(context, params.transport);
  FetchTags::Set(context, params.has_tag ? IdsVec{kRoverTagId} : IdsVec{});

  EXPECT_EQ(filter.Process({}, context),
            (params.allow ? Result::kAllow : Result::kDisallow));
}

INSTANTIATE_TEST_SUITE_P(
    RoversTest, RoversParametric,
    ::testing::Values(TestCase{TransportType::kRover, false, false, false},
                      TestCase{TransportType::kRover, true, false, false},
                      TestCase{TransportType::kRover, false, true, false},
                      TestCase{TransportType::kRover, true, true, false},
                      TestCase{TransportType::kCar, false, false, true},
                      TestCase{TransportType::kCar, true, false, true},
                      TestCase{TransportType::kCar, false, true, true},
                      TestCase{TransportType::kCar, true, true, false}));
