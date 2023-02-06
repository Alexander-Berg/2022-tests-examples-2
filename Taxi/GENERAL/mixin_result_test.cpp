#include <eats-adverts-places/auction/mixin_result.hpp>

#include <gtest/gtest.h>

#include <eats-adverts-places/utils/test.hpp>

namespace eats_adverts_places::auction {

namespace {

using PlaceId = eats_shared::PlaceId;

constexpr bool kShouldOverwriteEqualPositions = true;
constexpr bool kShouldNotOverwriteEqualPositions =
    !kShouldOverwriteEqualPositions;

struct MixinResultTestCase {
  std::string name{};
  std::vector<models::PlaceAdvert> place_adverts{};
  MixinResultSettings settings{};
  std::vector<PlaceId> place_ids{};
  std::vector<models::AuctionResultPlace> expected{};
};

}  // namespace

class MixinResultTest : public ::testing::TestWithParam<MixinResultTestCase> {};

TEST_P(MixinResultTest, GetPlaces) {
  auto param = GetParam();

  const MixinResult mixin_result(std::move(param.place_adverts),
                                 param.settings);

  const auto actual = mixin_result.GetPlaces(std::move(param.place_ids));

  ASSERT_EQ(param.expected, actual) << param.name;
}

std::vector<MixinResultTestCase> MakeMixinResultTestCases();

INSTANTIATE_TEST_SUITE_P(MixinResult, MixinResultTest,
                         ::testing::ValuesIn(MakeMixinResultTestCases()),
                         [](const auto& test_case) {
                           return utils::test::GetName(test_case.param);
                         });

std::vector<MixinResultTestCase> MakeMixinResultTestCases() {
  return {
      {
          "no place adverts for place_ids",            // name
          {},                                          // place_adverts
          {},                                          // settings
          {PlaceId{"1"}, PlaceId{"2"}, PlaceId{"3"}},  // place_ids
          {
              {
                  PlaceId{"1"},  // place_id
                  std::nullopt,  // advert
              },
              {
                  PlaceId{"2"},  // place_id
                  std::nullopt,  // advert
              },
              {
                  PlaceId{"3"},  // place_id
                  std::nullopt,  // advert
              },

          },  // expected
      },
      {
          "no place adverts",  // name
          {},                  // place_adverts
          {},                  // settings
          {},                  // place_ids
          {},                  // expected
      },
      {
          "no advert positions",  // name
          {
              {
                  eats_shared::PlaceId("1"),  // place_id
                  models::Advert{},           // advert
              },
          },   // place_adverts
          {},  // settings
          {},  // place_ids
          {},  // expected
      },
      {
          "no place ids",  // name
          {
              {
                  eats_shared::PlaceId("1"),  // place_id
                  models::Advert{},           // advert
              },
          },  // place_adverts
          {
              {0, 1, 2, 3},                       // advert_positions
              kShouldNotOverwriteEqualPositions,  // overwrite_equal_position
          },                                      // settings
          {},                                     // place_ids
          {},                                     // expected
      },
      {
          "no suitable place ids",  // name
          {
              {
                  eats_shared::PlaceId("1"),  // place_id
                  models::Advert{},           // advert
              },
          },  // place_adverts
          {
              {0, 1, 2, 3},                       // advert_positions
              kShouldNotOverwriteEqualPositions,  // overwrite_equal_position
          },                                      // settings
          {
              PlaceId{"2"},
              PlaceId{"3"},
          },  // place_ids
          {
              {
                  PlaceId{"2"},  // place_id
                  std::nullopt,  // advert
              },
              {
                  PlaceId{"3"},  // place_id
                  std::nullopt,  // advert
              },
          },  // expected
      },
      {
          "organic dedublicate lesser position",  // name
          {
              {
                  eats_shared::PlaceId("1"),  // place_id
                  models::Advert{},           // advert
              },
          },  // place_adverts
          {
              {1},                                // advert_positions
              kShouldNotOverwriteEqualPositions,  // overwrite_equal_position
          },                                      // settings
          {
              PlaceId{"1"},
              PlaceId{"2"},
              PlaceId{"3"},
          },  // place_ids
          {
              {
                  PlaceId{"1"},  // place_id
                  std::nullopt,  // advert
              },
              {
                  PlaceId{"2"},  // place_id
                  std::nullopt,  // advert
              },
              {
                  PlaceId{"3"},  // place_id
                  std::nullopt,  // advert
              },
          },  // expected
      },
      {
          "organic dedublicate equal position",  // name
          {
              {
                  eats_shared::PlaceId("1"),  // place_id
                  models::Advert{},           // advert
              },
          },  // place_adverts
          {
              {0},                                // advert_positions
              kShouldNotOverwriteEqualPositions,  // overwrite_equal_position
          },                                      // settings
          {
              PlaceId{"1"},
              PlaceId{"2"},
              PlaceId{"3"},
          },  // place_ids
          {
              {
                  PlaceId{"1"},  // place_id
                  std::nullopt,  // advert
              },
              {
                  PlaceId{"2"},  // place_id
                  std::nullopt,  // advert
              },
              {
                  PlaceId{"3"},  // place_id
                  std::nullopt,  // advert
              },
          },  // expected
      },
      {
          "advert dedublicate",  // name
          {
              {
                  eats_shared::PlaceId("1"),  // place_id
                  models::Advert{
                      models::ViewUrl{"view_1"},    // view_url
                      models::ClickUrl{"click_1"},  // click_url
                  },                                // advert
              },
          },  // place_adverts
          {
              {0},                                // advert_positions
              kShouldNotOverwriteEqualPositions,  // overwrite_equal_position
          },                                      // settings
          {
              PlaceId{"2"},
              PlaceId{"1"},
              PlaceId{"3"},
          },  // place_ids
          {
              {
                  PlaceId{"1"},  // place_id
                  models::Advert{
                      models::ViewUrl{"view_1"},    // view_url
                      models::ClickUrl{"click_1"},  // click_url
                  },                                // advert
              },
              {
                  PlaceId{"2"},  // place_id
                  std::nullopt,  // advert
              },
              {
                  PlaceId{"3"},  // place_id
                  std::nullopt,  // advert
              },
          },  // expected
      },
      {
          "do not advertise places when there is not enough positions",  // name
          {
              {
                  eats_shared::PlaceId("1"),  // place_id
                  models::Advert{
                      models::ViewUrl{"view_1"},    // view_url
                      models::ClickUrl{"click_1"},  // click_url
                  },                                // advert
              },
              {
                  eats_shared::PlaceId("2"),  // place_id
                  models::Advert{
                      models::ViewUrl{"view_2"},    // view_url
                      models::ClickUrl{"click_2"},  // click_url
                  },                                // advert
              },
              {
                  eats_shared::PlaceId("3"),  // place_id
                  models::Advert{
                      models::ViewUrl{"view_3"},    // view_url
                      models::ClickUrl{"click_3"},  // click_url
                  },                                // advert
              },
          },  // place_adverts
          {
              {0},                                // advert_positions
              kShouldNotOverwriteEqualPositions,  // overwrite_equal_position
          },                                      // settings
          {
              PlaceId{"2"},
              PlaceId{"1"},
              PlaceId{"3"},
          },  // place_ids
          {
              {
                  PlaceId{"1"},  // place_id
                  models::Advert{
                      models::ViewUrl{"view_1"},    // view_url
                      models::ClickUrl{"click_1"},  // click_url
                  },                                // advert
              },
              {
                  PlaceId{"2"},  // place_id
                  std::nullopt,  // advert
              },
              {
                  PlaceId{"3"},  // place_id
                  std::nullopt,  // advert
              },
          },  // expected
      },
  };
}

}  // namespace eats_adverts_places::auction
