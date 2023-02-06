#include <gtest/gtest.h>

#include "eats-full-text-search-models/utils.hpp"

using namespace eats_full_text_search_models::utils;

TEST(Utils, ToSaasRating) { ASSERT_EQ(ToSaasRating(4.2), 42); }

TEST(Utils, FromSaasRating) { ASSERT_FLOAT_EQ(FromSaasRating(42), 4.2); }
