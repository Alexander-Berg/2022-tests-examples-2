#include <userver/engine/run_in_coro.hpp>
#include <userver/utest/utest.hpp>

#include <models/candidates/waybill/geoindex.hpp>
#include <models/united_dispatch/waybill.hpp>

namespace {

using models::candidates::waybill::Candidate;
using models::candidates::waybill::Filter;
using models::candidates::waybill::GeoIndex;
using models::candidates::waybill::Processor;
using models::geometry::Point;

auto MakeWaybill(const std::string& id) {
  auto waybill = std::make_shared<united_dispatch::models::WaybillProposal>();
  waybill->external_ref = id;

  united_dispatch::models::WaybillCandidate candidate_doc{};
  candidate_doc.info.id = id;
  waybill->candidate_doc = std::move(candidate_doc);

  return waybill;
}

class WaybillGeoIndexTest : public ::testing::Test {
 protected:
  void SetUp() override {
    std::vector<Candidate> candidates = {
        {Point(92.865575, 55.986885), MakeWaybill("id1")},
        {Point(39.051504, 45.033745), MakeWaybill("id2")},
        {Point(30.370960, 60.050888), MakeWaybill("id3")},
        {Point(30.206501, 59.999286), MakeWaybill("id4")},
        {Point(24.876888, 59.445591), MakeWaybill("id5")},
        {Point(37.811739, 55.324163), MakeWaybill("id6")},
        {Point(39.539579, 52.627610), MakeWaybill("id7")},
        {Point(24.151080, 56.880285), MakeWaybill("id8")},
        {Point(30.322031, 59.955284), MakeWaybill("id9")},
        {Point(30.515912, 59.831577), MakeWaybill("id10")},
        {Point(83.080449, 54.991660), MakeWaybill("id11")},
        {Point(44.459404, 40.189564), MakeWaybill("id12")},
        {Point(44.524996, 40.191471), MakeWaybill("id13")},
        {Point(37.735815, 55.910961), MakeWaybill("id14")},
        {Point(49.109904, 55.819350), MakeWaybill("id15")},
        {Point(37.647127, 55.769408), MakeWaybill("id16")},
        {Point(30.386680, 59.924346), MakeWaybill("id17")},
        {Point(24.735324, 59.425072), MakeWaybill("id18")},
        {Point(39.905697, 59.247612), MakeWaybill("id19")},
        {Point(92.827186, 55.981922), MakeWaybill("id20")},
        {Point(20.559154, 54.731014), MakeWaybill("id21")},
        {Point(40.094509, 47.418810), MakeWaybill("id22")},
        {Point(82.979266, 54.992008), MakeWaybill("id23")},
        {Point(37.332883, 55.692754), MakeWaybill("id24")},
        {Point(44.490443, 40.019954), MakeWaybill("id25")},
        {Point(60.543896, 56.823917), MakeWaybill("id26")},
        {Point(37.685597, 55.878708), MakeWaybill("id27")},
        {Point(65.545306, 57.148598), MakeWaybill("id28")},
        {Point(47.283096, 56.106177), MakeWaybill("id29")},
        {Point(82.596553, 49.947420), MakeWaybill("id30")},
        {Point(30.290262, 59.827178), MakeWaybill("id31")},
        {Point(37.713778, 55.655304), MakeWaybill("id32")},
        {Point(76.963387, 43.238302), MakeWaybill("id33")}};
    geoindex_ = std::make_shared<GeoIndex>(std::move(candidates));
    search_point_ = Point(37.603439, 55.731470);  // Gorky park
  }

 public:
  std::shared_ptr<GeoIndex> geoindex_;
  Point search_point_;
};

class DummyFilter : public Filter {
 public:
  Result Process(const Candidate&, const uint32_t) const override {
    return Result::kAllow;
  }
};

auto MakeProcessor(const uint32_t limit, const Filter& filter) {
  Processor::Params params;
  params.limit = limit;
  return Processor(params, filter);
}

}  // namespace

UTEST_F(WaybillGeoIndexTest, ZeroDistance) {
  DummyFilter filter;

  auto processor = MakeProcessor(100, filter);

  GeoIndex::Params params;
  params.position = search_point_;
  params.max_distance = 0;

  geoindex_->Search(params, processor);
  EXPECT_EQ(processor.size(), 0);
}

UTEST_F(WaybillGeoIndexTest, ShortDistance) {
  DummyFilter filter;

  auto processor = MakeProcessor(100, filter);

  GeoIndex::Params params;
  params.position = search_point_;
  params.max_distance = 12000;

  geoindex_->Search(params, processor);

  auto results = processor.ExtractResults();
  ASSERT_EQ(results.size(), 2);
  EXPECT_EQ(results[0].position, Point(37.647127, 55.769408));
  EXPECT_EQ(results[1].position, Point(37.713778, 55.655304));
}

UTEST_F(WaybillGeoIndexTest, LongDistance) {
  DummyFilter filter;

  auto processor = MakeProcessor(100, filter);

  GeoIndex::Params params;
  params.position = search_point_;
  params.max_distance = 10000000;

  geoindex_->Search(params, processor);
  ASSERT_EQ(processor.size(), 33);
}
