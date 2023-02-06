#include <gtest/gtest.h>

#include "etag_data.hpp"

TEST(EtagData, Encode) {
  models::v2::ModeEtag mode_etag{1};
  models::v2::OfferedModeEtag offered_mode_etag{1};
  models::v2::StateEtag state_etag{1};

  ASSERT_EQ(mode_etag.Encode(), "\"27DkPbkRfOa5Y9L6\"");
  ASSERT_EQ(offered_mode_etag.Encode(), "\"Q8J0yelOh2dER7OY\"");
  ASSERT_EQ(state_etag.Encode(), "\"2Q5xmbmQijboKM7W\"");
}

TEST(EtagData, Decode) {
  const auto& mode_etag = models::v2::ModeEtag::Decode("\"27DkPbkRfOa5Y9L6\"");
  const auto& offered_mode_etag =
      models::v2::OfferedModeEtag::Decode("\"Q8J0yelOh2dER7OY\"");
  const auto& state_etag =
      models::v2::StateEtag::Decode("\"2Q5xmbmQijboKM7W\"");

  ASSERT_TRUE(mode_etag && mode_etag->revision == 1);
  ASSERT_TRUE(offered_mode_etag && offered_mode_etag->revision == 1);
  ASSERT_TRUE(state_etag && state_etag->revision == 1);

  ASSERT_FALSE(models::v2::OfferedModeEtag::Decode("\"27DkPbkRfOa5Y9L6\""));
  ASSERT_FALSE(models::v2::StateEtag::Decode("\"Q8J0yelOh2dER7OY\""));
  ASSERT_FALSE(models::v2::ModeEtag::Decode("\"2Q5xmbmQijboKM7W\""));
}
