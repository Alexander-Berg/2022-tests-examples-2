#include <gtest/gtest.h>

#include <boost/lexical_cast/bad_lexical_cast.hpp>

#include <common/types.hpp>
#include <common/utils/identifiers.hpp>

#include <fmt/format.h>

namespace identifiers_utils = billing_time_events::utils;

TEST(DocIdFromSubscriptionRefTest, WhenAllGood) {
  auto subscription_ref = ".../.../6";
  auto doc_id =
      identifiers_utils::doc_id::FromSubscriptionRef(subscription_ref);
  ASSERT_EQ(doc_id, 6);
}

TEST(DocIdFromSubscriptionRefTest, ExceptionWhenNoSlash) {
  auto subscription_ref = "incorrect subscription";
  ASSERT_THROW(identifiers_utils::doc_id::FromSubscriptionRef(subscription_ref),
               std::invalid_argument);
}

TEST(DocIdFromSubscriptionRefTest, ExceptionWhenNotInt) {
  auto subscription_ref = ".../.../abc";
  ASSERT_THROW(identifiers_utils::doc_id::FromSubscriptionRef(subscription_ref),
               std::exception);
}

TEST(DocIdFromSubscriptionRefTest, ExceptionWhenNotInt64) {
  auto subscription_ref =
      fmt::format(".../.../{}", std::numeric_limits<uint64_t>::max());
  ASSERT_THROW(identifiers_utils::doc_id::FromSubscriptionRef(subscription_ref),
               std::exception);
}

TEST(DocIdFromSubscriptionRefTest, GoodForMaxInt64) {
  auto subscription_ref =
      fmt::format(".../.../{}", std::numeric_limits<int64_t>::max());
  auto doc_id =
      identifiers_utils::doc_id::FromSubscriptionRef(subscription_ref);
  ASSERT_EQ(doc_id, std::numeric_limits<int64_t>::max());
}
