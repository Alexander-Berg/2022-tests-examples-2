#include "translations.hpp"

#include <gtest/gtest.h>
#include <models/translations.hpp>

namespace tr = models::reposition::translations;

TEST(Translations, ModeKeysAutoregistrationTest) {
  const auto& mode_keys = components::Translations::GetModeKeys();
  ASSERT_FALSE(mode_keys.empty());
  ASSERT_TRUE(mode_keys.count(tr::ChangeAlert::kSuffix));
  ASSERT_TRUE(mode_keys.count(tr::ChangeAlertTitle::kSuffix));
  ASSERT_TRUE(mode_keys.count(tr::SubName::kSuffix));
  ASSERT_TRUE(mode_keys.count(tr::Title::kSuffix));
  ASSERT_TRUE(mode_keys.count(tr::TextHeader::kSuffix));
  ASSERT_TRUE(mode_keys.count(tr::TextDayCountLimit::kSuffix));
  ASSERT_TRUE(mode_keys.count(tr::TextDayDurationLimit::kSuffix));
  ASSERT_TRUE(mode_keys.count(tr::TextWeekCountLimit::kSuffix));
  ASSERT_TRUE(mode_keys.count(tr::TextWeekDurationLimit::kSuffix));
  ASSERT_TRUE(mode_keys.count(tr::LimitsDayTitle::kSuffix));
  ASSERT_TRUE(mode_keys.count(tr::LimitsWeekTitle::kSuffix));
  ASSERT_TRUE(mode_keys.count(tr::LimitsDayCountRemains::kSuffix));
  ASSERT_TRUE(mode_keys.count(tr::LimitsDayDurationRemains::kSuffix));
  ASSERT_TRUE(mode_keys.count(tr::LimitsWeekCountRemains::kSuffix));
  ASSERT_TRUE(mode_keys.count(tr::LimitsWeekDurationRemains::kSuffix));
  ASSERT_TRUE(mode_keys.count(tr::LimitsNextChangeDate::kSuffix));
  ASSERT_TRUE(mode_keys.count(tr::LimitsNextChangeDateTitle::kSuffix));
  ASSERT_TRUE(mode_keys.count(tr::DayUsagesCountExceeded::kSuffix));
  ASSERT_TRUE(mode_keys.count(tr::DayUsagesDurationExceeded::kSuffix));
  ASSERT_TRUE(mode_keys.count(tr::WeekUsagesCountExceeded::kSuffix));
  ASSERT_TRUE(mode_keys.count(tr::WeekUsagesDurationExceeded::kSuffix));
  ASSERT_TRUE(mode_keys.count(tr::UsagesLimitExceeded::kSuffix));
  ASSERT_TRUE(mode_keys.count(tr::ActivePanelTitle::kSuffix));
  ASSERT_TRUE(mode_keys.count(tr::ActivePanelSubtitle::kSuffix));
  ASSERT_TRUE(mode_keys.count(tr::FinishDialogTitle::kSuffix));
  ASSERT_TRUE(mode_keys.count(tr::FinishDialogBody::kSuffix));
}

TEST(Translations, SubmodeKeysAutoregistrationTest) {
  const auto& submode_keys = components::Translations::GetSubmodeKeys();
  ASSERT_FALSE(submode_keys.empty());
  ASSERT_TRUE(submode_keys.count(tr::Name::kSuffix));
  ASSERT_TRUE(submode_keys.count(tr::SubName::kSuffix));
}

TEST(Translations, KeysAutoregistrationTest) {
  const auto& keys = components::Translations::GetKeys();
  ASSERT_FALSE(keys.empty());
  ASSERT_TRUE(keys.count(tr::PointTooClose::kSuffix));
  ASSERT_TRUE(keys.count(tr::PointTooDistant::kSuffix));
  ASSERT_TRUE(keys.count(tr::ModeBlockedByWorkMode::kSuffix));
  ASSERT_TRUE(keys.count(tr::ModeDurationExceedsUsageLimit::kSuffix));
}

TEST(Translations, ModeBonusKeysAutoregistrationTest) {
  const auto& bonus_keys = components::Translations::GetModeBonusKeys();
  ASSERT_FALSE(bonus_keys.empty());
  ASSERT_TRUE(bonus_keys.count(tr::BonusHeadlineTitle::kSuffix));
  ASSERT_TRUE(bonus_keys.count(tr::BonusHeadlineSubtitle::kSuffix));
  ASSERT_TRUE(bonus_keys.count(tr::BonusSublineTitle::kSuffix));
  ASSERT_TRUE(bonus_keys.count(tr::BonusSublineSubtitle::kSuffix));
}

TEST(Translations, DisplayRuleKeysAutoregistrationTest) {
  const auto& dr_keys = components::Translations::GetDisplayRuleKeys();
  ASSERT_FALSE(dr_keys.empty());
  ASSERT_TRUE(dr_keys.count(tr::DisplayRuleShortText::kSuffix));
  ASSERT_TRUE(dr_keys.count(tr::DisplayRuleText::kSuffix));
  ASSERT_TRUE(dr_keys.count(tr::DisplayRuleTitle::kSuffix));
}
