#include <gtest/gtest.h>

#include <models/replace_policy.hpp>

using namespace models::replace_policy;

namespace {

using Map = std::unordered_map<int, int>;

}  // namespace

TEST(TestReplacePolicy, ReplaceInFuture) {
  const Map existing = {{1, 1}, {2, 2}, {3, 3}, {5, 5}, {6, 6}};
  const Map requested = {{2, 1}, {3, 4}, {4, 4}, {6, 6}};
  const int tags_are_alive = 0;

  const auto& operations = Merge(existing, requested, tags_are_alive);
  const Map append = {{2, 1}, {3, 4}, {4, 4}};
  ASSERT_TRUE(operations.append == append);

  const Map remove = {{1, 1}, {5, 5}};
  ASSERT_TRUE(operations.remove == remove);
}

TEST(TestReplacePolicy, ReplaceCurrent) {
  const Map existing = {{0, 1}, {1, 1}, {2, 2}, {3, 2}, {5, 5}, {6, 6}};
  const Map requested = {{0, 3}, {2, 1}, {3, 4}, {4, 4}, {6, 0}};
  const int tags_live_until_2 = 2;

  const auto operations = Merge(existing, requested, tags_live_until_2);
  const Map append = {{0, 3}, {4, 4}, {3, 4}};
  const Map remove = {{5, 5}, {6, 6}};
  ASSERT_TRUE(operations.append == append);
  ASSERT_TRUE(operations.remove == remove);
}

TEST(TestReplacePolicy, ReplaceOutdated) {
  const Map existing = {{1, 1}, {2, 2}, {3, 3}, {5, 5}, {6, 6}, {7, 7}};
  const Map requested = {{2, 1}, {3, 6}, {4, 4}, {6, 6}, {7, 2}};
  const int tags_are_outdated = 4;

  const auto operations = Merge(existing, requested, tags_are_outdated);
  const Map append = {{3, 6}};
  ASSERT_TRUE(operations.append == append);
  const Map remove = {{5, 5}, {7, 7}};
  ASSERT_TRUE(operations.remove == remove);
}
