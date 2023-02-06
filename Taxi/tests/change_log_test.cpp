#include <gtest/gtest.h>

#include <models/place_menu_item.hpp>

#include <utils/change_log.hpp>

namespace eats_rest_menu_storage::utils::tests {

namespace {

ChangeLog MakeChangeLog() {
  return ChangeLog{models::PlaceId{1}, defs::internal::change_log::Type::kItem};
}

}  // namespace

TEST(ChangeLog, ChangedNoBefore) {
  auto change_log = MakeChangeLog();

  models::PlaceMenuItem after{};
  after.legacy_id = models::LegacyId{10};

  change_log.Changed(after);

  const auto result = change_log.Extract();
  ASSERT_EQ(result.changed.extra.size(), 1);
  const auto& front = result.changed.extra.begin()->second;
  ASSERT_FALSE(front.before.has_value());
  ASSERT_EQ(front.after.legacy_id, 10);
}

TEST(ChangeLog, ChangedWithBefore) {
  auto change_log = MakeChangeLog();

  models::PlaceMenuItem after{};
  after.legacy_id = models::LegacyId{10};

  models::PlaceMenuItem before{};
  before.legacy_id = models::LegacyId{20};

  change_log.Changed(after, &before);

  const auto result = change_log.Extract();
  ASSERT_EQ(result.changed.extra.size(), 1);
  const auto& front = result.changed.extra.begin()->second;
  ASSERT_TRUE(front.before.has_value());
  ASSERT_EQ(front.after.legacy_id, 10);
  ASSERT_EQ(front.before->legacy_id, 20);
}

TEST(ChangeLog, Unchanged) {
  auto change_log = MakeChangeLog();
  models::PlaceMenuItem after{};
  after.legacy_id = models::LegacyId{10};

  models::PlaceMenuItem before{};
  before.legacy_id = models::LegacyId{20};

  change_log.Unchanged(after, &before);

  const auto result = change_log.Extract();
  ASSERT_TRUE(result.changed.extra.empty());
  ASSERT_EQ(result.unchanged.extra.size(), 1);
  const auto& front = result.unchanged.extra.begin()->second;
  ASSERT_TRUE(front.before.has_value());
  ASSERT_EQ(front.after.legacy_id, 10);
  ASSERT_EQ(front.before->legacy_id, 20);
}

}  // namespace eats_rest_menu_storage::utils::tests
