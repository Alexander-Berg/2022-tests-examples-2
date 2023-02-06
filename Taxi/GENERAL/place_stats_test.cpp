#include "place_stats.hpp"

#include <userver/dump/test_helpers.hpp>

#include <gtest/gtest.h>

namespace eats_catalog::adverts {

auto tie(const AveragePlaceStats& avg) {
  return std::tie(avg.viewed_to_opened, avg.viewed_to_opened_session,
                  avg.viewed_to_ordered, avg.viewed_to_ordered_session,
                  avg.opened_to_ordered, avg.opened_to_ordered_session);
}

bool operator==(const AveragePlaceStats& lhs, const AveragePlaceStats& rhs) {
  return tie(lhs) == tie(rhs);
}

}  // namespace eats_catalog::adverts

namespace eats_catalog::adverts {

TEST(PlaceStatsContainer, ReadWriteCycleEmpty) {
  const PlaceStatsContainer target({}, 1);
  dump::TestWriteReadCycle(target);
}

TEST(PlaceStatsContainer, ReadWriteCycleWithData) {
  std::vector<PlaceStats> place_stats{
      {
          1,    // brand_id
          0.1,  // viewed_to_opened
          0.1,  // viewed_to_opened_sess
          0.1,  // viewed_to_ordered
          0.1,  // viewed_to_ordered_sess
          0.1,  // opened_to_ordered
          0.1,  // opened_to_ordered_sess
      },
      {
          2,    // brand_id
          0.2,  // viewed_to_opened
          0.2,  // viewed_to_opened_sess
          0.2,  // viewed_to_ordered
          0.2,  // viewed_to_ordered_sess
          0.2,  // opened_to_ordered
          0.2,  // opened_to_ordered_sess
      },
      {
          3,    // brand_id
          0.3,  // viewed_to_opened
          0.3,  // viewed_to_opened_sess
          0.3,  // viewed_to_ordered
          0.3,  // viewed_to_ordered_sess
          0.3,  // opened_to_ordered
          0.3,  // opened_to_ordered_sess
      },
  };
  const PlaceStatsContainer target(std::move(place_stats), 1);
  dump::TestWriteReadCycle(target);
}

TEST(PlaceStatsContainer, FindDefault) {
  const PlaceStatsContainer target;
  const auto actual = target.Find(BrandId{1});
  ASSERT_FALSE(actual.has_value());
}

TEST(PlaceStatsContainer, FindEmpty) {
  const PlaceStatsContainer target({}, 1);
  const auto actual = target.Find(BrandId{1});
  ASSERT_FALSE(actual.has_value());
}

TEST(PlaceStatsContainer, FindMissing) {
  const PlaceStatsContainer target({PlaceStats{
                                       1,    // brand_id,
                                       0.1,  // viewed_to_opened
                                       0.1,  // viewed_to_opened_sess
                                       0.1,  // viewed_to_ordered
                                       0.1,  // viewed_to_ordered_sess
                                       0.1,  // opened_to_ordered
                                       0.1,  // opened_to_ordered_sess
                                   }},
                                   1);
  const auto actual = target.Find(BrandId{2});
  ASSERT_FALSE(actual.has_value());
}

TEST(PlaceStatsContainer, FindOK) {
  const BrandId brand_id{1};
  const PlaceStats expected{
      brand_id.GetUnderlying(),  // brand_id
      0.1,                       // viewed_to_opened
      0.1,                       // viewed_to_opened_sess
      0.1,                       // viewed_to_ordered
      0.1,                       // viewed_to_ordered_sess
      0.1,                       // opened_to_ordered
      0.1,                       // opened_to_ordered_sess
  };
  const PlaceStatsContainer target({expected}, 1);
  const auto actual = target.Find(brand_id);
  ASSERT_TRUE(actual.has_value());
  ASSERT_EQ(expected, actual.value());
}

TEST(PlaceStatsContainer, FindCTR) {
  const BrandId brand_id{1};
  const PlaceStats expected{
      brand_id.GetUnderlying(),  // brand_id
      1,                         // viewed_to_opened
      2,                         // viewed_to_opened_sess
      3,                         // viewed_to_ordered
      4,                         // viewed_to_ordered_sess
      5,                         // opened_to_ordered
      6,                         // opened_to_ordered_sess
  };

  const PlaceStatsContainer target({expected}, 1);
  ASSERT_EQ(expected.viewed_to_opened,
            target.FindCTR(brand_id, CTRSource::kViewedToOpened).value());
  ASSERT_EQ(expected.viewed_to_opened_sess,
            target.FindCTR(brand_id, CTRSource::kViewedToOpenedSess).value());

  ASSERT_EQ(expected.viewed_to_ordered,
            target.FindCTR(brand_id, CTRSource::kViewedToOrdered).value());
  ASSERT_EQ(expected.viewed_to_ordered_sess,
            target.FindCTR(brand_id, CTRSource::kViewedToOrderedSess).value());

  ASSERT_EQ(expected.opened_to_ordered,
            target.FindCTR(brand_id, CTRSource::kOpenedToOrdered).value());
  ASSERT_EQ(expected.opened_to_ordered_sess,
            target.FindCTR(brand_id, CTRSource::kOpenedToOrderedSess).value());
}

TEST(PlaceStatsContainer, FindAverageCTREmpty) {
  const PlaceStatsContainer target;

  ASSERT_EQ(0, target.FindAverageCTR(CTRSource::kViewedToOpened));
  ASSERT_EQ(0, target.FindAverageCTR(CTRSource::kViewedToOpenedSess));
  ASSERT_EQ(0, target.FindAverageCTR(CTRSource::kViewedToOrdered));
  ASSERT_EQ(0, target.FindAverageCTR(CTRSource::kViewedToOrderedSess));
  ASSERT_EQ(0, target.FindAverageCTR(CTRSource::kOpenedToOrdered));
  ASSERT_EQ(0, target.FindAverageCTR(CTRSource::kOpenedToOrderedSess));
}

TEST(PlaceStatsContainer, FindAverageCTROK) {
  std::vector<PlaceStats> places_stats{
      {
          1,  // brand_id
          1,  // viewed_to_opened
          2,  // viewed_to_opened_sess
          3,  // viewed_to_ordered
          4,  // viewed_to_ordered_sess
          5,  // opened_to_ordered
          6,  // opened_to_ordered_sess
      },
      {
          2,  // brand_id
          1,  // viewed_to_opened
          2,  // viewed_to_opened_sess
          3,  // viewed_to_ordered
          4,  // viewed_to_ordered_sess
          5,  // opened_to_ordered
          6,  // opened_to_ordered_sess
      },
      {
          3,  // brand_id
          1,  // viewed_to_opened
          2,  // viewed_to_opened_sess
          3,  // viewed_to_ordered
          4,  // viewed_to_ordered_sess
          5,  // opened_to_ordered
          6,  // opened_to_ordered_sess
      },
  };

  const PlaceStatsContainer target(std::move(places_stats), 1);
  ASSERT_EQ(1, target.FindAverageCTR(CTRSource::kViewedToOpened));
  ASSERT_EQ(2, target.FindAverageCTR(CTRSource::kViewedToOpenedSess));
  ASSERT_EQ(3, target.FindAverageCTR(CTRSource::kViewedToOrdered));
  ASSERT_EQ(4, target.FindAverageCTR(CTRSource::kViewedToOrderedSess));
  ASSERT_EQ(5, target.FindAverageCTR(CTRSource::kOpenedToOrdered));
  ASSERT_EQ(6, target.FindAverageCTR(CTRSource::kOpenedToOrderedSess));
}

}  // namespace eats_catalog::adverts
