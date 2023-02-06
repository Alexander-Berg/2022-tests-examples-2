#include <gtest/gtest.h>

#include <random>

#include <models/boundary_epsilon_envelope.hpp>
#include <models/geoarea.hpp>
#include <models/point_operations.hpp>
#include <models/segment_epsilon_envelope.hpp>

#include <common/test_config.hpp>
#include "utils/geoareas_fixture.hpp"
#include "utils/jsonfixtures.hpp"

class GeoareaContainsPointPreciseAlgoTest : public ::testing::Test {
 public:
  static void SetUpTestCase() {
    const auto geoareas_bson = JSONFixtures::GetFixtureBSON(
        "geoarea_contains_point_precise_algo_unittest/testareas.json");
    all_geoareas_ = GeoareasFixture::LoadFromBSONArray(geoareas_bson);
    std::cout << "areas loaded : " << all_geoareas_.size() << std::endl;
    max_vertexes_geoarea_ = FindMaxPointsGeoarea(all_geoareas_);
  }

 private:
  static std::size_t CountVertexes(const Geoarea::polygon_t& pt) {
    std::size_t inner_total = 0;
    for (const auto& inner : pt.inners()) inner_total += inner.size();
    return inner_total + pt.outer().size();
  };

  static Geoarea::Sptr FindMaxPointsGeoarea(
      const Geoarea::geoarea_dict_t& all_areas) {
    auto itMaxFound = std::max_element(
        all_areas.begin(), all_areas.end(),
        [](const Geoarea::geoarea_dict_t::value_type& area_pair1,
           const Geoarea::geoarea_dict_t::value_type& area_pair2) -> bool {
          return CountVertexes(area_pair1.second->polygon()) <
                 CountVertexes(area_pair2.second->polygon());
        });
    if (itMaxFound == all_areas.end())
      throw std::runtime_error("was unable to find maximum sized geoarea");
    return itMaxFound->second;
  }

 protected:
  const std::size_t points_count_ = 10000;
  static Geoarea::geoarea_dict_t all_geoareas_;
  static Geoarea::Sptr max_vertexes_geoarea_;
};

Geoarea::geoarea_dict_t GeoareaContainsPointPreciseAlgoTest::all_geoareas_;
Geoarea::Sptr GeoareaContainsPointPreciseAlgoTest::max_vertexes_geoarea_;

// check geoarea->contains_point_fast(pt) against etalon call
// geoarea->contains_point(pt) try it 100000 times
TEST_F(GeoareaContainsPointPreciseAlgoTest, testRandomPoints4maxSizedGeoarea) {
  auto geoarea = max_vertexes_geoarea_;
  auto totalEnvelope = geoarea->envelope();

  std::random_device rd;
  std::mt19937 gen(rd());
  std::uniform_real_distribution<> gen_0_coord(
      totalEnvelope.min_corner().get<0>(), totalEnvelope.max_corner().get<0>());
  std::uniform_real_distribution<> gen_1_coord(
      totalEnvelope.min_corner().get<1>(), totalEnvelope.max_corner().get<1>());

  for (std::size_t i = 0; i < points_count_; ++i) {
    Geoarea::point_t pt{gen_0_coord(gen), gen_1_coord(gen)};
    // compare with etalon geoarea->contains_point(pt)
    ASSERT_EQ(geoarea->contains_point(pt), geoarea->contains_point_fast(pt));
    // this old implementation (contains_point_fast_imprecise) most likely will
    // have discrepancies with etalon contains_point on some iteration
    // ASSERT_EQ(geoarea->contains_point(pt),
    // geoarea->contains_point_fast_imprecise(pt));
  }
}

// BoundaryEpsilonEnvelope tests
// testing code that is used internally by Geoarea::contains_point_fast
TEST_F(GeoareaContainsPointPreciseAlgoTest,
       testBoundaryEpsilonEnvelopeFastContains) {
  class GetGeoAreaBoundaryEnvelope : public Geoarea {
   public:
    const geoarea::helpers::BoundaryEpsilonEnvelope&
    getBoundaryEpsilonEnvelope() const {
      return static_cast<const geoarea::helpers::BoundaryEpsilonEnvelope&>(
          *(this->boundary_epsilon_envelope_.get()));
    }

    static const geoarea::helpers::BoundaryEpsilonEnvelope&
    getBoundaryEpsilonEnvelope(Geoarea::Sptr ptrArea) {
      return reinterpret_cast<GetGeoAreaBoundaryEnvelope*>(ptrArea.get())
          ->getBoundaryEpsilonEnvelope();
    }
  };

  auto geoarea = max_vertexes_geoarea_;
  auto total_envelope = geoarea->envelope();

  const geoarea::helpers::BoundaryEpsilonEnvelope& boundary_envelope =
      GetGeoAreaBoundaryEnvelope::getBoundaryEpsilonEnvelope(
          max_vertexes_geoarea_);

  std::random_device rd;
  std::mt19937 gen(rd());
  std::uniform_real_distribution<> gen_0_coord(
      total_envelope.min_corner().get<0>(),
      total_envelope.max_corner().get<0>());
  std::uniform_real_distribution<> gen_1_coord(
      total_envelope.min_corner().get<1>(),
      total_envelope.max_corner().get<1>());

  for (std::size_t i = 0; i < points_count_; ++i) {
    Geoarea::point_t pt{gen_0_coord(gen), gen_1_coord(gen)};
    ASSERT_EQ(boundary_envelope.ContainsPoint(pt),
              boundary_envelope.ContainsPointSlowForCheckOnly(pt));
  }
}

