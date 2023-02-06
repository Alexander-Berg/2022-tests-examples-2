#include <userver/utest/utest.hpp>

#include <memory>

#include <userver/formats/json/value.hpp>
#include <userver/formats/json/value_builder.hpp>
#include <userver/formats/serialize/common_containers.hpp>
#include <userver/utils/datetime.hpp>

#include <accounting/journal_entries_reducer.hpp>
#include <common/types.hpp>
#include <models/journal.hpp>

namespace accounting = billing_time_events::accounting;
namespace models = billing_time_events::models;
namespace types = billing_time_events::types;

namespace {

formats::json::Value MakeIntervalJson() {
  ::formats::json::ValueBuilder builder{::formats::json::Type::kObject};
  builder["duration_min"] = "5";
  builder["rate_per_min"] = "10";
  return builder.ExtractValue();
}

formats::json::Value MakeDetailsJson(
    std::vector<::formats::json::Value>&& intervals) {
  ::formats::json::ValueBuilder builder{::formats::json::Type::kObject};
  builder["intervals"] = std::move(intervals);
  return builder.ExtractValue();
}
}  // namespace

TEST(JournalEntriesReducerTest, NoEntries) {
  accounting::JournalEntriesReducer reducer{};
  auto res = reducer.Reduce();
  ASSERT_EQ(res.size(), 0);
}

TEST(JournalEntriesReducerTest, AllDifferent) {
  accounting::JournalEntriesReducer reducer{};
  std::vector<models::JournalEntry> entries{
      {types::Numeric{6},
       "USD",
       "time/free",
       ::utils::datetime::Stringtime("2020-08-02T01:00:00Z", "UTC"),
       {}},
      {types::Numeric{28},
       "USD",
       "unfit/time/free",
       ::utils::datetime::Stringtime("2020-08-02T01:00:00Z", "UTC"),
       {}},
      {types::Numeric{496},
       "EUR",
       "time/free",
       ::utils::datetime::Stringtime("2020-08-02T01:00:00Z", "UTC"),
       {}}};
  reducer.Add(std::move(entries));
  auto res = reducer.Reduce();
  ASSERT_EQ(res.size(), 3);
}

TEST(JournalEntriesReducerTest, Reduce) {
  accounting::JournalEntriesReducer reducer{};
  std::vector<models::JournalEntry> entries{
      {types::Numeric{6},
       "USD",
       "time/free",
       ::utils::datetime::Stringtime("2020-08-02T01:00:00Z", "UTC"),
       {}},
      {types::Numeric{28},
       "USD",
       "unfit/time/free",
       ::utils::datetime::Stringtime("2020-08-03T01:00:00Z", "UTC"),
       {}},
      {types::Numeric{496},
       "USD",
       "time/free",
       ::utils::datetime::Stringtime("2020-08-04T01:00:00Z", "UTC"),
       {}}};
  reducer.Add(std::move(entries));
  auto res = reducer.Reduce();
  ASSERT_EQ(res.size(), 2);
  EXPECT_EQ(res[0].sub_account, "time/free");
  EXPECT_EQ(res[0].amount, types::Numeric{502});
  EXPECT_EQ(res[0].timestamp,
            ::utils::datetime::Stringtime("2020-08-02T01:00:00Z", "UTC"));
  EXPECT_EQ(res[1].sub_account, "unfit/time/free");
  EXPECT_EQ(res[1].amount, types::Numeric{28});
  EXPECT_EQ(res[1].timestamp,
            ::utils::datetime::Stringtime("2020-08-03T01:00:00Z", "UTC"));
}

TEST(JournalEntriesReducerTest, ReduceWithEventAtSeparator) {
  accounting::JournalEntriesReducer reducer{};
  std::vector<models::JournalEntry> entries{
      {types::Numeric{6},
       "USD",
       "time/free",
       ::utils::datetime::Stringtime("2020-08-02T01:00:00Z", "UTC"),
       {}},
      {types::Numeric{28},
       "USD",
       "unfit/time/free",
       ::utils::datetime::Stringtime("2020-08-03T01:00:00Z", "UTC"),
       {}},
      {types::Numeric{496},
       "USD",
       "time/free",
       ::utils::datetime::Stringtime("2020-08-04T01:00:00Z", "UTC"),
       {}}};
  reducer.SplitAt(::utils::datetime::Stringtime("2020-08-03T01:00:00Z", "UTC"));
  reducer.Add(std::move(entries));
  auto res = reducer.Reduce();
  ASSERT_EQ(res.size(), 3);
  EXPECT_EQ(res[0].sub_account, "time/free");
  EXPECT_EQ(res[0].amount, types::Numeric{6});
  EXPECT_EQ(res[0].timestamp,
            ::utils::datetime::Stringtime("2020-08-02T01:00:00Z", "UTC"));

  EXPECT_EQ(res[1].sub_account, "time/free");
  EXPECT_EQ(res[1].amount, types::Numeric{496});
  EXPECT_EQ(res[1].timestamp,
            ::utils::datetime::Stringtime("2020-08-04T01:00:00Z", "UTC"));

  EXPECT_EQ(res[2].sub_account, "unfit/time/free");
  EXPECT_EQ(res[2].amount, types::Numeric{28});
  EXPECT_EQ(res[2].timestamp,
            ::utils::datetime::Stringtime("2020-08-03T01:00:00Z", "UTC"));
}

TEST(JournalEntriesReducerTest, NotBeReducedIfSeparatorEqualTimestamp) {
  accounting::JournalEntriesReducer reducer{};
  std::vector<models::JournalEntry> entries{
      {types::Numeric{6},
       "USD",
       "time/free",
       ::utils::datetime::Stringtime("2020-08-02T00:59:00Z", "UTC"),
       {}},
      {types::Numeric{28},
       "USD",
       "unfit/time/free",
       ::utils::datetime::Stringtime("2020-08-02T01:00:00Z", "UTC"),
       {}}};
  reducer.SplitAt(::utils::datetime::Stringtime("2020-08-02T01:00:00Z", "UTC"));
  reducer.Add(std::move(entries));
  auto reduced_entries = reducer.Reduce();
  ASSERT_EQ(reduced_entries.size(), 2);
}

TEST(JournalEntriesReducerTest, DetailsCombined) {
  using namespace billing_time_events;
  accounting::JournalEntriesReducer reducer{};
  std::vector<models::JournalEntry> entries{
      {types::Numeric{6},
       "USD",
       "guarantee",
       ::utils::datetime::Stringtime("2020-08-02T00:59:00Z", "UTC"),
       {},
       MakeDetailsJson({MakeIntervalJson()})},
      {types::Numeric{28},
       "USD",
       "guarantee",
       ::utils::datetime::Stringtime("2020-08-02T01:00:00Z", "UTC"),
       {},
       MakeDetailsJson({MakeIntervalJson()})}};
  reducer.Add(std::move(entries));
  auto reduced_entries = reducer.Reduce();
  ASSERT_EQ(reduced_entries.size(), 1);
  auto actual_details = reduced_entries[0].details;
  auto expected_details =
      MakeDetailsJson({MakeIntervalJson(), MakeIntervalJson()});
  EXPECT_EQ(actual_details, expected_details);
}
