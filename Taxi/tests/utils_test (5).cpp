#include <userver/utest/utest.hpp>
#include <utils/get_place_info.hpp>

namespace eats_restapp_marketing::utils {

TEST(Util, UnprocessedPhrases) {
  ASSERT_EQ(ReplaceUnprocessedPhrases("burger king"), "burger king");
  ASSERT_EQ(ReplaceUnprocessedPhrases("burger king!"), "burger king");
  ASSERT_EQ(ReplaceUnprocessedPhrases("ßurgör KING9769"), "urgr KING9769");
}

}  // namespace eats_restapp_marketing::utils
