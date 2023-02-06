#include <gtest/gtest.h>
#include <userver/utest/utest.hpp>
#include <utils/advert.hpp>

namespace eats_restapp_marketing::utils::advert {

namespace {
struct IntersectTestCase {
  std::string name;
  std::vector<models::PlaceId> left;
  std::vector<models::PlaceId> right;
  std::vector<models::PlaceId> expected;
};
}  // namespace

struct IntersectionPlaceIdsSuccessTest
    : ::testing::TestWithParam<std::tuple<IntersectTestCase>> {};

INSTANTIATE_TEST_SUITE_P(
    results, IntersectionPlaceIdsSuccessTest,
    ::testing::Values(
        std::make_tuple(IntersectTestCase{
            "empty intersection",            // name
            std::vector<models::PlaceId>{},  // left
            std::vector<models::PlaceId>{},  // right
            std::vector<models::PlaceId>{}   // expected
        }),
        std::make_tuple(IntersectTestCase{
            "no intersection data",  // name
            std::vector<models::PlaceId>{models::PlaceId{1}, models::PlaceId{2},
                                         models::PlaceId{3}},  // left
            std::vector<models::PlaceId>{models::PlaceId{4}, models::PlaceId{5},
                                         models::PlaceId{6}},  // right
            std::vector<models::PlaceId>{}                     // expected
        }),
        std::make_tuple(IntersectTestCase{
            "intersection with empty vector",  // name
            std::vector<models::PlaceId>{models::PlaceId{1}, models::PlaceId{2},
                                         models::PlaceId{3}},  // left
            std::vector<models::PlaceId>{},                    // right
            std::vector<models::PlaceId>{}                     // expected
        }),
        std::make_tuple(IntersectTestCase{
            "intersection one element",  // name
            std::vector<models::PlaceId>{models::PlaceId{1}, models::PlaceId{2},
                                         models::PlaceId{3}},  // left
            std::vector<models::PlaceId>{models::PlaceId{3}},  // right
            std::vector<models::PlaceId>{models::PlaceId{3}}   // expected
        }),
        std::make_tuple(IntersectTestCase{
            "intersection all element",  // name
            std::vector<models::PlaceId>{models::PlaceId{1}, models::PlaceId{2},
                                         models::PlaceId{3}},  // left
            std::vector<models::PlaceId>{models::PlaceId{1}, models::PlaceId{2},
                                         models::PlaceId{3}},  // right
            std::vector<models::PlaceId>{models::PlaceId{1}, models::PlaceId{2},
                                         models::PlaceId{3}}  // expected
        })));

TEST_P(IntersectionPlaceIdsSuccessTest, success) {
  const auto [test] = GetParam();
  ASSERT_EQ(advert::IntersectionPlaceIds(test.left, test.right), test.expected)
      << test.name;
}

}  // namespace eats_restapp_marketing::utils::advert
