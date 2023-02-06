#include <dispatch/matching/grocery/scoreboard/filter_chain.hpp>

#include <gtest/gtest.h>

using namespace united_dispatch::matching::grocery::scoreboard;
using namespace models::grocery;

static constexpr reject::Reason kTestReason{"Test reason",
                                            reject::RejectKind::kSingleItem};

struct NeverCalledFilter {};
struct TestFilter {};
struct TestFilterReject {};

struct TestFeatures {
  std::optional<reject::Reason> Filter(NeverCalledFilter) const {
    ADD_FAILURE() << "TestFeatures::Filter(NeverCalledFilter) was called";
    return std::nullopt;
  }

  std::optional<reject::Reason> Filter(TestFilter) const {
    return std::nullopt;
  }

  std::optional<reject::Reason> Filter(TestFilterReject) const {
    return kTestReason;
  }
};

TEST(GroceryFilterChainTest, Basic) {
  const TestFeatures features;

  {
    auto chain = FilterChain{TestFilter{}};
    auto res = chain.Filter(features);

    ASSERT_EQ(std::nullopt, res);
  }

  {
    auto chain = FilterChain{TestFilter{}, TestFilter{}, TestFilter{}};
    auto res = chain.Filter(features);

    ASSERT_EQ(std::nullopt, res);
  }

  {
    auto chain = FilterChain{TestFilterReject{}};
    auto res = chain.Filter(features);

    ASSERT_EQ(kTestReason, res);
  }

  {
    auto chain = FilterChain{TestFilter{}, TestFilter{}, TestFilterReject{},
                             NeverCalledFilter{}};
    auto res = chain.Filter(features);

    ASSERT_EQ(kTestReason, res);
  }
}
