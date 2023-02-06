#include <eats-adverts-places/auction/ads_only_result.hpp>

#include <gtest/gtest.h>

#include <eats-adverts-places/utils/test.hpp>

namespace eats_adverts_places::auction {

namespace {

using PlaceId = eats_shared::PlaceId;

struct AdsOnlyResultTestCase {
  std::string name{};
  std::vector<models::PlaceAdvert> place_adverts{};
  std::vector<PlaceId> place_ids{};
  std::vector<models::AuctionResultPlace> expected{};
};

}  // namespace

class AdsOnlyResultTest
    : public ::testing::TestWithParam<AdsOnlyResultTestCase> {};

TEST_P(AdsOnlyResultTest, GetPlaces) {
  auto param = GetParam();

  const AdsOnlyResult ads_only_result(param.place_adverts);

  const auto actual = ads_only_result.GetPlaces(std::move(param.place_ids));

  ASSERT_EQ(param.expected, actual) << param.name;
}

std::vector<AdsOnlyResultTestCase> MakeAdsOnlyResultTestCases();

INSTANTIATE_TEST_SUITE_P(AdsOnlyResult, AdsOnlyResultTest,
                         ::testing::ValuesIn(MakeAdsOnlyResultTestCases()),
                         [](const auto& test_case) {
                           return utils::test::GetName(test_case.param);
                         });

std::vector<AdsOnlyResultTestCase> MakeAdsOnlyResultTestCases() {
  return {
      {
          "no adverts",  // name
          {},            // place_adverts
          {},            // place_ids
          {},            // expected
      },
      {
          "no place ids",  // name
          {{
              PlaceId{"1"},      // place_id
              models::Advert{},  // advert
          }},                    // place_adverts
          {},                    // place_ids
          {},                    // expected
      },
      {
          "place ids not in ads",  // name
          {{
              PlaceId{"1"},      // place_id
              models::Advert{},  // advert
          }},                    // place_adverts
          {
              PlaceId{"2"},
              PlaceId{"3"},
          },   // place_ids
          {},  // expected
      },
      {
          "place ids in ads",  // name
          {{
              PlaceId{"1"},      // place_id
              models::Advert{},  // advert
          }},                    // place_adverts
          {
              PlaceId{"1"},
              PlaceId{"2"},
              PlaceId{"3"},
          },  // place_ids
          {{
              PlaceId{"1"},      // place_id
              models::Advert{},  // advert
          }},                    // expected
      },
      {
          "ordered ads",  // name
          {
              {
                  PlaceId{"2"},  // place_id
                  models::Advert{
                      models::ViewUrl{"view_2"},    // view_url
                      models::ClickUrl{"click_2"},  // click_url
                  },                                // advert
              },
              {
                  PlaceId{"1"},  // place_id
                  models::Advert{
                      models::ViewUrl{"view_1"},  // view_url
                      std::nullopt,               // click_url
                  },                              // advert
              },
              {
                  PlaceId{"3"},  // place_id
                  models::Advert{
                      std::nullopt,                 // view_url
                      models::ClickUrl{"click_3"},  // click_url
                  },                                // advert
              },
          },  // place_adverts
          {
              PlaceId{"1"},
              PlaceId{"2"},
              PlaceId{"3"},
          },  // place_ids
          {
              {
                  PlaceId{"2"},  // place_id
                  models::Advert{
                      models::ViewUrl{"view_2"},    // view_url
                      models::ClickUrl{"click_2"},  // click_url
                  },                                // advert
              },
              {
                  PlaceId{"1"},  // place_id
                  models::Advert{
                      models::ViewUrl{"view_1"},  // view_url
                      std::nullopt,               // click_url
                  },                              // advert
              },
              {
                  PlaceId{"3"},  // place_id
                  models::Advert{
                      std::nullopt,                 // view_url
                      models::ClickUrl{"click_3"},  // click_url
                  },                                // advert
              },
          },  // expected
      },
      {
          "ordered ads multiple",  // name
          {
              {
                  PlaceId{"2"},  // place_id
                  models::Advert{
                      models::ViewUrl{"view_2"},    // view_url
                      models::ClickUrl{"click_2"},  // click_url
                  },                                // advert
              },
              {
                  PlaceId{"1"},  // place_id
                  models::Advert{
                      models::ViewUrl{"view_1"},  // view_url
                      std::nullopt,               // click_url
                  },                              // advert
              },
              {
                  PlaceId{"3"},  // place_id
                  models::Advert{
                      std::nullopt,                 // view_url
                      models::ClickUrl{"click_3"},  // click_url
                  },                                // advert
              },
              {
                  PlaceId{"5"},  // place_id
                  models::Advert{
                      models::ViewUrl{"view_5"},    // view_url
                      models::ClickUrl{"click_5"},  // click_url
                  },                                // advert
              },
              {
                  PlaceId{"4"},  // place_id
                  models::Advert{
                      models::ViewUrl{"view_4"},    // view_url
                      models::ClickUrl{"click_4"},  // click_url
                  },                                // advert
              },
              {
                  PlaceId{"6"},  // place_id
                  models::Advert{
                      models::ViewUrl{"view_6"},    // view_url
                      models::ClickUrl{"click_6"},  // click_url
                  },                                // advert
              },
          },  // place_adverts
          {
              PlaceId{"1"},
              PlaceId{"2"},
              PlaceId{"3"},
              PlaceId{"4"},
              PlaceId{"5"},
              PlaceId{"6"},
              PlaceId{"7"},
          },  // place_ids
          {
              {
                  PlaceId{"2"},  // place_id
                  models::Advert{
                      models::ViewUrl{"view_2"},    // view_url
                      models::ClickUrl{"click_2"},  // click_url
                  },                                // advert
              },
              {
                  PlaceId{"1"},  // place_id
                  models::Advert{
                      models::ViewUrl{"view_1"},  // view_url
                      std::nullopt,               // click_url
                  },                              // advert
              },
              {
                  PlaceId{"3"},  // place_id
                  models::Advert{
                      std::nullopt,                 // view_url
                      models::ClickUrl{"click_3"},  // click_url
                  },                                // advert
              },
              {
                  PlaceId{"5"},  // place_id
                  models::Advert{
                      models::ViewUrl{"view_5"},    // view_url
                      models::ClickUrl{"click_5"},  // click_url
                  },                                // advert
              },
              {
                  PlaceId{"4"},  // place_id
                  models::Advert{
                      models::ViewUrl{"view_4"},    // view_url
                      models::ClickUrl{"click_4"},  // click_url
                  },                                // advert
              },
              {
                  PlaceId{"6"},  // place_id
                  models::Advert{
                      models::ViewUrl{"view_6"},    // view_url
                      models::ClickUrl{"click_6"},  // click_url
                  },                                // advert
              },
          },  // expected
      },
  };
}

}  // namespace eats_adverts_places::auction
