#include <eats-adverts-places/auction/strong_indexes_result.hpp>

#include <iostream>

#include <fmt/format.h>
#include <gtest/gtest.h>

#include <eats-adverts-places/utils/test.hpp>

namespace eats_adverts_places::models {

std::ostream& operator<<(std::ostream& dst, const AuctionResultPlace& place) {
  dst << place.place_id.GetUnderlying();
  return dst;
}

std::ostream& operator<<(std::ostream& dst,
                         const std::vector<AuctionResultPlace>& places) {
  for (const auto& place : places) {
    dst << "[" << place << "] ";
  }
  return dst;
}

}  // namespace eats_adverts_places::models

namespace eats_adverts_places::auction {

namespace {

::testing::AssertionResult AssertAreEqual(
    const char* m_expr, const char* n_expr,
    const std::vector<models::AuctionResultPlace>& lhs,
    const std::vector<models::AuctionResultPlace>& rhs) {
  if (lhs.size() != rhs.size()) {
    return ::testing::AssertionFailure()
           << m_expr << " and " << n_expr << " (" << lhs << " and " << rhs
           << ") has different sizes";
  }

  for (size_t i = 0; i < lhs.size(); i++) {
    const auto& left = lhs[i];
    const auto& right = rhs[i];
    if (left != right) {
      return ::testing::AssertionFailure()
             << m_expr << " and " << n_expr << " (" << lhs << " and " << rhs
             << ") differs at position [" << std::to_string(i) << "]";
    }
  }

  return ::testing::AssertionSuccess();
}

using PlaceId = eats_shared::PlaceId;

struct StrongIndexesResultTestCase {
  std::string name{};
  std::vector<models::PlaceAdvert> place_adverts{};
  std::set<size_t> indexes{};
  std::vector<PlaceId> place_ids{};
  std::vector<models::AuctionResultPlace> expected{};
};

class StrongIndexesResultTest
    : public ::testing::TestWithParam<StrongIndexesResultTestCase> {};

models::Advert MakeAdvert(const PlaceId& place_id) {
  return {
      models::ViewUrl(fmt::format("/view/{}", place_id.GetUnderlying())),
      models::ClickUrl(fmt::format("/click/{}", place_id.GetUnderlying())),
  };
}

models::PlaceAdvert MakePlaceAdvert(const PlaceId& place_id) {
  return {
      place_id,              // place_id
      MakeAdvert(place_id),  // advert
  };
}

models::AuctionResultPlace MakeResultPlace(const PlaceId& place_id,
                                           bool with_ads) {
  return {
      place_id,  // place_id
      with_ads ? std::optional(MakeAdvert(place_id)) : std::nullopt,  // advert
  };
}

}  // namespace

TEST_P(StrongIndexesResultTest, GetPlaces) {
  auto test_param = GetParam();

  const StrongIndexesResult target(std::move(test_param.place_adverts),
                                   test_param.indexes);
  const auto actual = target.GetPlaces(std::move(test_param.place_ids));
  EXPECT_PRED_FORMAT2(AssertAreEqual, test_param.expected, actual);
}

std::vector<StrongIndexesResultTestCase> MakeStrongIndexesResultTestCases();

INSTANTIATE_TEST_SUITE_P(
    StrongIndexesResult, StrongIndexesResultTest,
    ::testing::ValuesIn(MakeStrongIndexesResultTestCases()),
    [](const auto& test_case) {
      return utils::test::GetName(test_case.param);
    });

std::vector<StrongIndexesResultTestCase> MakeStrongIndexesResultTestCases() {
  return {
      {
          "no place adverts",            // name
          {},                            // place_adverts
          {0, 1, 2, 3},                  // indexes
          {PlaceId("1"), PlaceId("2")},  // place_ids
          {
              MakeResultPlace(PlaceId("1"), /*with_advert*/ false),
              MakeResultPlace(PlaceId("2"), /*with_advert*/ false),
          },  // expected
      },
      {
          "no indexes",                     // name
          {MakePlaceAdvert(PlaceId("1"))},  // place_adverts
          {},                               // indexes
          {PlaceId("1"), PlaceId("2")},     // place_ids
          {
              MakeResultPlace(PlaceId("1"), /*with_advert*/ false),
              MakeResultPlace(PlaceId("2"), /*with_advert*/ false),
          },  // expected
      },
      {
          "no place ids",                   // name
          {MakePlaceAdvert(PlaceId("1"))},  // place_adverts
          {1, 2, 3},                        // indexes
          {},                               // place_ids
          {},                               // expected
      },
      {
          "set on positions",  // name
          {
              MakePlaceAdvert(PlaceId("1")),
              MakePlaceAdvert(PlaceId("2")),
              MakePlaceAdvert(PlaceId("3")),
          },          // place_adverts
          {0, 1, 2},  // indexes
          {
              PlaceId("3"),
              PlaceId("2"),
              PlaceId("1"),
          },  // place_ids
          {
              MakeResultPlace(PlaceId("1"), /*with_advert*/ true),
              MakeResultPlace(PlaceId("2"), /*with_advert*/ true),
              MakeResultPlace(PlaceId("3"), /*with_advert*/ true),
          },  // expected
      },
      {
          "set on even positions",  // name
          {
              MakePlaceAdvert(PlaceId("1")),
              MakePlaceAdvert(PlaceId("2")),
              MakePlaceAdvert(PlaceId("3")),
          },          // place_adverts
          {0, 2, 4},  // indexes
          {
              PlaceId("5"),
              PlaceId("4"),
              PlaceId("3"),
              PlaceId("2"),
              PlaceId("1"),
          },  // place_ids
          {
              MakeResultPlace(PlaceId("1"), /*with_advert*/ true),
              MakeResultPlace(PlaceId("5"), /*with_advert*/ false),
              MakeResultPlace(PlaceId("2"), /*with_advert*/ true),
              MakeResultPlace(PlaceId("4"), /*with_advert*/ false),
              MakeResultPlace(PlaceId("3"), /*with_advert*/ true),
          },  // expected
      },
      {
          "positions out of range",  // name
          {
              MakePlaceAdvert(PlaceId("1")),
              MakePlaceAdvert(PlaceId("2")),
              MakePlaceAdvert(PlaceId("3")),
          },                         // place_adverts
          {10, 11, 12, 13, 14, 15},  // indexes
          {
              PlaceId("5"),
              PlaceId("4"),
              PlaceId("3"),
              PlaceId("2"),
              PlaceId("1"),
          },  // place_ids
          {
              MakeResultPlace(PlaceId("5"), /*with_advert*/ false),
              MakeResultPlace(PlaceId("4"), /*with_advert*/ false),
              MakeResultPlace(PlaceId("3"), /*with_advert*/ false),
              MakeResultPlace(PlaceId("2"), /*with_advert*/ false),
              MakeResultPlace(PlaceId("1"), /*with_advert*/ false),
          },  // expected
      },
      {
          "no adverts for missing indexes",  // name
          {
              MakePlaceAdvert(PlaceId("1")),
              MakePlaceAdvert(PlaceId("2")),
              MakePlaceAdvert(PlaceId("3")),
          },          // place_adverts
          {3, 4, 5},  // indexes
          {
              PlaceId("5"),
              PlaceId("4"),
              PlaceId("3"),
              PlaceId("2"),
              PlaceId("1"),
          },  // place_ids
          {
              MakeResultPlace(PlaceId("5"), /*with_advert*/ false),
              MakeResultPlace(PlaceId("4"), /*with_advert*/ false),
              MakeResultPlace(PlaceId("3"), /*with_advert*/ false),
              MakeResultPlace(PlaceId("1"), /*with_advert*/ true),
              MakeResultPlace(PlaceId("2"), /*with_advert*/ true),
          },  // expected
      },
  };
}

}  // namespace eats_adverts_places::auction