///////////////////////////
// test SegmentEpsilonEnvelope::contains_point function

namespace {
const Geoarea::point_t p1 = {1, 1};
Geoarea::point_t p2 = {125, 105};
double epsilon = 1.0;
double small_step = 0.00001;
}  // namespace

using namespace geoarea::helpers;

struct SegmentEpsilonEnvelopeTestParam {
  Geoarea::point_t pnt;
  bool expected_result;
};

class SegmentEpsilonEnvelopeTest
    : public ::testing::TestWithParam<SegmentEpsilonEnvelopeTestParam> {};

TEST_P(SegmentEpsilonEnvelopeTest, envelope_param) {
  geoarea::helpers::SegmentEpsilonEnvelope env{p1, p2, epsilon};
  ASSERT_EQ(env.ContainsPoint(GetParam().pnt), GetParam().expected_result);
}

INSTANTIATE_TEST_CASE_P(
    pref, SegmentEpsilonEnvelopeTest,
    ::testing::Values(
        SegmentEpsilonEnvelopeTestParam{(p1 + p2) * 0.5, true},

        SegmentEpsilonEnvelopeTestParam{
            p1 + Normalize(Left90(p2 - p1)) * (epsilon + small_step), false},
        SegmentEpsilonEnvelopeTestParam{
            p1 + Normalize(Left90(p2 - p1)) * (epsilon - small_step), true},
        SegmentEpsilonEnvelopeTestParam{
            p1 + Normalize(Right90(p2 - p1)) * (epsilon + small_step), false},
        SegmentEpsilonEnvelopeTestParam{
            p1 + Normalize(Right90(p2 - p1)) * (epsilon - small_step), true},

        SegmentEpsilonEnvelopeTestParam{
            p2 + Normalize(Left90(p2 - p1)) * (epsilon + small_step), false},
        SegmentEpsilonEnvelopeTestParam{
            p2 + Normalize(Left90(p2 - p1)) * (epsilon - small_step), true},
        SegmentEpsilonEnvelopeTestParam{
            p2 + Normalize(Right90(p2 - p1)) * (epsilon + small_step), false},
        SegmentEpsilonEnvelopeTestParam{
            p2 + Normalize(Right90(p2 - p1)) * (epsilon - small_step), true},

        SegmentEpsilonEnvelopeTestParam{
            p1 + (-Normalize(p2 - p1) * (epsilon - small_step)), true},
        SegmentEpsilonEnvelopeTestParam{
            p1 + (-Normalize(p2 - p1) * (epsilon + small_step)), false},

        SegmentEpsilonEnvelopeTestParam{
            p2 + (Normalize(p2 - p1) * (epsilon - small_step)), true},
        SegmentEpsilonEnvelopeTestParam{
            p2 + (Normalize(p2 - p1) * (epsilon + small_step)), false},

        SegmentEpsilonEnvelopeTestParam{
            p1 + (-Normalize(p2 - p1) + Left90(Normalize(p2 - p1))) *
                     (epsilon - small_step),
            true},
        SegmentEpsilonEnvelopeTestParam{
            p1 + (-Normalize(p2 - p1) + Left90(Normalize(p2 - p1))) *
                     (epsilon + small_step),
            false},
        SegmentEpsilonEnvelopeTestParam{
            p1 + (-Normalize(p2 - p1) + Right90(Normalize(p2 - p1))) *
                     (epsilon - small_step),
            true},
        SegmentEpsilonEnvelopeTestParam{
            p1 + (-Normalize(p2 - p1) + Right90(Normalize(p2 - p1))) *
                     (epsilon + small_step),
            false},

        SegmentEpsilonEnvelopeTestParam{
            p2 + (Normalize(p2 - p1) + Left90(Normalize(p2 - p1))) *
                     (epsilon - small_step),
            true},
        SegmentEpsilonEnvelopeTestParam{
            p2 + (Normalize(p2 - p1) + Left90(Normalize(p2 - p1))) *
                     (epsilon + small_step),
            false},
        SegmentEpsilonEnvelopeTestParam{
            p2 + (Normalize(p2 - p1) + Right90(Normalize(p2 - p1))) *
                     (epsilon - small_step),
            true},
        SegmentEpsilonEnvelopeTestParam{
            p2 + (Normalize(p2 - p1) + Right90(Normalize(p2 - p1))) *
                     (epsilon + small_step),
            false}), );
